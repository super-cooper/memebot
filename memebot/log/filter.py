import logging
import os.path


class MemebotLogFilter(logging.Filter):
    """
    Replaces module name with fully qualified module path
    """

    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        file_path_no_ext = os.path.splitext(os.path.relpath(record.pathname))[0]
        module_path = file_path_no_ext.replace(os.sep, ".")
        record.module = module_path
        return record
