from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime

SNOWFLAKE_CONN_ID = "snowflake_conn"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    "02_airline_main_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["airline", "main_etl"],
) as dag:

    task_run_transformation = SnowflakeOperator(
        task_id="run_transformation_procedure",
        snowflake_conn_id=SNOWFLAKE_CONN_ID,
        sql="""
            USE ROLE AIRFLOW_ROLE;
            USE WAREHOUSE AIRLINE_WH;
            USE DATABASE AIRLINE_DWH;
            CALL AIRLINE_DWH.INTEGRATION.SP_TRANSFORM_AIRLINE_DATA();
        """,
        autocommit=True,
    )

    task_run_transformation
