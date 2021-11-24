import os
import sys
from pathlib import Path
from typing import List

import pymongo
import pytest

import gemmi

sys.path.append(Path(__file__).parent.parent.as_posix())

from bio3dbeacons.cli.mongoload.mongoload import MongoLoad  # NOQA
from .testutils import TestExample  # NOQA

MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
MONGO_DB_HOST = os.environ.get("MONGO_DB_HOST")
MONGO_DB_URL = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_DB_HOST}"


@pytest.fixture(scope="session")
def data_dir():
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def res_dir():
    return Path(__file__).parent.parent.parent / "resources"


@pytest.fixture(scope="session")
def cif_file(data_dir) -> str:
    f = data_dir / "cif" / "P38398_1jm7.1.A_1_103.cif"
    return f.as_posix()


@pytest.fixture(scope="session")
def pdb_file(data_dir) -> str:
    f = data_dir / "pdb" / "P38398_1jm7.1.A_1_103.pdb"
    return f.as_posix()


@pytest.fixture(scope="session")
def metatdata_file(data_dir) -> str:
    f = data_dir / "metadata" / "P38398_1jm7.1.A_1_103.json"
    return f.as_posix()


@pytest.fixture(scope="function")
def cif_doc(cif_file) -> gemmi.cif.Document:
    return gemmi.cif.read_file(cif_file)


@pytest.fixture(scope="session")
def mongo_db():
    return pymongo.MongoClient(MONGO_DB_URL).models


@pytest.fixture(scope="session")
def mongo_collection(mongo_db):
    return mongo_db.modelCollection


@pytest.fixture(scope="session")
def mongo_load(mongo_collection) -> MongoLoad:
    ml = MongoLoad()
    ml.collection = mongo_collection

    return ml


@pytest.fixture(scope="function")
def make_example():

    examples = []

    def _make_example(src_root: str, stems: List[str], copy_files: bool = True):
        eg = TestExample(src_root=src_root, stems=stems, copy_files=copy_files)
        examples.append(eg)
        return eg

    yield _make_example

    for eg in examples:
        eg.cleanup()
