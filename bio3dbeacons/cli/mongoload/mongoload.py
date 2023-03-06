import json
import logging
import os
from typing import Collection, Dict, List

import pymongo
from pymongo import UpdateOne

from bio3dbeacons.config import config

LOG = logging.getLogger(__name__)


class MongoLoad:

    data: List[Dict]
    collection: Collection

    def __init__(self) -> None:
        self.data = []
        self.key_fields = list(
            (x, "text") for x in config.get_config("cli", "MONGO_INDEXES").split(",")
        )

    def init_collection(self, mongo_db_url):
        self.collection = pymongo.MongoClient(
            mongo_db_url).models.modelCollection

    def load(self):
        self.collection.bulk_write(self.data)

    def create_index(self):
        LOG.info("Creating index")
        self.collection.create_index(self.key_fields)


def run(index_path: str, mongo_db_url: str, batch_size: int):
    """Load json documents in MONGO

    Args:
        index_path (str): Path to the index json file, if a directory is passed,
            process all .json files inside it
        mongo_db_url (str): Mongo DB URL
        batch_size (int): Number of documents to batch in a single commit
    """

    lm = MongoLoad()
    lm.init_collection(mongo_db_url)

    # if a directory is provided, convert all .pdb files in it
    if os.path.isdir(index_path):
        LOG.info(f"Loading all json files in {index_path}")
        total = incr = 0

        for path, _, files in os.walk(index_path):
            for file in filter(lambda x: x.endswith(".json"), files):
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
                    LOG.info(f"Loading done: {incr} documents")

            if lm.data:
                lm.load()
                LOG.info(f"Loading done: {incr} documents")

    else:
        if not os.path.isfile(index_path):
            LOG.error("Index json not found!")
            return 1

        LOG.info(f"Loading {index_path}")
        d = json.load(open(index_path, "r"))
        lm.data.append(
            UpdateOne({"_id": d.get("_id")}, {"$set": d}, upsert=True))
        lm.load()
        LOG.info(f"Loaded {index_path}")

    lm.create_index()

    return 0
