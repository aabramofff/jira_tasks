"""
Airflow DAG: Data Ingestion and Processing Pipeline.

This DAG performs TWO main steps:
1. Ingest raw CSV data from the local filesystem into the S3 Data Lake (LocalStack).
2. Triggers & Apache Spark job via REST API to process the uploaded data.

Workflow:
    [Local CSVs] -> (upload_to_s3) -> [S3 Bucket] -> (trigger_spark) -> [Spark Cluster]
"""

import boto3
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator


AWS_ENDPOINT_URL = "http://localstack:4566"
AWS_ACCESS_KEY = "test"
AWS_SECRET_KEY = "test"
BUCKET_NAME = "bike-data-raw"
SOURCE_DIR = "/opt/airflow/data/raw"


SPARK_MASTER_URL = "http://spark-master:6066"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


def upload_files_to_s3(**context):
    """
    Uploads all csv files from the local source directory to the S3 bucket.

    This function:
    1. Connects to LocalStack S3.
    2. Scans the source directory for .csv files.
    3. Uploads each file.
    4. Returns a list of uploaded filenames to be used by the next task (XCom).

    Args:
        **context: Airflow context dictionary.

    Returns:
        list: A list of filenames that were successfully uploaded.
    """
    print("--- Starting S3 Upload ---")

    s3_client = boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="us-east-1",
    )

    source_path = Path(SOURCE_DIR)
    if not source_path.exists():
        print(f"❌ Directory {SOURCE_DIR} not found!")
        return []

    uploaded_files = []
    files = list(source_path.glob("*.csv"))
    print(f"Found {len(files)} CSV files in {SOURCE_DIR}")

    for file_path in files:
        file_name = file_path.name
        s3_key = file_name

        print(f"Uploading {file_name} to s3://{BUCKET_NAME}/{s3_key}...")

        try:
            s3_client.upload_file(str(file_path), BUCKET_NAME, s3_key)
            uploaded_files.append(file_name)
            print(f"✅ Success: {file_name}")
        except Exception as e:
            print(f"❌ Failed to upload {file_name}: {e}")
            raise e

    print("--- Upload complete ---")

    return uploaded_files


def trigger_spark_job(**context):
    """
    Submits a Spark Job to the standalone cluster via REST API.

    This function:
    1. Retrieves the list of uploaded files from the previous task (via XCom)
    2. Constructs a JSON payload compatible with Spark's Hidden REST API.
    3. Sends a POST request to Spark Master to start the processing.

    Args:
        **context: Airflow context dictionary.
    """
    ti = context["ti"]
    uploaded_files = ti.xcom_pull(task_ids="upload_csvs")

    if not uploaded_files:
        print("⚠️ No files uploaded, skipping Spark job.")
        return

    target_file = uploaded_files[0]
    print(f"Triggering Spark processing for: {target_file}")

    spark_input_path = f"/opt/spark/data/raw/{target_file}"
    output_folder = target_file.replace(".csv", "")
    spark_output_path = f"/opt/spark/data/processed/{output_folder}"

    payload = {
        "action": "CreateSubmissionRequest",
        "appArgs": ["--input", spark_input_path, "--output", spark_output_path],
        "appResource": "file://opt/spark/jobs/data_processor.py",
        "clientSparkVersion": "3.5.1",
        "mainClass": "org.apache.spark.deploy.PythonRunner",
        "environmentVariables": {"SPARK_ENV_LOADED": "1"},
        "sparkProperties": {
            "spark.master": "spark://spark-master:7077",
            "spark.submit.deployMode": "cluster",
            "spark.app.name": "AirflowTriggeredHelsinki",
        },
    }

    url = f"{SPARK_MASTER_URL}/v1/submissions/create"
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        print(f"Spark Response: {json.dumps(response_data, indent=2)}")

        if response_data.get("success"):
            print(
                f"✅ Spark Job Started! Submission ID: {response_data.get('submissionId')}"
            )
        else:
            raise Exception(
                f"❌ Spark Submission Failed: {response_data.get('message')}"
            )
    except Exception as e:
        print(f"❌ Error talking to Spark Master: {e}")
        raise e


with DAG(
    "1_upload_raw_data_to_s3",
    default_args=default_args,
    description="Uploads raw CSVs to LovalStack S3",
    schedule_interval=None,
    catchup=False,
    tags=["helsinki-bikes", "s3", "S3"],
) as dag:

    upload_task = PythonOperator(
        task_id="upload_csvs", python_callable=upload_files_to_s3
    )

    spark_task = PythonOperator(
        task_id="process_with_spark", python_callable=trigger_spark_job
    )

    upload_task >> spark_task
