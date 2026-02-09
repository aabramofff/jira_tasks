"""
Application Configuration Module.

This module manages the configuration settings for the project.
It uses the python-dotenv library to load sensetive credentials and settings
from a .env file (if present), falling back to default values suitable for
local development with LocalStack.
"""

import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    """
    Central configuration class.
    Attributes are populated from environment variables or defaults.
    """

    # AWS / LocalStack
    aws_endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "test")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    # App Settings
    input_file = "./data/helsinki_city_bikes.csv"
    output_dir = "./data/raw"
    s3_bucket_name = os.getenv("S3_BUCKET_NAME", "bike-data-raw")
    sns_topic_name = os.getenv("SNS_TOPIC_NAME", "file-upload-topic")


config = Config()
