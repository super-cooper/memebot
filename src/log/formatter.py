import logging
from typing import Any


class MemeBotLogFormatter(logging.Formatter):
    """
    Defines the log formatting for MemeBot
    """

    def __init__(self):
        super().__init__(
            fmt="{asctime}\t{levelname}\t{name}: {message}",
            style='{'
        )

    def formatException(self, ex: Any) -> str:
        return repr(super().formatException(ex))

    def format(self, record: logging.LogRecord) -> str:
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result
