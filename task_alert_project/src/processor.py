import json
import sys
from src.redis_client import get_redis
from src.config import Config
from src.models import LogEntry
from src.rules.fatal_global import FatalGlobalRule
from src.rules.fatal_bundle import FatalBundleRule


def main():
    """
    Main worker loop that consumes logs from Redis and evaluates altering rules.

    This function initializes the rule engine and enters an infinite loop,
    waiting for new log entries to appear in the Redis queue.
    """
    r = get_redis()
    print("✅ Processor started. Waiting for logs...")

    rules = [FatalGlobalRule(r), FatalBundleRule(r)]

    processed_count = 0

    while True:
        item = r.brpop(Config.LOG_QUEUE, timeout=5)

        if item:
            _, raw_data = item

            try:
                data = json.loads(raw_data)
                log = LogEntry(**data)

                for rule in rules:
                    rule.check(log)

                processed_count += 1
                if processed_count % 1000 == 0:
                    sys.stdout.write(f"\rProcessed: {processed_count}")
                    sys.stdout.flush()

            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
