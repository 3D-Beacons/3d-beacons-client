import logging
import random
import sys
from pathlib import Path

from prettyconf import config

import pymongo
import pytest

import gemmi

sys.path.append(Path(__file__).parent.parent.as_posix())

from bio3dbeacons.cli.mongoload.mongoload import MongoLoad

MONGO_USERNAME = config("MONGO_USERNAME")
MONGO_PASSWORD = config("MONGO_PASSWORD")
MONGO_DB_HOST = config("MONGO_DB_HOST")
MONGO_DB_URL = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_DB_HOST}"


LOG = logging.getLogger(__name__)


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
    yield pymongo.MongoClient(MONGO_DB_URL).models


@pytest.fixture(scope="session")
def mongo_collection(mongo_db):
    return mongo_db.modelCollection


@pytest.fixture(scope="session")
def mongo_load(mongo_collection) -> MongoLoad:
    ml = MongoLoad()
    ml.collection = mongo_collection

    return ml
