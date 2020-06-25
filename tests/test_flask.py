import logging
import os
import tempfile

import pytest

from bio3dbeacon.app import app

LOG = logging.getLogger(__name__)


@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            pass
            # flaskr.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/api')
    LOG.info("RV: %s", rv)
