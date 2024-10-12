import atexit
import contextlib
import logging
from typing import cast, Any, TYPE_CHECKING

from memebot import config
from . import formatter, logger

config.log_location.setFormatter(formatter.MemeBotLogFormatter())
logging.setLoggerClass(logger.MemeBotLogger)

# We use a project-wide logger because of how we shim metadata into log statements
memebot_logger = cast(logger.MemeBotLogger, logging.getLogger("memebot"))

# Redirect all stdout to a logger, as some packages in the stdlib still use print
# for debug messages
stdout_logger = logging.getLogger("stdout")
contextlib.redirect_stdout(stdout_logger).__enter__()  # type: ignore[type-var]

# Ensure the handler is properly flushed when MemeBot is killed
atexit.register(logging.shutdown)


def set_third_party_logging() -> None:
    """
    Enable logging on third-party packages that can't be overwritten with MemeBotLogger
    """
    # Tweepy does not use a unified logger, so the best we can do is
    # enable its debug mode.
    import asyncio

    if config.log_level == logging.getLevelName(logging.DEBUG):
        asyncio.get_event_loop().set_debug(True)


# Forward memebot_logger's logging methods as module-level functions
debug = memebot_logger.debug
info = memebot_logger.info
warning = memebot_logger.warning
error = memebot_logger.error
critical = memebot_logger.critical
log = memebot_logger.log
exception = memebot_logger.exception

# discord is imported as late as possible to ensure its logger is set properly
if TYPE_CHECKING:
    import discord


def interaction(
    inter: "discord.Interaction",
    msg: str,
    level: int = logging.INFO,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Logging wrapper to prefix a log message with the interaction ID. This is helpful
    for tracking the information flow for an interaction.
    """
    # Highlight the interaction id
    log(level, f"\033[1mInteraction {inter.id}\033[22m {msg}", *args, **kwargs)
