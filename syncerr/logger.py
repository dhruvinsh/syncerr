"""
Logging module to create and setup logger
"""
import logging

from config import cfg

try:
    LEVEL = getattr(logging, str.upper(cfg.LOG_LEVEL))
except AttributeError:
    LEVEL = logging.INFO


def create_logger(name: str = __name__, level: int = LEVEL) -> logging.Logger:
    """
    setup logger
    :param name: logger name, default set to __name__
    :param level: log level, defautl set to INFO via config
    """
    fmt: str = "%(asctime)s: %(name)-10s: %(levelname)-8s: %(message)s"
    formatter: logging.Formatter = logging.Formatter(fmt)

    # pylint: disable=redefined-outer-name
    logger = logging.getLogger(name)
    logger.setLevel(level)

    stream = logging.StreamHandler()
    stream.setLevel(level)
    stream.setFormatter(formatter)

    logger.addHandler(stream)

    return logger


logger = create_logger("syncerr")
