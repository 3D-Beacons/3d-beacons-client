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
from bio3dbeacon import settings
from bio3dbeacon.app import app
from bio3dbeacon.database import db
from bio3dbeacon.database.models import ModelStructure

LOG = logging.getLogger(__name__)

# this is used to generate the UID for all entries
# if you change this then all database entries need
# to be recalculated (which might be what you want)
DATA_MODEL_VERSION = '1'


def get_uid_from_file(model_file):
    model_path = Path(model_file).resolve()
    model_contents = open(model_path, 'r').read()
    m = hashlib.sha256()
    m.update(model_contents.encode('utf-8'))
    m.update(DATA_MODEL_VERSION.encode('utf-8'))
    uid = m.hexdigest()
    return uid


class IngestModelPdb(luigi.Task):

    pdb_file = luigi.Parameter()
    uid = luigi.Parameter()

    def output(self):
        uid = str(self.uid)
        pdb_file = settings.WORK_DIR / uid[:2] / str(uid + '.pdb')
        target = luigi.LocalTarget(pdb_file)
        target.makedirs()
        return target

    def run(self):

        with app.app_context():
            entry = ModelStructure.query.get(self.uid)
            original_path = str(Path(self.pdb_file).resolve())

        dt_now = datetime.utcnow()
        if not entry:
            entry = ModelStructure(
                id=self.uid,
                created_at=dt_now,
                updated_at=dt_now,
                original_path=original_path)
        else:
            entry.updated_at = dt_now
            entry.original_path = original_path

        with app.app_context():
            db.session.add(entry)
            shutil.copyfile(original_path, self.output().path)
            db.session.commit()


@requires(IngestModelPdb)
class CalculateModelQuality(luigi.Task):

    def output(self):
        pdb_file = self.input()
        if not pdb_file.path.endswith('.pdb'):
            raise ValueError(
                f"expected pdb_file '{pdb_file}' to end with '.pdb'")
        json_file = pdb_file.path.replace('.pdb', '.json')
        return luigi.LocalTarget(json_file)

    def run(self):

        pdb_file = Path(self.pdb_file).resolve()

        LOG.debug("Running quality analysis on PDB: %s", self.pdb_file)
        submit_response = self._submit()
        check_uri = submit_response.json()["results_json"]

        score_data = None
        while True:
            check_response = self._check(check_uri)
            status = check_response.json()["status"]
            if status in ('QUEUEING', 'RUNNING'):
                pass
            elif status == 'COMPLETED':
                score_data = check_response.json()
                break
            else:
                raise ValueError(
                    f"failed check: unknown status '{status}' ({check_uri})")
            time.sleep(5)

        dt_now = datetime.utcnow()

        with app.app_context():
            entry = ModelStructure.query.get(self.uid)
            if not entry:
                raise ValueError(
                    f"failed to find model_structure '{self.uid}' in database")

            entry.updated_at = dt_now
            entry.qmean_created_at = dt_now
            db.session.add(entry)

            LOG.info("Writing output JSON score data to: '%s'", self.output())
            with self.output().open('w') as fh:
                json.dump(score_data, fh, indent=2, sort_keys=True)

            db.session.commit()

    def _submit(self):
        kwargs = {
            'url': settings.QMEAN_SUBMIT_URL,
            'data': {"email": settings.CONTACT_EMAIL},
            'files': {"structure": open(self.pdb_file, 'rb')}
        }
        LOG.debug("submit.post: %s", kwargs)
        response = requests.post(**kwargs)
        LOG.debug("submit.response: %s", json.dumps(
            response.json(), indent=2, sort_keys=True))
        response.raise_for_status()
        return response

    def _check(self, results_uri):
        response = requests.get(results_uri)
        response.raise_for_status()
        return response


@requires(CalculateModelQuality)
class ProcessScoresTask(luigi.Task):

    def run(self):

        LOG.debug('Loading quality score data from: %s', self.input())
        with open(self.input(), 'r') as fh:
            score_data = json.load(fh)

        qmean_disco_score = None
        for model_name, model in score_data['models'].items():
            if str(self.pdb_file.name) != str(model['original_name']):
                raise ValueError(
                    f"expected original_name to be '{self.pdb_file.name}' (not '{model['original_name']}')")

            qmean_disco_score = model['scores']['global_scores']['qmean4_z_score']


@requires(IngestModelPdb)
class ConvertPdbToMmcif(luigi.Task):

    def output(self):
        pdb_file = self.input()
        if not pdb_file.path.endswith('.pdb'):
            raise ValueError(
                f"expected pdb_file '{pdb_file}' to end with '.pdb'")
        mmcif_file = pdb_file.path.replace('.pdb', '.mmcif')
        return luigi.LocalTarget(mmcif_file)

    def convert_pdb_to_mmcif(self, pdb_path, mmcif_path):
        """Converts PDB to mmCIF file"""

        cmd_args = [str(settings.GEMMI_EXE), 'convert',
                    '--to', 'mmcif', pdb_path, mmcif_path]
        try:
            subprocess.run(cmd_args, check=True, encoding='utf-8',
                           stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as err:
            LOG.error("failed to convert pdb to mmcif: %s", err)
            LOG.error("CMD: %s", " ".join(cmd_args))
            LOG.error("ERROR: %s", err)
            LOG.error("STDERR: %s", err.stderr)
            LOG.error("STDOUT: %s", err.stdout)
            raise

    def update_db(self):
        """Updates the database"""

        dt_now = datetime.utcnow()
        with app.app_context():
            entry = ModelStructure.query.get(self.uid)
            if not entry:
                raise ValueError(
                    f"failed to find model_structure '{self.uid}' in database")

            entry.updated_at = dt_now
            entry.mmcif_created_at = dt_now
            db.session.add(entry)

            LOG.info("Moving mmCIF file to: '%s'", self.output())
            db.session.commit()

    def run(self):
        LOG.info("run.about to get output")
        pdb_file = self.input()
        LOG.info("run.about to get output")
        mmcif_atomic_file = self.output()
        LOG.info("run.mmcif_atomic_file: %s", mmcif_atomic_file)
        with mmcif_atomic_file.temporary_path() as temp_output_path:
            LOG.info("convert PDB to mmCIF: %s -> %s",
                     pdb_file.path, temp_output_path)
            self.convert_pdb_to_mmcif(pdb_file.path, temp_output_path)
            LOG.info("updating DB")
            self.update_db()
            LOG.info("done")


@requires(ConvertPdbToMmcif)
class AddMmcifToMolstar(luigi.Task):

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

        cmd_args = ['node', str(settings.MOLSTAR_PREPROCESS_EXE),
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

    pdb_file = luigi.Parameter()
    uid = luigi.Parameter()

    def requires(self):
        uid = self.uid
        LOG.info("ProcessModelPdb: calculate model quality")
        yield(CalculateModelQuality(pdb_file=self.pdb_file, uid=uid))
        LOG.info("ProcessModelPdb: convert pdb to mmcif")
        yield(ConvertPdbToMmcif(pdb_file=self.pdb_file, uid=uid))
        LOG.info("ProcessModelPdb: add mmcif to molstar")
        yield(AddMmcifToMolstar(pdb_file=self.pdb_file, uid=uid))
