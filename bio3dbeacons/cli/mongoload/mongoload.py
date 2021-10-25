import json
import os
from typing import Collection, Dict, List

import pymongo
from pymongo import UpdateOne

from bio3dbeacons.cli import logger
from bio3dbeacons.config import config


class MongoLoad:

    data: List[Dict]
    collection: Collection

    def __init__(self, mongo_db_url) -> None:
        client = pymongo.MongoClient(mongo_db_url)
        db = client.models
        self.collection = db.modelCollection
        self.data = []
        self.key_fields = list(
            (x, "text") for x in config.get_config("cli", "MONGO_INDEXES").split(",")
        )

    def load(self):
        self.collection.bulk_write(self.data)

    def create_index(self):
        logger.info("Creating index")
        self.collection.create_index(self.key_fields)


def run(index_path: str, mongo_db_url: str, batch_size: int):
    """Load json documents in MONGO

    Args:
        index_path (str): Path to the index json file, if a directory is passed,
            process all .json files inside it
        mongo_db_url (str): Mongo DB URL
        batch_size (int): Number of documents to batch in a single commit
    """

    lm = MongoLoad(mongo_db_url)

    # if a directory is provided, convert all .pdb files in it
    if os.path.isdir(index_path):
        logger.info(f"Loading all json files in {index_path}")
        total = incr = 0

        for path, _, files in os.walk(index_path):
            for file in files:
                j: dict = json.load(open(f"{path}/{file}"))
                lm.data.append(
                    UpdateOne({"_id": j.get("_id")}, {"$set": j}, upsert=True)
                )
                incr += 1
                if incr == batch_size:
                    total += incr
                    incr = 0
                    lm.load()
                    lm.data.clear()
                    logger.info(f"Loading done: {incr} documents")

            if lm.data:
                lm.load()
                logger.info(f"Loading done: {incr} documents")

    else:
        if not os.path.isfile(index_path):
            logger.error("Index json not found!")
            exit(1)

        logger.info(f"Loading {index_path}")
        lm.data = [json.load(open(index_path, "r"))]
        lm.load()
        logger.info(f"Loaded {index_path}")

    lm.create_index()
