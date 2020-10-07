import logging

import pytest

LOG = logging.getLogger(__name__)


def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'<title>3D Beacons Client: Home</title>' in rv.data
