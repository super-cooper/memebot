"""
Functions that will validate string input from the command line and convert them into appropriate data for use
by the config module.
"""
import collections
import logging
import logging.handlers
import sys


# Logging validators
def validate_log_location(location: str) -> logging.Handler:
    return collections.defaultdict((lambda: logging.FileHandler(location)), **{
        "stdout": logging.StreamHandler(sys.stdout),
        "stderr": logging.StreamHandler(sys.stderr),
        "syslog": logging.handlers.SysLogHandler(),
    })[location]


def validate_bool(val: str) -> bool:
    return val.lower() in ("true", "yes", "y")
