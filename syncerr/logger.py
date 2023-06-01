"""
Logging module to create and setup logger
"""
import logging


def setup_logger(level: int):
    """
    setup logger
    :param name: logger name, default set to __name__
    :param level: log level, defautl set to INFO via config
    """
    fmt: str = "%(asctime)s: %(name)-10s:%(funcName)20s: %(levelname)-8s: %(message)s"
    formatter: logging.Formatter = logging.Formatter(fmt)

    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    stream = logging.StreamHandler()
    stream.setLevel(level)
    stream.setFormatter(formatter)

    logger.addHandler(stream)
