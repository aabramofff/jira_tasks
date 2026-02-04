import pandas as pd
import json
import time
from src.config import Config
from src.redis_client import get_redis


def load_data():
    """
    Reads log data from a CSV file in chunks and pushes it to a Redis queue.

    This function acts as a Data Producer. It uses Pandas 'chunksize' to
    handle large datasets efficiently by keeping memory usage low.
    Each record is converted to a JSON string and sent to Redis using
    pipelines for optimised network performance.
    """
    r = get_redis()
    print(f"📂 Loading data from {Config.CSV_PATH}...", flush=True)

    try:
        chunks = pd.read_csv(
            Config.CSV_PATH,
            skiprows=1,
            header=None,
            names=Config.COLUMNS,
            chunksize=Config.CHUNK_SIZE,
        )

        total = 0
        chunk_count = 0

        for chunk in chunks:
            chunk_count += 1
            if chunk.empty:
                continue

            records = chunk.to_dict(orient="records")

            pipe = r.pipeline()
            for record in records:
                pipe.lpush(Config.LOG_QUEUE, json.dumps(record))
            pipe.execute()

            total += len(records)
            print(
                f"--> Chunk {chunk_count}: Pushed {len(records)} logs (Total: {total})",
                flush=True,
            )

            time.sleep(0.5)

        if total == 0:
            print(
                "⚠️ WARNING: File was processed but 0 records were found. Check if CSV is empty.",
                flush=True,
            )
        else:
            print("✅ Data loading finished!", flush=True)

    except FileNotFoundError:
        print(
            "❌ ERROR: File not found. Please check data/alert_project_data.csv",
            flush=True,
        )
    except pd.errors.EmptyDataError:
        print("❌ ERROR: The CSV file is completely empty.", flush=True)
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}", flush=True)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    load_data()
