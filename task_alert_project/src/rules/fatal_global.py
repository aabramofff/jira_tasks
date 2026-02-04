from src.rules.base import BaseRule
from src.models import LogEntry
from src.logger import alert_logger


class FatalGlobalRule(BaseRule):
    """
    Alerting rule for Rule 2.1: More than 10 fatal errors in less than one minute
    across all bundles (global scope).
    """

    LIMIT = 10
    WINDOW = 60

    def check(self, log: LogEntry):
        """
        Evaluates the log entry against the global fatal error threshold.

        Args:
            log (LogEntry): The validated log entry to check.
        """
        if not log.is_fatal:
            return

        key = "alert:global:fatal"
        count = self.check_threshold(key, log.timestamp, self.WINDOW, self.LIMIT)

        if count > self.LIMIT:
            msg = f"[RULE 2.1] HIGH FATAL RATE! {count} errors in last minute."
            print(msg)
            alert_logger.error(msg)
