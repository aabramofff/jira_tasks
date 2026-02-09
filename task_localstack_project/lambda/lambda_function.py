"""
AWS Lambda Function: Raw Data Ingestion.

This function serves as a "Fast path" in the architecture.
Is is triggered via SNS whenever a new CSV file is uploaded to the S3 bucket.

Workflow:
1. Receives an SNS Event containing an S3 Event message.
2. Downloads the uploaded CSV file from S3 into memory.
3. Parse the CSV content.
4. Writes the raw records into a DynamoDB table for low-latency access.
"""

import json
import boto3
import csv
import io
import os
import uuid


ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "http://localstack:4566")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_RAW", "BikeTripsRaw")


def handler(event, context):
    """
    Main Lambda entry point.

    Args:
        event (dict): The JSON dictionary containing event data (SNS wrpped S3 event).
        context (object): Runtime information (request ID, log stream, etc.).
    Returns:
        dict: A response object with status code & body.
    """
    print("🚀 Event received!")

    s3 = boto3.client("s3", endpoint_url=ENDPOINT_URL)
    dynamodb = boto3.resource("dynamodb", endpoint_url=ENDPOINT_URL)
    table = dynamodb.Table(TABLE_NAME)

    try:
        if "Records" not in event:
            print("⚠️ Unknown event structure (No 'Records' in top level)")
            return

        sns_record = event["Records"][0]
        if "Sns" not in sns_record:
            print("⚠️ Not an SNS event")
            return

        sns_message_raw = sns_record["Sns"]["Message"]
        s3_event = json.loads(sns_message_raw)

        if "Event" in s3_event and s3_event["Event"] == "s3:TestEvent":
            print("ℹ️ Received s3:TestEvent. Configuration works! Ignoring...")
            return {"statusCode": 200, "body": "Test Event Ignored"}

        if "Records" not in s3_event:
            print(f"⚠️ No 'Records' key in S3 event. Content: {json.dumps(s3_event)}")
            return

        bucket_name = s3_event["Records"][0]["s3"]["bucket"]["name"]
        file_key = s3_event["Records"][0]["s3"]["object"]["key"]

        print(f"📥 Processing real file: s3://{bucket_name}/{file_key}")

        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content = response["Body"].read().decode("utf-8")

        csv_reader = csv.DictReader(io.StringIO(content))

        count = 0
        with table.batch_writer() as batch:
            for row in csv_reader:
                if count >= 100:
                    break

                item = {
                    "trip_id": str(uuid.uuid4()),
                    "departure_time": row.get("departure") or row.get("Departure"),
                    "station_name": row.get("departure_name")
                    or row.get("Departure station"),
                    "distance": row.get("distance (m)") or row.get("Distance (m)", "0"),
                    "source_file": file_key,
                }

                if not item["trip_id"]:
                    continue

                batch.put_item(Item=item)
                count += 1

        print(f"✅ SUCCESS: Wrote {count} records to DynamoDB")
        return {"statusCode": 200, "body": f"Processed {count}"}

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise e
