import logging

import pytest

LOG = logging.getLogger(__name__)


def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'<title>3D Beacons Client' in rv.data


def test_about(client):
    assert client.get('/about').status_code == 200


def test_apidocs(client):
    assert client.get('/apidocs').status_code == 200


def test_add_data(client):
    assert client.get('/add_data').status_code == 200


def test_browse(client):
    assert client.get('/browse').status_code == 200
