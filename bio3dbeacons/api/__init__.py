import logging
import os

import motor.motor_asyncio
from dotenv import load_dotenv

# load variables from .env file to env vars
load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL")
MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
MONGO_DB_HOST = os.environ.get("MONGO_DB_HOST")
MONGO_DB_URL = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_DB_HOST}"
ASSETS_URL = os.environ.get("ASSETS_URL")

logger = logging.getLogger("3dbeacons-client")

if LOG_LEVEL:
    logger.setLevel(LOG_LEVEL)
else:
    logger.setLevel(logging.INFO)


class SingletonMongoDB:
    models_db = None
    mongo_client = None

    @classmethod
    def get_mongo_client(cls):
        if cls.mongo_client is None:
            cls.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)

        return cls.mongo_client

    @classmethod
    def get_models_db(cls):
        cls.models_db = cls.get_mongo_client().models

        return cls.models_db
