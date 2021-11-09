import logging
import os

import coloredlogs

handler = logging.StreamHandler()
root = logging.getLogger()
root.addHandler(handler)
log_format = "%(asctime)s | %(levelname)6s | %(message)s"

root.setLevel(logging.INFO)

try:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root.setLevel(log_level)
    if log_level == 'DEBUG':
        log_format = "%(asctime)s %(module)s:%(lineno)d[%(process)d] %(levelname)6s %(message)s"

except ValueError:
    root.error("Invalid log level in env var LOG_LEVEL. Defaulting to INFO")
    log_level = logging.INFO

root.setLevel(log_level)
coloredlogs.install(level=log_level, fmt=log_format, logger=root)
