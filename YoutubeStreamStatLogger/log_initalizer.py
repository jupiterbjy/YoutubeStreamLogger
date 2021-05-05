"""
Handles logging initialization.
"""

import logging

try:
    import coloredlogs
except ModuleNotFoundError:
    COLOR = False
else:
    COLOR = True


def init_logger(logger, debug, file_output=""):
    """
    Initialize logger.

    :param logger: logger created by logging module
    :param debug: if value is considered True, will set logging level to debug.
    :param file_output: path where log file is saved. leave it blank to disable file logging.
    """

    level = logging.DEBUG if debug else logging.INFO

    fmt = logging.Formatter("[%(name)s][%(levelname)s] %(asctime)s <%(funcName)s> %(message)s")

    handlers = [logging.StreamHandler()]
    if file_output:
        handlers.append(logging.FileHandler(file_output))

    logger.setLevel(level)

    for handler in handlers:
        handler.setFormatter(fmt)
        handler.setLevel(level)
        logger.addHandler(handler)

    if COLOR:
        coloredlogs.install(level=level, logger=logger)
        logger.info("Colored logging enabled.")
    else:
        logger.info("Colored logging is disabled. Install 'coloredlogs' to enable it.")
