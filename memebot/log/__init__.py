import atexit
import contextlib
import logging
from typing import cast, Any

import discord

from memebot import config
from . import formatter, logger

memebot_logger: logger.MemeBotLogger


def log(level: int, msg: str, *args: Any, **kwargs: Any) -> None:
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    memebot_logger.log(level, msg, *args, **kwargs)


def debug(msg: str, *args: Any, **kwargs: Any) -> None:
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    memebot_logger.debug(msg, *args, **kwargs)


def info(msg: str, *args: Any, **kwargs: Any) -> None:
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    memebot_logger.info(msg, *args, **kwargs)


def warning(msg: str, *args: Any, **kwargs: Any) -> None:
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    memebot_logger.warning(msg, *args, **kwargs)


def error(msg: str, *args: Any, **kwargs: Any) -> None:
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    memebot_logger.error(msg, *args, **kwargs)


def critical(msg: str, *args: Any, **kwargs: Any) -> None:
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    memebot_logger.critical(msg, *args, **kwargs)


def exception(msg: str, exc_info: Any = True, *args: Any, **kwargs: Any) -> None:
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    memebot_logger.exception(msg, *args, exc_info=exc_info, **kwargs)


def configure_logging() -> None:
    config.log_location.setFormatter(formatter.MemeBotLogFormatter())
    logging.setLoggerClass(logger.MemeBotLogger)

    # We use a project-wide logger because of how we shim metadata into log statements
    global memebot_logger
    memebot_logger = cast(logger.MemeBotLogger, logging.getLogger("memebot"))

    # Redirect all stdout to a logger, as some packages in the stdlib still use print
    # for debug messages
    stdout_logger = logging.getLogger("stdout")
    contextlib.redirect_stdout(stdout_logger).__enter__()  # type: ignore[type-var]

    # Ensure the handler is properly flushed when MemeBot is killed
    atexit.register(logging.shutdown)


def interaction(
    inter: discord.Interaction,
    msg: str,
    level: int = logging.INFO,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Logging wrapper to prefix a log message with the interaction ID. This is helpful
    for tracking the information flow for an interaction.
    """
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
    # Highlight the interaction id
    log(level, f"\033[1mInteraction {inter.id}\033[22m {msg}", *args, **kwargs)
