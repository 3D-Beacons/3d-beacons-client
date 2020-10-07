import logging
import os
import tempfile

import pytest

LOG = logging.getLogger(__name__)


def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/api')
    LOG.info("RV: %s", rv)
