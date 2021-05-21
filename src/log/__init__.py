import atexit
import contextlib
import logging

import config
from log import formatter, logger

config.log_location.setFormatter(formatter.MemeBotLogFormatter())
logging.setLoggerClass(logger.MemeBotLogger)

# Redirect all stdout to a logger, as some packages in the stdlib still use print for debug messages
stdout_logger = logging.getLogger("stdout")
contextlib.redirect_stdout(stdout_logger).__enter__()

# Ensure the handler is properly flushed when MemeBot is killed
atexit.register(logging.shutdown)


def set_third_party_logging():
    """
    Enable logging on third-party packages that can't be overwritten with MemeBotLogger
    """
    # Tweepy does not use a unified logger, so the best we can do is enable its debug mode.
    import asyncio
    import tweepy
    if config.log_level == logging.DEBUG:
        asyncio.get_event_loop().set_debug(True)
        tweepy.debug()
