import pandas as pd
import os
import re


from pendulum import datetime
from airflow.models.dag import DAG
from airflow.utils.task_group import TaskGroup
from airflow.decorators import task
from airflow.providers.standard.sensors.filesystem import FileSensor
from airflow.providers.standard.operators.python import PythonOperator
from airflow.datasets import Dataset


PROCESSED_DATA_DATASET = Dataset("file://airflow/processed_data_ready")
INTERNAL_DATA_PATH = "/opt/airflow/data_in/tiktok_google_play_reviews.csv"
PROCESSED_DATA_PATH = "/opt/airflow/data_in/processed_data.csv"
TEMP_DIR = "/opt/airflow/data_in/temp"


def get_temp_path(filename):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    return os.path.join(TEMP_DIR, filename)


@task.branch(task_id="check_file_empty")
def is_empty_file(filepath: str):
    try:
        df_head = pd.read_csv(filepath, nrows=1)

        if df_head.empty:
            print("Файл с данными пуст!")
            return "file_empty_log"

        print(f"Прочитано строк: {len(df_head)}. Начинается обработка...")
        return "data_processing_group.read_data_task"

    except Exception as e:
        print("Ошибка при чтении файла:\n", e)
        return "file_empty_log"


@task(task_id="read_data_task")
def read_data(filepath: str):
    df = pd.read_csv(filepath)
    print(f"Прочитано строк: {len(df)}")

    output_path = get_temp_path("step1_read.csv")
    df.to_csv(output_path, index=False)
    return output_path


@task(task_id="replace_null_task")
def replace_null(input_path: str):    
    df = pd.read_csv(input_path)

    df = df.fillna("-")

    output_path = get_temp_path("step2_nulls.csv")
    df.to_csv(output_path, index=False)
    print('NULL-значения в заменены на "-".')
    return output_path


@task(task_id="sort_data_task")
def sort_data(input_path: str):
    df = pd.read_csv(input_path)
    
    if 'at' in df.columns:
        df['at'] = pd.to_datetime(df['at'], errors='coerce')
        
        df = df.sort_values(by='at', ascending=False)
        print('Данные отсортированы по "at" (по убыванию)')
    else:
        print('Столбец "at" не найден. Сортировка не выполняется!')
    
    output_path = get_temp_path("step3_sorted.csv")
    df.to_csv(output_path, index=False)
    return output_path


@task(task_id="clean_content_task")
def clean_content(input_path: str):
    df = pd.read_csv(input_path)
    
    if 'content' in df.columns:
        df['content'] = df['content'].astype(str).apply(lambda x: re.sub(r'[^\w\s\.,!\?]', '', x))
        print('Столбец "content" успешно очищен!')
    else:
        print('Столбец "content" не найден. Очистка не выполняется!')
        
    output_path = get_temp_path("step4_cleaned.csv")
    df.to_csv(output_path, index=False)
    return output_path


@task(task_id="save_to_csv_file_task")
def save_to_csv_file(input_path: str, final_output_path: str):
    if os.path.exists(input_path):
        os.rename(input_path, final_output_path)
        print("Обработанные данные сохранены!\nПолный путь:", final_output_path)
    else:
        raise FileNotFoundError(f"Финальный файл не найден: {input_path}")
    

@task(task_id="publish_data_task", outlets=[PROCESSED_DATA_DATASET])
def publish_data():
    print("Данные сохранены. Dataset опубликован для запуска загрузчика.")


with DAG(
    dag_id="etl_dag",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["sensors", "data", "processing", "etl"]
) as dag:

    wait_for_data = FileSensor(
        task_id="wait_for_data",
        filepath=INTERNAL_DATA_PATH,
        fs_conn_id="fs_default",
        poke_interval=15,
        timeout=300
    )

    check_branch = is_empty_file(filepath=INTERNAL_DATA_PATH)
    file_empty_log = PythonOperator(
        task_id="file_empty_log",
        python_callable=lambda: print("Файл пуст! Логгирование факта и завершение работы...")
    )

    with TaskGroup("data_processing_group") as processing_group:
        
        read = read_data(filepath=INTERNAL_DATA_PATH)
        replace_nulls = replace_null(input_path=read)
        sort_data_flow = sort_data(input_path=replace_nulls)
        clean_content_flow = clean_content(input_path=sort_data_flow)
        
        read >> replace_nulls >> sort_data_flow >> clean_content_flow
    
    save_result = save_to_csv_file(
        input_path=clean_content_flow, 
        final_output_path=PROCESSED_DATA_PATH
    )

    wait_for_data >> check_branch
    check_branch >> [file_empty_log, processing_group]
    processing_group >> save_result
    save_result >> publish_data()
