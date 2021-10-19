import logging
import os

LOG_LEVEL = os.environ.get("LOG_LEVEL")

logger = logging.getLogger("3dbeacons-client-cli")

if LOG_LEVEL:
    logger.setLevel(LOG_LEVEL)
else:
    logger.setLevel(logging.INFO)
