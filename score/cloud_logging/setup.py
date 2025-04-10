import logging
from pythonjsonlogger.json import JsonFormatter  # type: ignore
from .filter import GoogleCloudLogFilter


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.addFilter(GoogleCloudLogFilter(project="openteams-score"))
    formatter = JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
