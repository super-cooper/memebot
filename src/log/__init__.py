import atexit
import contextlib
import logging

import config
from . import formatter, logger

config.log_location.setFormatter(formatter.MemeBotLogFormatter())
logging.setLoggerClass(logger.MemeBotLogger)

# We use a project-wide logger because of how we shim metadata into log statements
memebot_logger = logging.getLogger("memebot")

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
    if config.log_level == logging.getLevelName(logging.DEBUG):
        asyncio.get_event_loop().set_debug(True)
        tweepy.debug()


# Forward memebot_logger's logging methods as module-level functions
debug = memebot_logger.debug
info = memebot_logger.info
warning = memebot_logger.warning
error = memebot_logger.error
critical = memebot_logger.critical
log = memebot_logger.log
exception = memebot_logger.exception
