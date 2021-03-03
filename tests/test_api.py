import logging
import os
import tempfile

import pytest
import logging

LOG = logging.getLogger(__name__)


def test_get_uniprot(client):
    uniprot_acc = 'P00520'
    rv = client.get(f'/api/uniprot/{uniprot_acc}.json')
    assert rv.status_code == 200
    LOG.info("response.json: %s", rv.json)
    assert rv.json == {'uniprot_entry': {'ac': uniprot_acc,
                                         'description': None,
                                         'id': None,
                                         'sequence_length': None,
                                         'uniprot_md5': None},
                       'structures': []}
