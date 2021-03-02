# core
import logging
import os
import pytest
import tempfile

# pip
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

os.environ['FLASK_ENV'] = 'TESTING'

from bio3dbeacon.database import init_db  # NOQA
from bio3dbeacon.app import create_app  # NOQA

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
    db_fd, db_path = tempfile.mkstemp()

    _app = create_app()

    LOG.debug("APP: db_path = %s", db_path)

    _app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    LOG.info("app: %s", _app)
    LOG.info("app.config: %s", _app.config)

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
def cli_runner(app):
    """A test runner for the app's Click commands."""

    LOG.info("cli_runner.app: %s", app)
    cli_runner = app.test_cli_runner()

    LOG.info("cli_runner.app.config: %s", app.config)

    LOG.info("cli_runner.app.cli_runner: %s", cli_runner)
    return cli_runner
