"""
Data Preparation Module.

This script is responsible for pre-processing the raw monolithic dataset.
It handles cleaning, type conversation, and splits the large CSV file into
smaller, managable chunks (partitioned by month). This simulates a real-world
scenario where data arrives periodically (e.g., monthly logs).
"""

import pandas as pd
from pathlib import Path
from src.config import config


class DataPreparaion:
    """
    Handles loading, cleaning, and partitioning of the bike dataset.
    """

    def __init__(self, input_path: str, output_dir: str):
        """
        Initialize the DataPreparation pipeline.

        Args:
            input_path (str): File path to the large input CSV.
            output_path (str): Directory where split files will be saved.
        """
        self.input_path = input_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Execute the data processing logics:
        1. Loads the dataset.
        2. Cleans the column names.
        3. Remomved invalud rows.
        4. Groups data by months and saves the separate CSV files.
        """
        print(f"--- Starting Data Preparation ---")

        print(f"Loading {self.input_path}...")
        df = pd.read_csv(self.input_path, low_memory=False)

        df.columns = df.columns.str.strip()
        print(f"Columns found: {list(df.columns)}")

        print("Converting dates & cleaning data...")
        df["departure"] = pd.to_datetime(df["departure"], errors="coerce")
        df["return"] = pd.to_datetime(df["return"], errors="coerce")

        df = df.dropna(subset=["departure", "return"])

        df["month_key"] = df["departure"].dt.to_period("M")

        print("Splitting into monthly files...")
        for period, group in df.groupby("month_key"):
            file_name = f"{period}.csv"
            file_path = self.output_dir / file_name

            output_group = group.drop(columns=["month_key"])

            output_group.to_csv(file_path, index=None)
            print(f" Created: {file_name} ({len(output_group)} rows)")

        print(f"--- Data preparation Finished! Files are in {self.output_dir} ---")


if __name__ == "__main__":
    prep = DataPreparaion(config.input_file, config.output_dir)
    prep.run()
