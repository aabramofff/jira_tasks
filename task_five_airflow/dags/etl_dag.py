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

# The path to the input folder (where FileSensor will search for the file)
INPUT_DIR_PATH = "/opt/airflow/input"

# The path to the output folder (where all the results will be saved)
OUTPUT_DIR_PATH = "/opt/airflow/output"

# 3. The final path for the processed file
PROCESSED_DATA_PATH = os.path.join(OUTPUT_DIR_PATH, "processed_data.csv")

# The path for temporary files (saved inside the output folder)
TEMP_DIR = os.path.join(OUTPUT_DIR_PATH, "temp")

# This variable make us available to trigger mongo_loader_dag
PROCESSED_DATA_DATASET = Dataset("file://airflow/processed_data_ready")

def get_temp_path(filename):
    """ 
        A function that creates or updates a file
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    return os.path.join(TEMP_DIR, filename)


@task.branch(task_id="check_file_empty")
def is_empty_file(ti=None):
    """
        Checking for the contents of the data file
    """
    # extracting the path to the found file from XCom
    filepath = ti.xcom_pull(task_ids='get_filepath_and_push', key='return_value')

    if not filepath:
        print("Error: File path could not be retrieved from Pusher.")
        return "file_empty_log"

    try:
        df_head = pd.read_csv(filepath, nrows=1)

        if df_head.empty:
            print("File with data is empty!")
            return "file_empty_log"

        print(f"Lines read: {len(df_head)}. Processing begins...")
        return "data_processing_group.read_data_task"

    except Exception as e:
        print("Error ocurred while reading the file:\n", e)
        print(f"Path received: {filepath}")
        return "file_empty_log"
    
@task(task_id="get_filepath_and_push")
def get_filepath_and_push():
    """
        Finds the actual path to the file found by the sensor and pushes it to XCom.
    """
    import glob
    
    file_pattern = os.path.join(INPUT_DIR_PATH, "*.csv")
    
    # Searching for a file using Python's built-in 'glob' module
    found_files = glob.glob(file_pattern, recursive=False)
    
    if not found_files:
        raise FileNotFoundError(f"FileSensor succeeded, but glob failed to find file at: {file_pattern}")
    
    print(f"File path found and pushed to XCom: {found_files[0]}")
    return found_files[0]


@task(task_id="read_data_task")
def read_data(filepath: str):
    """
        Task that reads the data from initial data file
    """
    if not filepath:
        raise ValueError("Could not retrieve file path from FileSensor XCom.")

    df = pd.read_csv(filepath)
    print(f"Lines read: {len(df)}")

    output_path = get_temp_path("step1_read.csv")
    df.to_csv(output_path, index=False)
    return output_path


@task(task_id="replace_null_task")
def replace_null(input_path: str):
    """
        Task that replaces NaN values
    """    
    df = pd.read_csv(input_path)

    df = df.fillna("-")

    output_path = get_temp_path("step2_nulls.csv")
    df.to_csv(output_path, index=False)
    print('NULL-values replaced with "-".')
    return output_path


@task(task_id="sort_data_task")
def sort_data(input_path: str):
    """
        Task that sorts data with replaced NaN values
    """
    df = pd.read_csv(input_path)
    
    if 'at' in df.columns:
        df['at'] = pd.to_datetime(df['at'], errors='coerce')
        
        df = df.sort_values(by='at', ascending=False)
        print('The data is sorted by "at" (descending)')
    else:
        print('The "at" column was not found. Sorting is not performed!')
    
    output_path = get_temp_path("step3_sorted.csv")
    df.to_csv(output_path, index=False)
    return output_path


@task(task_id="clean_content_task")
def clean_content(input_path: str):
    """
        This task cleans "content" column
    """
    df = pd.read_csv(input_path)
    
    if 'content' in df.columns:
        df['content'] = df['content'].astype(str).apply(lambda x: re.sub(r'[^\w\s\.,!\?]', '', x))
        df['content'] = df['content'].str.strip() 
        df['content'] = df['content'].replace('', '-', regex=False)

        print('The "content" column has been successfully cleared!')
    else:
        print('The "content" column was not found. Cleaning is not performed!')
        
    output_path = get_temp_path("step4_cleaned.csv")
    df.to_csv(output_path, index=False)
    return output_path


@task(task_id="save_to_csv_file_task")
def save_to_csv_file(input_path: str, final_output_path: str):
    """
        Saves processed data into .csv file
    """
    if os.path.exists(input_path):
        os.rename(input_path, final_output_path)
        print("The processed data is saved!\nFull path:", final_output_path)
    else:
        raise FileNotFoundError(f"File not found: {input_path}")
    

@task(task_id="publish_data_task", outlets=[PROCESSED_DATA_DATASET])
def publish_data():
    """
        Success task's execution means that all dag ended uo successfuly
    """
    print("The data is saved. The Dataset is published to run the loader.")


# in this section, the dag is launched and all dependencies are registered.
with DAG(
    dag_id="etl_dag",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["sensors", "data", "processing", "etl"]
) as dag:

    wait_for_data = FileSensor(
        task_id="wait_for_data",
        filepath=os.path.join(INPUT_DIR_PATH, "*.csv"),
        fs_conn_id="fs_default",
        poke_interval=15,
        timeout=300
    )

    file_path_pusher = get_filepath_and_push()

    check_branch = is_empty_file()
    file_empty_log = PythonOperator(
        task_id="file_empty_log",
        python_callable=lambda: print("The file is empty! Logging the fact and shutting down the work...")
    )

    with TaskGroup("data_processing_group") as processing_group:
        
        read = read_data(filepath=file_path_pusher)
        replace_nulls = replace_null(input_path=read)
        sort_data_flow = sort_data(input_path=replace_nulls)
        clean_content_flow = clean_content(input_path=sort_data_flow)
        
        read >> replace_nulls >> sort_data_flow >> clean_content_flow
    
    save_result = save_to_csv_file(
        input_path=clean_content_flow, 
        final_output_path=PROCESSED_DATA_PATH
    )

    wait_for_data >> file_path_pusher
    file_path_pusher >> check_branch
    check_branch >> [file_empty_log, processing_group]
    processing_group >> save_result
    save_result >> publish_data()
