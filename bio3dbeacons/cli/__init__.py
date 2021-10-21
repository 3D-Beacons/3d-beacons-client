import logging
import os

import coloredlogs

handler = logging.StreamHandler()
LOG_FORMAT = "{hostname}: {username}: {asctime}: {module}: {levelname}: {message}"
handler.setFormatter(logging.Formatter(LOG_FORMAT, style="{"))

logger = logging.getLogger()

logger.addHandler(handler)

try:
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(log_level)
    coloredlogs.install(level=log_level, logger=logger)
except ValueError:
    logger.error("Invalid log level in env var LOG_LEVEL. Defaulting to INFO")
    logger.setLevel(logging.INFO)
    coloredlogs.install(level="INFO", logger=logger)
