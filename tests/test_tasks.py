#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_tasks

Module to test the Luigi tasks
"""

import tempfile
from pathlib import Path
import logging
import json
import uuid

import luigi
import bio3dbeacon

from bio3dbeacon.database.models import ModelStructure
from bio3dbeacon.tasks import IngestModelPdb, ProcessModelPdb, get_file_path

DATA_ROOT = Path(__file__).parent / 'fixtures'
DATA_ORIGINAL = DATA_ROOT / 'baker_pfam' / 'original'
DATA_GENERATED = DATA_ROOT / 'baker_pfam' / 'generated'
DATA_EXPECTED = DATA_ROOT / 'baker_pfam' / 'expected'


LOG = logging.getLogger(__name__)


def test_app(app):

    pdb_file = DATA_ORIGINAL / 'pdb' / 'PF05017.pdb'
    uid = str(uuid.uuid4())

    task = IngestModelPdb(pdb_file=str(pdb_file), uid=str(uid))

    assert 'pytest-bio3dbeacon-' in str(app.config['WORK_DIR'])

    # tasks should have been monkeypatched to return the same app
    assert 'pytest-bio3dbeacon-' in str(task.app.config['WORK_DIR'])


def test_ingest_model_pdb(app, luigi_runner):
    """
    Check that we copy the model PDB okay (into file + db)
    """
    orig_pdb_file = DATA_ORIGINAL / 'pdb' / 'PF05017.pdb'
    uid = str(uuid.uuid4())

    task = IngestModelPdb(pdb_file=str(orig_pdb_file), uid=uid)

    success = luigi_runner.run([task])

    assert success

    expected_pdb_file = get_file_path(
        basedir=app.config['WORK_DIR'], uid=uid, suffix='.pdb')

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


def test_process_model_pdb(app, monkeypatch, luigi_runner):
    """
    Process all steps required to ingest the model PDB
    """

    orig_pdb_file = DATA_ORIGINAL / 'pdb' / 'PF05017.pdb'
    expected_qmean_json_file = DATA_GENERATED / 'qmean' / 'PF05017_qmean.json'

    def mock_qmean(*args):
        with open(expected_qmean_json_file, 'rt') as fp:
            data = json.load(fp)
        return data

    monkeypatch.setattr(bio3dbeacon.tasks.QmeanRunner,
                        'run_remote', mock_qmean)

    task = ProcessModelPdb(pdb_file=str(orig_pdb_file))

    success = luigi_runner.run([task])

    assert success

    uid = task.get_uid()

    # expected_file_suffixes = ('.pdb', '.mmcif', '.bcif')
    expected_file_suffixes = ('.pdb', '.mmcif')

    for suffix in expected_file_suffixes:
        expected_path = get_file_path(
            basedir=app.config['WORK_DIR'], uid=uid, suffix=suffix)
        assert expected_path.exists()

    with app.app_context():
        entry = ModelStructure.query.get(uid)
        assert entry
        LOG.info("entry: %s", entry)
        assert entry.created_at
        assert entry.updated_at
        assert entry.original_path == str(orig_pdb_file)

        assert entry.pdb_created_at
        assert entry.mmcif_created_at
        assert entry.qmean_created_at

        assert not entry.model_data_created_at
