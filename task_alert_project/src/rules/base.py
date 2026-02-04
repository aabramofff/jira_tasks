from abc import ABC, abstractmethod
from src.models import LogEntry
import time


class BaseRule(ABC):
    """
    Abstract Base Class for all altering rules.

    Provdes a template for implementing specific log analysis logic
    and includes a shared method for sliding window calculations using Redis.
    """

    def __init__(self, redis_client):
        """
        Initializes the rule with a Redis client.

        Args:
            redis_client: An active Redis connection for state persistence.
        """
        self.redis = redis_client

    @abstractmethod
    def check(srlf, log: LogEntry):
        """
        Abstract method to be implemented by subclasses.
        Contains the specific logic to determine if a log entry triggers an alert.

        Args:
            log (LogEntry): The validated log object to analyze.
        """
        pass

    def check_threshold(
        self, key: str, timestamp: float, window: int, limit: int
    ) -> int:
        """
        Implements the Slidig Window algorightm using Redis Stored Sets (ZSET).

        This method performs three atomic operations:
        1. Removes entries outside the current time window.
        2. Adds the new event timestamp.
        3. Counts the total events remaining in the window.

        Args:
            key (str): Unique Redis key for this specific rule/context
            timestamp (float): The event time for the log entry.
            window (int): Size of the sliding window in seconds.
            limit (int): The threshold for triggering an alert.

        Returns:
            int: The current number of events within the sliding window.
        """
        pipe = self.redis.pipeline()
        min_score = timestamp - window
        pipe.zremrangebyscore(key, "-inf", min_score)

        unique_member = f"{timestamp}:{time.time_ns}"
        pipe.zadd(key, {unique_member: timestamp})

        pipe.zcard(key)

        _, _, count = pipe.execute()
        return count
