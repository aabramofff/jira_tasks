"""
Infrastructure Initialisation Script for LocalStack.

This script acts as "Infrastructure as Code" (IaC) for the local development environment.
It sets up the necessary AWS resources in LocalStack to mimic a production environment.

Resources created:
1. S3 Bucket: Acts as the Data Lake for raw files.
2. SNS Topic: Pub/Sub messaging system to decouple S3 uploads from processing logic.
3. DynamoDB Tables: NoSQL storage for processed data.
4. Lambda Function: Serverless compute to process incoming data.
5. Event Triggers: Configures S3 to send events to SNS, and SNS to trigger Lambda.
"""

import sys
import boto3
import zipfile
import io
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))


from src.config import config
from src.dynamodb_schemas import TableSchema


def get_boto_client(service):
    """
    Factory function to create a boto3 client configured for LocalStack.

    Args:
        service (str): The name of the AWS service (e.g., 's3', 'dynamodb').

    Returns:
        boto3.client: Configured AWS client.
    """
    return boto3.client(
        service,
        endpoint_url=config.aws_endpoint_url,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_region,
    )


def create_lambda_package():
    """
    Compress the Lambda function code into a ZIP archive.

    AWS Lambda (and LocalStack) requires code to be uploaded as a deployment package (ZIP).
    This function reads 'lambda_function.py' and zips in in-memory.

    Returns:
        bytes: Binary content of the zip file.
    """
    lambda_path = Path("lambda/lambda_function.py")
    if not lambda_path.exists():
        raise FileNotFoundError(f"Lambda file not found at {lambda_path}")

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(lambda_path, "lambda_function.py")
    buffer.seek(0)
    return buffer.read()


def main():
    print("--- Initializing LocalStack Infrastructure ---")

    # S3
    s3 = get_boto_client("s3")
    try:
        s3.create_bucket(Bucket=config.s3_bucket_name)
        print(f"✅ S3 Bucket created: {config.s3_bucket_name}")
    except Exception as e:
        print(f"❌ S3 Bucket note: {e}")

    # SNS
    sns = get_boto_client("sns")
    topic_res = sns.create_topic(Name=config.sns_topic_name)
    topic_arn = topic_res["TopicArn"]
    print(f"✅ SNS Topic created: {topic_arn}")

    # DynamoDB
    db = get_boto_client("dynamodb")
    tables = [
        TableSchema.get_bike_trips_raw_schema(),
        TableSchema.get_bike_metrics_daily_schema(),
        TableSchema.get_bike_metrics_monthly_schema(),
    ]

    for table in tables:
        try:
            db.create_table(**table)
            print(f"✅ DynamoDB Table created: {table['TableName']}")
        except Exception as e:
            if "ResourceInUseException" in str(e):
                print(f"⚠️ DynamoDB Table already exists: {table['TableName']}")
            else:
                print(f"❌ DynamoDB Error: {e}")

    # Lambda
    lam = get_boto_client("lambda")
    func_name = "bike-data-processor"

    try:
        lam.create_function(
            FunctionName=func_name,
            Runtime="python3.9",
            Role="arn:aws:iam::000000000000:role/lambda-role",  # Fake role for LocalStack
            Handler="lambda_function.handler",
            Code={"ZipFile": create_lambda_package()},
            Environment={
                "Variables": {
                    "AWS_ENDPOINT_URL": "http://localstack:4566",  # Внутри контейнера лямбды свой адрес
                    "DYNAMODB_TABLE_RAW": "BikeTripsRaw",
                    "DYNAMODB_TABLE_DAILY": "BikeMetricsDaily",
                }
            },
        )
        print(f"✅ Lambda created: {func_name}")
    except Exception as e:
        if "ResourceConflictException" in str(e):
            print(f"⚠️ Lambda already exists: {func_name}")
        else:
            print(f"❌ Lambda error: {e}")
            return

    # Connect S3 -> SNS -> Lambda
    func_arn = lam.get_function(FunctionName=func_name)["Configuration"]["FunctionArn"]
    sns.subscribe(TopicArn=topic_arn, Protocol="lambda", Endpoint=func_arn)
    print(f"✅ Lambda subscribed to SNS")

    # S3 Trigger on SNS
    s3.put_bucket_notification_configuration(
        Bucket=config.s3_bucket_name,
        NotificationConfiguration={
            "TopicConfigurations": [
                {
                    "TopicArn": topic_arn,
                    "Events": ["s3:ObjectCreated:*"],
                    "Filter": {
                        "Key": {"FilterRules": [{"Name": "suffix", "Value": ".csv"}]}
                    },
                }
            ]
        },
    )
    print("✅ S3 Bucket configured")
    print("--- Infrastructure Ready! ---")


if __name__ == "__main__":
    main()
