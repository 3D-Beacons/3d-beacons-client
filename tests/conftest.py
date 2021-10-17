# core
from bio3dbeacon.config import TestingConfig
import logging
import os
import pytest
import tempfile
from pathlib import Path

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

FIXTURE_PATH = (Path(__file__).parent / 'fixtures').absolute()


@pytest.fixture
def app_factory():
    """Create and configure a new app instance for each test."""

    created_app_envs = []

    def _app_factory():

        # create a temporary file to isolate the database for each test

        LOG.info("Creating test app ... ")

        # create the app with common test config
        db_fd, db_path = tempfile.mkstemp()
        tmp_work_dir = tempfile.TemporaryDirectory(
            prefix='pytest-bio3dbeacon-')

        config = TestingConfig()
        config.WORK_DIR = tmp_work_dir.name

        _app = create_app(config=config)

        LOG.debug("APP: db_path = %s", db_path)

        _app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

        # create the database and load test data
        with _app.app_context():
            LOG.debug("Initialising test database ... ")
            init_db()
            # get_db().executescript(_data_sql)

        created_app_envs.append({
            'app': _app,
            'db_fd': db_fd,
            'db_path': db_path,
            'work_dir': tmp_work_dir,
        })

        return _app

    yield _app_factory

    for app_env in created_app_envs:
        LOG.info("Cleaning up test app ...")
        # close and remove the temporary database
        os.close(app_env['db_fd'])
        os.unlink(app_env['db_path'])
        app_env['work_dir'].cleanup()


@pytest.fixture
def app(app_factory):
    return app_factory()


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
