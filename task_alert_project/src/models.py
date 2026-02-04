from pydantic import BaseModel, Field, field_validator
from typing import Optional


class LogEntry(BaseModel):
    """
    Data model representing a single log entry from the mobile application.

    Provides atumated validation, type convertion & data clean ining using Pydantic
    """

    severity: str
    bundle_id: Optional[str] = ""
    timestamp: float = Field(alias="date")

    @field_validator("severity", pre=True)
    @classmethod
    def clean_severity(cls, v):
        """
        Cleans & normalizes the severity string before validation.

        Converts input to uppercase and remove leading/trailing spaces
        to ensure consistency (e.g, 'error ' becomes 'ERROR').

        Args:
            v: The raw value from the input data.
        Returns:
            str: Normalized uppercase severity string.
        """
        if v is None:
            return ""
        return str(v).strip().upper()

    @property
    def is_fatal(self) -> bool:
        """
        Helper property to check if the log entry represents a critical error.

        According to the task requirements, we catch 'FATAL' errors.
        'ERROR' is included for broader compatibility with provided datasets.

        Returns:
            bool: True if severity is FATAL or ERROR
        """
        return self.severity in ["FATAL", "ERROR"]
