import logging
from typing import Any


class MemeBotLogFormatter(logging.Formatter):
    """
    Defines the log formatting for MemeBot
    """

    def __init__(self):
        super().__init__(
            # This format will print as such:
            # [YYYY-MM-DD HH:MM:SS.uuu   LOGLEVEL    log.statement.call.site:line] I am a log message!
            fmt="[{asctime}\t{levelname}\t{_callsite}:{_lineno}]\t{message}",
            style='{'
        )
        # Have the milliseconds in timestamps separated by '.' instead of ','
        self.default_msec_format = self.default_msec_format.replace(',', '.')

    def formatException(self, ex: Any) -> str:
        return repr(super().formatException(ex))

    def format(self, record: logging.LogRecord) -> str:
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result
