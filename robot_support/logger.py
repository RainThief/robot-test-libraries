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


class LogError(Exception):
    """Errors that cannot be logged due to failed logger"""


def _console_debug(func: Callable[[str, List[int]], None]) -> Callable[[str, List[int]], None]:
    """Decorator to print logs to console if in debug mode

    Args:
        func: wrapped function

    Returns:
        decorated function
    """
    @wraps(func)
    def decorator(logger, message, *args):
        level = str(func.__name__).upper()

        # in debug mode all events output in console
        if logger.level == logging.DEBUG:
            stream =  sys.stdout
            if level == "ERROR":
                stream =  sys.stderr
            logger.console(f"{level}: {message}", stream)

        if len(args) > 0:
            func(logger, message, *args)
            return

        func(logger, message)

    return decorator


class Logger:
    """Logger class

    Logs to file and to console if log level is debug.
    Also encapsulates robot_logger to pass through log events
    to a more verbose log and robot reports

    Attributes:
        __INSTANCE: Logger instance
        _CREATE_KEY: Unique object reference

    Args:
        create_key: object reference to be checked to prevent
                    object being instantiated more than once
        log_path: location for log file
        level: logging level to dictate events levels to capture
    """


    __INSTANCE = None

    __CREATE_KEY = object()


    @classmethod
    def get_instance(cls, log_path: str = None, level: int = logging.INFO) -> object:
        """Gets Logger instance
        If instance does not exists then creates and returns
        """
        if cls.__INSTANCE is None:
            cls.__INSTANCE = cls(cls.__CREATE_KEY, log_path, level)
        return cls.__INSTANCE


    def __init__(self, create_key: object, log_path: str, level: int):
        if create_key != Logger.__CREATE_KEY:
            raise  LogError("Singleton class, please call Logger.get_instance()")

        self.level: int = level
        self.log_path: str = log_path

        self.test_logger: logging.Logger = logging.getLogger("robot_logger")
        self.test_logger.setLevel(level)

        if log_path is not None:
            self.set_file_log(log_path)


    def __del__(self):
        """destructor to clean up up logging resources"""
        logging.shutdown()
        if hasattr(self, 'file_handler') and self.file_handler is not None:
            self.file_handler.close()


    def set_level(self, level: str) -> None:
        """set logging level

        Args:
            level: logging level description
        """
        self.level = getattr(logging, level.upper())


    def set_file_log(self, log_path: str) -> None:
        """set logging file handler

        Args:
            log_path: location for log file
        """
        self.log_path: str = log_path
        self._check_path()
        self.file_handler: logging.FileHandler = logging.FileHandler(self.log_path, mode="w")
        self.file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        self.test_logger.addHandler(self.file_handler)


    @_console_debug
    def info(self, message) -> None:
        """Logs info event

        Args:
            message: log message
        """
        self.test_logger.info(message)


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


    @_console_debug
    def warn(self, message) -> None:
        """Logs warning event

        Args:
            message: log message
        """
        self.test_logger.warning(message)


    def error(self, message: Union[str, Exception]) -> None:
        """Logs error with stack trace

        Args:
            message: log message
        """
        # if error is exception then log trace for file log
        self.test_logger.error(Logger._format_trace(str(message)))


    @staticmethod
    def console(message: str, stream: io.TextIOWrapper =sys.stdout) -> None:
        """Prints to stdout ot stderr"""
        print(message, file=stream)
        robot_logger.console(message)


    def _check_path(self) -> None:
        """Check log path is valid directory and is writable"""
        if self.log_path is None:
            raise RuntimeError("log path has not been defined; use Logger.set_path()")

        log_dir = re.sub(r'\w+(?:\.[a-z]+)?$',"",self.log_path) or './'

        if not os.path.isdir(log_dir):
            raise NotADirectoryError("log directory does not exist")
        if not os.access(log_dir, os.W_OK):
            raise PermissionError("log directory not writable")


    @staticmethod
    def _format_trace(message: str) -> str:
        """Formats a message with stack trace

        Args:
            message: log message

        Returns:
            formatted message with stack trace
        """
        stack = inspect.stack()
        for stack_entry in enumerate(stack):
            file_stack = stack_entry[1][1]
            # disregard entries for this file in stack trace
            if "logger.py" in file_stack:
                continue
            message = str(message) + \
                "\n" + f'{"": <19} File: {file_stack}, line {str(stack_entry[1][2])}' \
                    + f' in {stack_entry[1][3]}'
            function_stack = stack_entry[1][4]
            if function_stack is not None:
                message += "\n" + f'{"": <23}' + stack_entry[1][4][0].rstrip("\r\n").lstrip(" ")
        return message
