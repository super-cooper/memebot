import logging


class MemeBotLogHandler(logging.Handler):
    """
    Custom Handler for MemeBotLoggers. Inherits behavior from parent Handler,
    but logs all multi-line statements with formatting on each line.
    """

    def __init__(self, parent: logging.Handler):
        super().__init__()
        self.createLock = parent.createLock
        self.acquire = parent.acquire
        self.release = parent.release
        self.setLevel = parent.setLevel
        self.setFormatter = parent.setFormatter
        self.addFilter = parent.addFilter
        self.removeFilter = parent.removeFilter
        self.filter = parent.filter
        self.flush = parent.flush
        self.close = parent.close
        self.handle = parent.handle
        self.handleError = parent.handleError
        self.format = parent.format
        self.actual_emit = parent.emit
        parent.emit = self.emit

    def emit(self, record: logging.LogRecord):
        for msg in record.msg.split('\n'):
            record.msg = msg
            self.actual_emit(record)
