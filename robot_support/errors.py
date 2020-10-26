"""system test errors"""
from robot_support.logger import Logger


LOGGER = Logger.get_instance()


class ErrorWithLog(Exception):
    """Log generic error to file"""
    def __init__(self, value: str):
        super().__init__()
        LOGGER.error(value)


class NotExpectedError(Exception):
    """Assertion error when values are not matching

    Args:
        message: error message
        quiet: suppress error, useful when expecting exception
    """
    def __init__(self, message: str, quiet: bool = False):
        super().__init__()
        if not quiet:
            LOGGER.error(f"Not expected error: {message}")


class ServiceNotReadyError(Exception):
    """Error that service required for testing is not ready

    Args:
        message: error message
        prev: logs previous error in chain
    """
    def __init__(self, message: str, prev: Exception = None):
        super().__init__()
        LOGGER.warn(f"Service not ready error: {message}")
        if prev:
            LOGGER.debug(str(prev), False)


class ServiceFailedError(Exception):
    """Error that service required for testing cannot be started

    Args:
        message: error message
        prev: logs previous error in chain
    """
    def __init__(self, value: str, prev: Exception = None):
        super().__init__()
        LOGGER.error(f"Service failed error: {value}")
        if prev:
            LOGGER.debug(prev)
