import sys
from pathlib import Path

import mongomock
import pytest

import gemmi

sys.path.append(Path(__file__).parent.parent.as_posix())

from bio3dbeacons.cli.mongoload.mongoload import MongoLoad

print(sys.path)


@pytest.fixture(scope="session")
def data_dir():
    return Path(__file__).parent / "data"


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


@pytest.fixture(scope="function")
def mongo_collection():
    return mongomock.MongoClient().models.modelCollection


@pytest.fixture(scope="function")
def mongo_load(mongo_collection) -> MongoLoad:
    ml = MongoLoad()
    ml.collection = mongo_collection

    return ml
