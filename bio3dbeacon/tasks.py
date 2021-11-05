#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=no-member
# core
from datetime import datetime
import hashlib
import logging
import json
from pathlib import Path
import shutil
import subprocess
import time

# pip
import requests  # noqa
import luigi  # noqa
from luigi.util import requires  # noqa

# local
import bio3dbeacon
from .app import create_app
from .database import get_db
from .database.models import ModelStructure
from .qmean import QmeanRunner

LOG = logging.getLogger(__name__)

# this is used to generate the UID for all entries
# if you change this then all database entries need
# to be recalculated (which might be what you want)
DATA_MODEL_VERSION = '1'


def get_uid_from_file(model_file):
    """
    Generates a unique id (MD5) based on the file contents (and `DATA_MODEL_VERSION`)
    """
    model_path = Path(model_file).resolve()
    model_contents = open(model_path, 'r').read()
    m = hashlib.sha256()
    m.update(model_contents.encode('utf-8'))
    m.update(DATA_MODEL_VERSION.encode('utf-8'))
    uid = m.hexdigest()
    return uid


def get_file_path(*, basedir, uid, suffix):
    """
    Generates a standardised internal file path
    """
    uid = str(uid)
    return Path(basedir) / uid[:2] / str(uid + suffix)


class BaseTask(luigi.Task):
    """
    Base class for all Luigi tasks
    """

    app = luigi.Parameter(default=create_app())


class IngestModelPdb(BaseTask):
    """
    Makes sure we have a PDB file for the model structure

    Params:
        pdb_file: PDB file
        uid: unique ID

    Output:
        /path/to/model.pdb

    """

    pdb_file = luigi.Parameter()
    uid = luigi.Parameter()

    def output(self):
        uid = str(self.uid)
        outfile = get_file_path(
            basedir=self.app.config['WORK_DIR'], uid=uid, suffix='.pdb')
        target = luigi.LocalTarget(outfile)
        target.makedirs()
        return target

    def run(self):

        uid = str(self.uid)
        pdb_path = Path(self.pdb_file).resolve()
        app = self.app

        with app.app_context():
            entry = ModelStructure.query.filter(uid=uid).one()

            dt_now = datetime.utcnow()
            if not entry:
                msg = f"failed to find entry with id '{uid}' in database"
                raise ValueError(msg)

            entry.update({
                'updated_at': dt_now,
                'original_path': str(pdb_path),
            })
            shutil.copyfile(pdb_path, self.output().path)
            db = get_db()
            LOG.info("Adding PDB entry %s to DB %s", entry, db)
            db.session.add(entry)
            db.session.commit()


@requires(IngestModelPdb)
class CalculateQmean(BaseTask):
    """
    Calculates the QMEAN score for the given PDB file

    Params:
        pdb_file: PDB file
        uid: unique ID
        run_remotely: whether to run via API or local docker (default: False)

    Input: 
        model.pdb

    Output: 
        model_qmean.json

    """

    run_remotely = luigi.Parameter(default=False)

    def output(self):
        pdb_file = self.input()
        if not pdb_file.path.endswith('.pdb'):
            raise ValueError(
                f"expected pdb_file '{pdb_file}' to end with '.pdb'")
        json_file = pdb_file.path.replace('.pdb', '_qmean.json')
        return luigi.LocalTarget(json_file)

    def run(self):

        uid = self.uid
        app = self.app

        pdb_file = Path(self.pdb_file).resolve()
        qmean_output_file = self.output()

        runner = QmeanRunner(app=self.app, pdb_file=pdb_file)

        if self.run_remotely:
            results = runner.run_remote()
        else:
            results = runner.run_local()

        score_data = results.

        dt_now = datetime.utcnow()

        with app.app_context():
            db = get_db()

            entry = ModelStructure.query.get(uid)
            if not entry:
                raise ValueError(
                    f"failed to find model_structure '{uid}' in database")

            entry.updated_at = dt_now
            entry.qmean_created_at = dt_now
            db.session.add(entry)

            LOG.info("Writing output JSON score data to: '%s'",
                     qmean_output_file)

            with qmean_output_file.temporary_path() as temp_output_path:
                json.dump(score_data, temp_output_path,
                          indent=2, sort_keys=True)

            db.session.commit()


@requires(IngestModelPdb)
class ConvertPdbToMmcif(BaseTask):
    """
    Converts model PDB to mmCIF file

    Params:
        pdb_file: PDB file
        uid: unique ID

    Input:
        model.pdb

    Output:
        model.mmcif
    """

    def output(self):
        pdb_file = self.input()
        if not pdb_file.path.endswith('.pdb'):
            raise ValueError(
                f"expected pdb_file '{pdb_file}' to end with '.pdb'")
        mmcif_file = pdb_file.path.replace('.pdb', '.mmcif')
        return luigi.LocalTarget(mmcif_file)

    def run(self):
        pdb_file = self.input()
        mmcif_atomic_file = self.output()
        with mmcif_atomic_file.temporary_path() as temp_output_path:
            LOG.info("convert PDB to mmCIF: %s -> %s",
                     pdb_file.path, temp_output_path)
            self.convert_pdb_to_mmcif(pdb_file.path, temp_output_path)
            LOG.info("updating DB")
            self.update_db()
            LOG.info("done")

    def convert_pdb_to_mmcif(self, pdb_path, mmcif_path):
        """Converts PDB to mmCIF file"""

        # gemmi_exe = self.app.config['GEMMI_EXE']
        # cmd_args = ['', 'convert', '--to', 'mmcif', pdb_path, mmcif_path]

        cmd_args = ['pdb_tocif', pdb_path]
        try:
            with open(mmcif_path, "wt") as outfile:
                subprocess.run(cmd_args, check=True, encoding='utf-8',
                               stderr=subprocess.PIPE, stdout=outfile)
        except subprocess.CalledProcessError as err:
            LOG.error("failed to convert pdb to mmcif: %s", err)
            LOG.error("CMD: %s", " ".join(cmd_args))
            LOG.error("ERROR: %s", err)
            LOG.error("STDERR: %s", err.stderr)
            LOG.error("STDOUT: %s", err.stdout)
            raise

    def update_db(self):
        """Updates the database"""
        app = self.app

        dt_now = datetime.utcnow()
        with app.app_context():
            db = get_db()
            entry = ModelStructure.query.get(self.uid)
            if not entry:
                raise ValueError(
                    f"failed to find model_structure '{self.uid}' in database")

            entry.updated_at = dt_now
            entry.mmcif_created_at = dt_now
            db.session.add(entry)

            LOG.info("Moving mmCIF file to: '%s'", self.output())
            db.session.commit()


@requires(ConvertPdbToMmcif)
class ConvertMmcifToBcif(BaseTask):
    """
    Convert mmCIF file to bCIF (molstar)

    Params:
        pdb_file: PDB file
        uid: unique ID

    Input:
        model.mmcif

    Output:
        model.bcif
    """

    def output(self):
        mmcif_file = self.input()
        if not mmcif_file.path.endswith('.mmcif'):
            raise ValueError(
                f"expected mmcif file '{mmcif_file}' to end with '.mmcif'")
        bcif_file = mmcif_file.path.replace('.mmcif', '.bcif')
        return luigi.LocalTarget(bcif_file)

    def run(self):
        mmcif_file = self.input()
        bcif_file = self.output()
        molstar_exe = self.app.config['MOLSTAR_PREPROCESS_EXE']
        cmd_args = ['node', molstar_exe,
                    '-i', mmcif_file.path, '-ob', bcif_file.path]
        try:
            subprocess.run(cmd_args, check=True, encoding='utf-8',
                           stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as err:
            LOG.error("failed to convert mmcif to bcif: %s", err)
            LOG.error("CMD: %s", " ".join(cmd_args))
            LOG.error("ERROR: %s", err)
            LOG.error("STDERR: %s", err.stderr)
            LOG.error("STDOUT: %s", err.stdout)
            raise


class ProcessModelPdb(luigi.WrapperTask):
    """
    Generate all related files for a given model PDB file

    Params:
        pdb_file: input PDB file
    """

    app = luigi.Parameter()
    pdb_file = luigi.Parameter()

    def requires(self):
        uid = str(self.uid)
        pdb_file = self.pdb_file

        LOG.info("ProcessModelPdb: calculate model quality")
        yield(CalculateQmean(pdb_file=self.pdb_file, uid=uid))
        LOG.info("ProcessModelPdb: convert pdb to mmcif")
        yield(ConvertPdbToMmcif(app=self.app, pdb_file=pdb_file, uid=uid))
        # LOG.info("ProcessModelPdb: add mmcif to molstar")
        # yield(ConvertMmcifToBcif(app=self.app, pdb_file=pdb_file, uid=uid))

    def get_uid(self):
        if not hasattr(self, '_uid'):
            self._uid = None

        if self._uid is None:
            self._uid = get_uid_from_file(self.pdb_file)

        return self._uid
