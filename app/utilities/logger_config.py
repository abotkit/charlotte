import logging
import sys


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s'))
    return console_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        logger.addHandler(get_console_handler())
        logger.propagate = False
    return logger

