"""logging module"""


import logging
import inspect
import sys
import os
import re
import io
from typing import Union, Callable, List
from functools import wraps
from robot.api import logger as robot_logger


def _console_debug(func: Callable[[str, List[int]], None]) -> Callable[[str, List[int]], None]:
    """Decorator to print logs to console if in debug mode

    Args:
        func: wrapped function

    Returns:
        decorated function
    """
    @wraps(func)
    def decorator(self, message, *args):
        level = str(func.__name__).upper()
        if level == "DEBUG" and len(args) > 0:
            func(self, message, *args)
        else:
            func(self, message)
        if self.level == logging.DEBUG:

            stream =  sys.stdout

            if level == "ERROR":
                stream =  sys.stderr
            self.console(f"{level}: {message}", stream)
    return decorator


class Logger:
    """Logger class

    Logs to file and to console if log level is debug.
    Also encapsulates robot_logger to pass through log events
    to a more verbose log and robot reports

    Attributes:
        _INSTANCE: Logger instance

    Args:
        log_path: location for log file
        level: logging level to dictate events levels to capture
    """


    _INSTANCE = None


    @classmethod
    def get_instance(cls, path: str = None, level: int = logging.INFO) -> object:
        """Gets Logger instance
        If instance does not exists then creates and returns
        """
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(path, level)
        return cls._INSTANCE


    def __init__(self, log_path: str, level: int):
        self.level: int = level
        self.log_path: str = log_path
        self.file_handler: logging.FileHandler = logging.FileHandler(self.log_path, mode="w")
        self.test_logger: logging.Logger = logging.getLogger("robot_logger")

        self._check_path()

        self.file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

        self.test_logger.addHandler(self.file_handler)
        self.test_logger.setLevel(level)



    def __del__(self):
        """destructor to cleanup up logging resources"""
        logging.shutdown()
        if hasattr(self, 'file_handler'):
            self.file_handler.close()


    @_console_debug
    def info(self, message) -> None:
        """Logs info event

        Args:
            message: log message
        """
        self.test_logger.info(message)
        robot_logger.info("INFO: " + message)


    @_console_debug
    def debug(self, message, trace=True) -> None:
        """Logs debug event with optional trace

        Args:
            message: log message
            trace: add trace to log message
        """
        if trace:
            message = Logger._format_trace(message)
        self.test_logger.debug(message)
        robot_logger.debug("DEBUG: " + message)


    @_console_debug
    def warn(self, message) -> None:
        """Logs warning event

        Args:
            message: log message
        """
        self.test_logger.warning(message)
        robot_logger.warn("WARN: " + message)


    def error(self, message: Union[str, Exception]) -> None:
        """Logs error with stack trace

        Args:
            message: log message
        """
        # if error is exception then log trace
        robot_logger.error("ERROR: " + str(message))
        message = Logger._format_trace(message)
        self.test_logger.error(message)


    @staticmethod
    def console(message: str, stream: io.TextIOWrapper =sys.stdout) -> None:
        """Prints to stdout ot stderr"""
        print(message, file=stream)


    def _check_path(self) -> None:
        """Check log path is valid directory and is writable"""
        log_dir = re.sub(r'\w+(?:\.[a-z]+)?$',"",self.log_path) or './'
        if self.log_path is None:
            raise RuntimeError("log path has not been defined; use Logger.set_path()")
        if not os.path.isdir(log_dir):
            raise NotADirectoryError("log directory does not exist")
        if not os.access(log_dir, os.W_OK):
            raise PermissionError("log directory not writable")


    @staticmethod
    def _format_trace(message) -> str:
        """Formats a message with stack trace

        Args:
            message: log message

        Returns:
            formatted message with stack trace
        """
        stack = inspect.stack()
        for stack_entry in enumerate(stack):
            message = str(message) + \
                "\n" + f'{"": <19} File: {stack_entry[1][1]}, line {str(stack_entry[1][2])}' \
                    + f' in {stack_entry[1][3]}' \
                "\n" + f'{"": <23}' + stack_entry[1][4][0].rstrip("\r\n").lstrip(" ")
        return message
