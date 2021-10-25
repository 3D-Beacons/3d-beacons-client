import json
import os

from requests import post

from bio3dbeacons.cli import logger
from bio3dbeacons.config.config import get_config


class SolrIndex:
    index_path: str
    solr_host_url: str

    def __init__(self, index_path: str, solr_host_url: str) -> None:
        self.index_path = index_path
        self.solr_host_url = solr_host_url

    def index_solr(self, data: str):
        try:
            r = post(
                url=self.solr_host_url + get_config("cli", "SOLR_INDEX_URL"),
                headers={
                    "content-type": "application/json",
                },
                data=data,
            )
            logger.info(r)
            # logger.info(f"Indexed: {r.status_code}, {r.content}")
        except Exception as e:
            logger.error("Error in indexing!")
            logger.debug(e)


def run(index_path: str, solr_host_url: str, batch_size: int):
    """Index json documents in SOLR

    Args:
        index_path (str): Path to the index json file, if a directory is passed,
            process all .json files inside it
        solr_host_url (str): SOLR host URL
        batch_size (int): Number of documents to batch in a single commit
    """

    si = SolrIndex(index_path, solr_host_url)

    # if a directory is provided, convert all .pdb files in it
    if os.path.isdir(index_path):
        logger.info(f"Indexing all json files in {index_path}")
        arr = []
        total = incr = 0

        for path, _, files in os.walk(index_path):
            for file in files:
                j: dict = json.load(open(f"{path}/{file}"))
                arr.append(j)
                incr += 1
                if incr == batch_size:
                    total += incr
                    incr = 0
                    dumped = json.dumps(arr.copy(), separators=(",", ":"))
                    arr.clear()
                    si.index_solr(data=dumped)
                    logger.info(f"Indexing done: {total}")

            if arr:
                dumped = json.dumps(arr, separators=(",", ":"))
                si.index_solr(data=dumped)

    else:
        if not os.path.isfile(index_path):
            logger.error("Index json not found!")
            exit(1)

        logger.info(f"Indexing {index_path}")
        # si.index_solr(data=json.load(index_path))
        logger.info(f"Indexed {index_path}")
