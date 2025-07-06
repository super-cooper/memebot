import io
import logging
import os
import sys

from memebot import config
from memebot.log.filter import MemebotLogFilter

memebot_context = os.getcwd()


class MemeBotLogger(logging.Logger, io.IOBase):
    """
    Defines a logging class that can be used to define a consistent logging style
    across all modules
    """

    def __init__(self, name: str, level: int | str | None = None):
        super(MemeBotLogger, self).__init__(name, level or config.log_level)
        self.propagate = False
        self.is_interactive = sys.stdin.isatty() or "pydev" in repr(
            __builtins__.get("__import__")  # type: ignore[attr-defined]
        )
        self.addFilter(MemebotLogFilter())
        super(MemeBotLogger, self).addHandler(config.log_location)

    def addHandler(self, _: logging.Handler) -> None:
        # We want to avoid external packages overwriting our custom handler
        return

    def write(self, msg: str) -> None:
        """
        This method is purely for stdout redirection, as contextlib requires a
        file-like object for redirection. This method also attempts to differentiate
        calls to print made within the memebot repo and print them as info
        instead of debug.
        """
        # This means we are in interactive mode, in which case peeking at the stack
        # can get very wonky
        if self.is_interactive and sys.__stdout__:
            sys.__stdout__.writelines([msg])
            return

        # Ensures a single trailing \n per print call
        if msg.strip() == "":
            return

        self.debug(msg, stacklevel=2)
