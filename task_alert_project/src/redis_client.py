import redis
from src.config import Config


pool = redis.ConnectionPool(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)


def get_redis():
    """
    Returns a Redis client instance from the global connection pool.

    The 'deecode_responses=True' argument ensures that Redis returns
    Python strings instead of raw bytes, simplifying data handling.

    Returns:
        redis.Redis: A ready-to-use Redis client.
    """
    return redis.Redis(connection_pool=pool, decode_responses=True)
