import logging


class MemeBotLogFormatter(logging.Formatter):
    """
    Defines the log formatting for MemeBot
    """

    def __init__(self) -> None:
        super().__init__(
            # This format will print as such:
            # [YYYY-MM-DD HH:MM:SS.uuu LOGLEVEL log.statement.call.site:line] I am a log message!
            fmt="[{asctime} {levelname} {module}:{lineno}]\t{message}",
            style="{",
        )
        # Have the milliseconds in timestamps separated by '.' instead of ','
        if self.default_msec_format:
            self.default_msec_format = self.default_msec_format.replace(",", ".")

    def formatMessage(self, record: logging.LogRecord) -> str:
        """
        This override causes multi-line messages to have formatting on every line
        """
        buf = []
        original_message = record.message
        for line in original_message.split("\n"):
            record.message = line
            buf.append(self._style.format(record))
        record.message = original_message
        return "\n".join(buf)

    def format(self, record: logging.LogRecord) -> str:
        """
        This override causes exceptions to be formatted in the same way as
        messages. This method is overriden instead of formatException, because
        the latter only accepts exception info as an argument rather than a LogRecord.

        This method is a little weird, because the record does not arrive with a state
        ready to be formatted. Therefore, a super call is needed before we can mess
        with the exception formatting.
        """
        if not record.exc_info:
            return super(MemeBotLogFormatter, self).format(record)

        # Pop out the record's exception info so that it doesn't get appended
        # to the message
        original_exc_info = record.exc_info
        record.exc_info = None
        # Format the message without the exception
        base_output = super(MemeBotLogFormatter, self).format(record)
        original_message = record.message
        # Store the traceback in the record's message
        record.message = self.formatException(original_exc_info)
        # Apply the same formatting to the traceback
        traceback_output = self.formatMessage(record)

        # Reset the record's attributes
        record.exc_info = original_exc_info
        record.message = original_message

        return f"{base_output}\n{traceback_output}"
