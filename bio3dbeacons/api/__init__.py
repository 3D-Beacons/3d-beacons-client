import logging
import os

import motor.motor_asyncio

LOG_LEVEL = os.environ.get("LOG_LEVEL")
MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
MONGO_DB_HOST = os.environ.get("MONGO_DB_HOST")
MONGO_DB_URL = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_DB_HOST}"
PROXY_URL = os.environ.get("PROXY_URL")

logger = logging.getLogger("3dbeacons-client")

if LOG_LEVEL:
    logger.setLevel(LOG_LEVEL)
else:
    logger.setLevel(logging.INFO)

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)
models_db = mongo_client.models
