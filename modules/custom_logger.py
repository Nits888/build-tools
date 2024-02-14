# custom_logger.py

import logging
import colorlog

# Define Log LEVEL
LOG_LEVEL = logging.INFO


def setup_custom_logger(name):
    # Create a logger with the specified name
    logger = logging.getLogger(name)

    # Create a StreamHandler
    handler = colorlog.StreamHandler()

    # Create a color formatter
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s: %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # Set the formatter for the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Set the log level for the logger
    logger.setLevel(LOG_LEVEL)

    return logger
