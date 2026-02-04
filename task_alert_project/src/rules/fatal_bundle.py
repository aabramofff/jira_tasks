from src.rules.base import BaseRule
from src.models import LogEntry
from src.logger import alert_logger


class FatalBundleRule(BaseRule):
    """
    Alerting rule for Rule 2.2: More than 10 fatal errors in less than one hour
    for a specific bundle_id.
    """

    LIMIT = 10
    WINDOW = 3600

    def check(self, log: LogEntry):
        """
        Evalueates the log entry againstt the bundle-specific fatal error rule.

        Args:
            log (LogEntry): The validated log entry to check.
        """
        if not log.is_fatal and log.bundle_id:
            return

        key = f"alert:bundle:{log.bundle_id}"
        count = self.check_threshold(key, log.timestamp, self.WINDOW, self.LIMIT)

        if count > self.LIMIT:
            msg = (
                f"[RULE 2.2] Bundle {log.bundle_id} issue! {count} errors in last hour."
            )
            print(msg)
            alert_logger.error(msg)
