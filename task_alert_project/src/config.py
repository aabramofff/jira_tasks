import os


class Config:
    """
    Central configuration class for the log analysis system.
    Stores environment variables, database connection parameters,
    and data schema defenitions.
    """

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = 6379
    LOG_QUEUE = "logs_queue"
    CSV_PATH = "/app/data/alert_project_data.csv"
    CHUNK_SIZE = 50000

    COLUMNS = [
        "error_code",
        "error_message",
        "severity",
        "log_location",
        "mode",
        "model",
        "graphics",
        "session_id",
        "sdkv",
        "test_mode",
        "flow_id",
        "flow_type",
        "sdk_date",
        "publisher_id",
        "game_id",
        "bundle_id",
        "appv",
        "language",
        "os",
        "adv_id",
        "gdpr",
        "ccpa",
        "country_code",
        "date",
    ]
