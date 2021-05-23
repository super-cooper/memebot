import functools
import inspect
import io
import logging
import os
import sys
from typing import Union

import config
import log

memebot_context = os.getcwd()


@functools.cache
def get_module_name_from_path(path: str) -> str:
    """
    Returns the module name for a given file as it would appear in an import statement
    :param path: The path to the python file
    :return: Essentially, the output of __name__ if it were referenced in the given module.
    If the module cannot be found, returns an empty string
    """
    target = next((mod for mod in sys.modules.values() if hasattr(mod, "__file__") and mod.__file__ == path), None)
    return target.__name__ if target else ""


class MemeBotLogger(logging.Logger, io.IOBase):
    """
    Defines a logging class that can be used to define a consistent logging style accross all modules
    """

    def __init__(self, name: str, level: Union[int, str] = config.log_level):
        super().__init__(name, level)
        self.propagate = False
        super().addHandler(config.log_location)

    def addHandler(self, _: logging.Handler):
        # We want to avoid external packages overwriting our custom handler
        return

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        """
        Apply some hooks to the internal logging function.
        """
        try:
            file_name, line_number, _, _ = self.findCaller(stack_info, stacklevel)
        except ValueError:
            # If we can't extract MemeBot logging metadata, just do the best we can
            super()._log(logging.ERROR, "Could not determine log statement callsite.", (),
                         extra={'_callsite': __name__, "_lineno": inspect.getframeinfo(inspect.currentframe()).lineno})
            super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)
            return
        # Log the line number on which the log statement was made
        memebot_lineno = f"{line_number}:"
        callsite = get_module_name_from_path(file_name)
        updated_extra = {'_lineno': line_number, '_callsite': callsite if callsite else self.name}
        if extra is not None:
            updated_extra.update(extra)
        super()._log(level, msg, args, exc_info, updated_extra, stack_info, stacklevel)

    def write(self, msg: str):
        """
        This method is purely for stdout redirection, as contextlib requires a file-like object for redirection.
        This method also attempts to differentiate calls to print made within the memebot repo and print them as
        info instead of debug.
        """
        if msg and not msg.isspace():
            # Capture the stack here, on a line without the string "print(" in it
            stack = inspect.stack()
            # Find the stack frame which (hopefully) contains the call to print
            print_frame = next((frame for frame in stack if "print(" in frame.code_context[0]), None)
            if print_frame is not None:
                module_name = get_module_name_from_path(print_frame.filename)
                log_extra = {"_callsite": module_name, "_lineno": print_frame.lineno}
                if print_frame.filename.startswith(memebot_context):
                    # If someone puts a print statement inside memebot code, output it regardless of log level
                    log.log_all(self.info, msg.splitlines(), extra=log_extra)
                else:
                    # We want to use debug logging for any non-memebot modules using print
                    log.log_all(self.debug, msg.splitlines(), extra=log_extra)
            else:
                self.error(
                    f"Attempted to format a print statement, but couldn't figure out where the print came from",
                    stack_info=True)
                log.log_all(self.info, msg.splitlines())