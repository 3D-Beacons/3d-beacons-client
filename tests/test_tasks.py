#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_tasks

Module to test the Luigi tasks
"""

import tempfile
from pathlib import Path
import uuid 
import logging

import luigi
import pytest

import bio3dbeacon
from bio3dbeacon.app import create_app
from bio3dbeacon.database import get_db
from bio3dbeacon.database.models import ModelStructure
from bio3dbeacon.tasks import IngestModelPdb, get_file_path

DATA_ROOT = Path(__file__).parent / 'fixtures'
DATA_ORIGINAL = DATA_ROOT / 'baker_pfam' / 'original'
DATA_GENERATED = DATA_ROOT / 'baker_pfam' / 'generated'
DATA_EXPECTED = DATA_ROOT / 'baker_pfam' / 'expected'


LOG = logging.getLogger()

def test_app(app):

    pdb_file = DATA_ORIGINAL / 'pdb' / 'PF05017.pdb'
    uid = str(uuid.uuid4())

    task = IngestModelPdb(app=app, pdb_file=str(pdb_file), uid=str(uid))

    assert 'pytest-bio3dbeacon-' in task.app.config['WORK_DIR'] 


def test_ingest_model_pdb(app):
    """
    Check that we copy the model PDB okay (into file + db)
    """
    orig_pdb_file = DATA_ORIGINAL / 'pdb' / 'PF05017.pdb'
    uid = str(uuid.uuid4())

    task = IngestModelPdb(app=app, pdb_file=str(orig_pdb_file), uid=uid)

    success = luigi.build([task], local_scheduler=True)

    assert success

    expected_pdb_file = get_file_path(basedir=app.config['WORK_DIR'], uid=uid, suffix='.pdb')

    assert expected_pdb_file.exists()

    assert orig_pdb_file.read_text() == expected_pdb_file.read_text()

    with app.app_context():
        entry = ModelStructure.query.get(uid)
        assert entry
        LOG.info("entry: %s", entry)
        assert entry.created_at
        assert entry.updated_at
        assert entry.original_path == str(orig_pdb_file)

        assert entry.pdb_created_at
        assert not entry.mmcif_created_at
        assert not entry.qmean_created_at
        assert not entry.model_data_created_at



def test_process_model_pdb(app):
    pass