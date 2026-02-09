"""
Spark Job: Helsinki City Bike Data Processor.

This script performs the ETL process on raw bike trip data.
It uses PySpark to calculate aggregated metrics (daily and monthly) from the input CSV files.

Usage:
    spark-submit data_processor.py --input <path_to_csv> --output <path_to_output_dir>
"""

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, round, to_date


def process_data(input_file, output_dir):
    """
    Reads raw bike data, applies transformations, calculates metrics, and saves results.

    Transformations:
    1. Standardizes column names,
    2. Converts timestamp strings to Date objects.
    3. Aggregates data by Day and Station.
    4. Aggregates data by Station (Monthly summary).

    Args:
        input_file (str): Path to the source CSV file (e.g., /data/raw/2020-05.csv)
        output_di (str): Path to the destination directory.
    """
    spark = SparkSession.builder.appName("HelsinkiBikeMetrics").getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    print(f"--- Processing file: {input_file} ---")

    df = (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .csv(input_file)
    )

    df = df.withColumn("date", to_date(col("departure")))

    df = df.withColumnRenamed("distance (m)", "distance_m").withColumnRenamed(
        "duration (sec.)", "duration_sec"
    )

    daily_metrics = df.groupBy("date", "departure_name").agg(
        count("*").alias("trip_count"),
        round(avg("distance_m"), 2).alias("avg_distance_m"),
        round(avg("duration_sec"), 2).alias("avg_duration_sec"),
    )

    monthly_metrics = df.groupBy("departure_name").agg(
        count("*").alias("total_trips"),
        round(avg("distance_m"), 2).alias("avg_distance_m"),
        round(avg("duration_sec"), 2).alias("avg_duration_sec"),
    )

    daily_output = f"{output_dir}/daily_stats"
    monthly_output = f"{output_dir}/monthly_stats"

    print(f"Saving daily metrics to {daily_output}...")
    daily_metrics.write.mode("overwrite").option("header", "true").csv(daily_output)

    print(f"Saving monthly metrics to {daily_output}...")
    monthly_metrics.write.mode("overwrite").option("header", "true").csv(monthly_output)

    print("--- ✅ Processing Complete ---")

    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output directory")
    args = parser.parse_args()

    process_data(args.input, args.output)
