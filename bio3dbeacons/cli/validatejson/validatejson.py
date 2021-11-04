import json
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import jsonschema
from jsonschema.exceptions import ValidationError

from bio3dbeacons.cli import logger

RESOURCES_PATH = (Path(__file__).parent.parent.parent.parent / "resources").as_posix()


class ValidateJSON:

    schema = json.load(open(f"{RESOURCES_PATH}/schema.json"))

    @classmethod
    def validate(cls, index_json) -> bool:

        if not os.path.exists(index_json):
            logger.error(f"{index_json} not found!")
            return False

        index = json.load(open(index_json))

        try:
            jsonschema.validate(index, schema=cls.schema)
            logger.info(f"Validated {index_json}")
        except ValidationError as e:
            logger.error(f"{index_json} not valid!\nExtra info: {e.message}")
            return False

        return True


def process(index_file_path: str):
    return ValidateJSON.validate(index_file_path)


def run(index_json_path: str):  # pragma: no cover
    """Validates JSON documents before loading to Mongo

    Args:
        index_json_path (str): Path to the index json file, if a directory is passed,
            process all .json files inside it
    """

    # if a directory is provided, convert all .pdb files in it
    if os.path.isdir(index_json_path):
        logger.info(f"Validating all json files in {index_json_path}")

        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() + 1) as p:
            for _, _, filenames in os.walk(index_json_path):
                for index_file in list(
                    filter(lambda x: x.endswith(".json"), filenames)
                ):
                    index_file_path = f"{index_json_path}/{index_file}"
                    p.submit(process, index_file_path)
    else:
        logger.info(f"Validating {index_json_path}")

        if ValidateJSON.validate(index_json_path):
            return 0

        return 1

    return 0
