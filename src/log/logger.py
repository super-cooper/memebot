import inspect
import io
import logging
import os
import threading

import config


class MemeBotLogger(logging.Logger, io.IOBase):
    """
    Defines a logging class that can be used to define a consistent logging style accross all modules
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.setLevel(config.log_level)
        self.propagate = False
        self.lock = threading.Lock()
        super().addHandler(config.log_location)

    def addHandler(self, hdlr: logging.Handler):
        # We want to avoid external packages overwriting our custom handler
        return

    def write(self, msg: str):
        """
        This method is purely for stdout redirection, as contextlib requires a file-like object for redirection.
        This method also attempts to differentiate calls to print made within the memebot repo and print them as
        info instead of debug.
        """
        with self.lock:
            # Capture the stack here, on a line without the string "print(" in it
            stack = inspect.stack()
            # Find the stack frame which (hopefully) contains the call to print
            print_frame = next((frame for frame in stack if "print(" in frame.code_context[0]), None)
            namespace = inspect.getmodulename(print_frame.filename) if print_frame is not None else "stdout"
            old_name = self.name
            self.name = namespace
            if msg and not msg.isspace():
                if print_frame is not None and not print_frame.filename.startswith(os.getcwd()):
                    # We want to use debug logging for any non-memebot modules using print
                    for line in msg.splitlines():
                        self.debug(line)
                else:
                    # If someone puts a print statement inside memebot code, output it regardless of log level
                    for line in msg.splitlines():
                        self.info(line)
            self.name = old_name
