import os

from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.python import PythonOperator
from datetime import datetime

SNOWFLAKE_CONN_ID = "snowflake_conn"
LOCAL_FILE_PATH = "/opt/airflow/data_in/airline_dataset.csv"
STAGE_NAME = "AIRLINE_DWH.RAW.airline_stage"
TABLE_NAME = "AIRLINE_DWH.RAW.AIRLINE_RAW_DATA"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
}


def upload_to_snowflake_stage(local_path, stage_name, snowflake_conn_id):
    """Loading file into internal Stage Snowflake"""
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File {local_path} doesn't exist in container!")

    hook = SnowflakeHook(snowflake_conn_id=snowflake_conn_id)
    put_query = f"PUT 'file://{local_path}' @{stage_name} OVERWRITE = TRUE;"
    hook.run(put_query)
    print(f"File {local_path} file successfuly loaded into @{stage_name}")


with DAG(
    "01_airline_ingestion_raw",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["airline", "ingestion"],
) as dag:

    task_upload_to_stage = PythonOperator(
        task_id="upload_to_stage",
        python_callable=upload_to_snowflake_stage,
        op_kwargs={
            "local_path": LOCAL_FILE_PATH,
            "stage_name": STAGE_NAME,
            "snowflake_conn_id": SNOWFLAKE_CONN_ID,
        },
    )

    task_copy_into_raw = SnowflakeOperator(
        task_id="copy_into_raw",
        snowflake_conn_id=SNOWFLAKE_CONN_ID,
        sql=f"""
            TRUNCATE TABLE {TABLE_NAME};
            COPY INTO {TABLE_NAME}
            FROM @{STAGE_NAME}
            FILE_FORMAT = (FORMAT_NAME = 'AIRLINE_DWH.RAW.csv_format')
            ON_ERROR = 'CONTINUE';
        """,
    )

    task_upload_to_stage >> task_copy_into_raw
