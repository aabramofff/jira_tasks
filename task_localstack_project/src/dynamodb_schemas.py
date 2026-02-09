"""
DynamoDB Schema Definitions.

This module contains the schema definitions for the DynamoDB tables used in the project.
It defines the Primary Keys (Partition Key & Sort Key), Attribute Types, and
Provisioned Throughput settings required by boto3 to create tables.
"""


class TableSchema:
    """
    Static container for DynamoDB table configurations.
    """

    @staticmethod
    def get_bike_trips_raw_schema():
        """
        Schema for the 'Fast Path' raw data table.

        Design:
        - Partition Key: trip_id (Unique UUID for every trip).
        - Purpose: Fast write access for individual records processed by Lambda.
        """
        return {
            "TableName": "BikeTripsRaw",
            "KeySchema": [{"AttributeName": "trip_id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "trip_id", "AttributeType": "S"}
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        }

    @staticmethod
    def get_bike_metrics_daily_schema():
        """
        Schema for Daily Aggregated Metrics.

        Design:
        - Partition Key: date (e.g., "2020-05-01").
        - Sort Key: metric_type (e.g., "avg_distance", "total_trips").
        - Purpose: Allow querying specific metrics for a specific day efficiently.
        """
        return {
            "TableName": "BikeMetricsDaily",
            "KeySchema": [
                {"AttributeName": "date", "KeyType": "HASH"},
                {"AttributeName": "metric_type", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "date", "AttributeType": "S"},
                {"AttributeName": "metric_type", "AttributeType": "S"},
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        }

    @staticmethod
    def get_bike_metrics_monthly_schema():
        """
        Schema for Monthly Aggregated Metrics.

        Design:
        - Partition Key: month (e.g., "2020-05).
        - Sort Key: metric_type.
        - Purpose: Aggregated views for longer time horizons.
        """
        return {
            "TableName": "BikeMetricsMonthly",
            "KeySchema": [
                {"AttributeName": "month", "KeyType": "HASH"},
                {"AttributeName": "metric_type", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "month", "AttributeType": "S"},
                {"AttributeName": "metric_type", "AttributeType": "S"},
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        }
