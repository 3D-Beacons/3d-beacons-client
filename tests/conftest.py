import logging
import os
import pytest
import tempfile

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from bio3dbeacon.config import TestingConfig
from bio3dbeacon.app import create_app
from bio3dbeacon.database import get_db, init_db

LOG = logging.getLogger(__name__)

# read in SQL for populating test data
# with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
#     _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test

    LOG.info("Creating test app ... ")

    # create the app with common test config
    test_config = TestingConfig()
    db_fd, db_path = tempfile.mkstemp()

    _app = create_app(test_config)

    LOG.debug("APP: db_path = %s", db_path)

    _app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    # create the database and load test data
    with _app.app_context():
        LOG.debug("Initialising test database ... ")
        init_db()
        # get_db().executescript(_data_sql)

    yield _app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
