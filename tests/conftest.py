import logging
import os
import tempfile
from pathlib import Path

os.environ['FLASK_ENV'] = 'TESTING'

# pip
import luigi  # NOQA
import pytest  # NOQA

# local
import bio3dbeacon  # NOQA

LOG = logging.getLogger(__name__)

FIXTURE_PATH = (Path(__file__).parent / 'fixtures').absolute()


@pytest.fixture
def luigi_runner():

    class MyLuigiRunner:
        def run(self, tasks):
            return luigi.build(tasks, workers=3, local_scheduler=True)

    return MyLuigiRunner()


@pytest.fixture
def app_factory(monkeypatch):
    """Create and configure a new app instance for each test."""

    created_app_envs = []

    def _app_factory():

        # create a temporary file to isolate the database for each test

        LOG.info("Creating test app ... ")

        # create the app with common test config
        db_fd, db_path = tempfile.mkstemp()
        tmp_work_dir = tempfile.TemporaryDirectory(
            prefix='pytest-bio3dbeacon-')

        config = bio3dbeacon.config.TestingConfig()
        config.WORK_DIR = tmp_work_dir.name

        # for the duration of this test, always return this app on 'create_app'
        original_create_app = bio3dbeacon.app.create_app
        _app = original_create_app(config=config)

        def mock_create_app(*args, **kwargs):
            LOG.warning('Using mocked create_app')
            return _app

        LOG.info("Applying monkeypatch for create_app ...")
        monkeypatch.setattr(bio3dbeacon.app, 'create_app', mock_create_app)

        LOG.debug("APP: db_path = %s", db_path)

        _app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

        # create the database and load test data
        with _app.app_context():
            LOG.debug("Initialising test database ... ")
            bio3dbeacon.database.init_db()
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
