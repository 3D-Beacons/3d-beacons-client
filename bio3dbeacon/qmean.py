from dataclasses import dataclass
from typing import List
import datetime
import logging
import json
import os
from pathlib import Path
import requests
import shutil
import subprocess
import tempfile
import time

LOG = logging.getLogger(__name__)


@dataclass
class QmeanResponseResultQuery:
    ac: str
    template: str


@dataclass
class QmeanResponseStructure:
    pass


@dataclass
class QmeanResponseResult:
    crc64: str
    md5: str
    sequence: str
    sequence_length: int
    structures: QmeanResponseStructure


@dataclass
class QmeanResponseUniprotEntry:
    ac: str
    id: str
    isoid: bool


@dataclass
class QmeanResponse:
    api_version: float
    query: QmeanResponseResultQuery
    query_date: datetime.datetime
    result: List[QmeanResponseResult]
    uniprot_entries: List[QmeanResponseUniprotEntry]


class QmeanRunner:

    def __init__(self, *, app, pdb_file):
        self.app = app
        self.pdb_file = Path(pdb_file).resolve()

    def run_local(self):

        uniclust_path = self.app.config['PATH_TO_LOCAL_UNICLUST']
        qmtl_path = self.app.config['PATH_TO_LOCAL_QMTL']
        qmean_docker_image = self.app.config['QMEAN_DOCKER_IMAGE']

        model_pdb_file = 'model.pdb'
        model_seqres_file = 'model.fasta'

        original_dir = os.getcwd()

        qmean_results = None
        try:
            args = []
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir).resolve()
                LOG.debug("Moving to tmp directory: %s", tmpdir_path)

                os.chdir(tmpdir_path)
                LOG.debug("Copying PDB file to local dir: %s -> %s",
                          self.pdb_file, model_pdb_file)
                shutil.copyfile(self.pdb_file, model_pdb_file)

                LOG.debug("Creating FASTA file from PDB: %s -> %s",
                          self.pdb_file, model_seqres_file)

                with open(model_seqres_file, 'wt') as fasta_fp:
                    subprocess.run(['pdb_tofasta', self.pdb_file],
                                   stdout=fasta_fp, check=True, text=True)

                LOG.debug("Running local QMEAN analysis")
                args = ['docker', 'run',
                        '-v', f'{tmpdir_path}:{tmpdir_path}',
                        '-v', f'{uniclust_path}:/uniclust30',
                        '-v', f'{qmtl_path}:/qmtl',
                        qmean_docker_image,
                        'run_qmean.py', model_pdb_file,
                        '--seqres', model_seqres_file,
                        ]
                LOG.info("CMD: `%s`", ' '.join(args))
                result = subprocess.run(
                    args, capture_output=True, check=True, text=True)
                qmean_content = result.stdout
                qmean_results = json.loads(qmean_content)
                LOG.debug("RESULT: %s", result)
        except Exception as err:  # subprocess.CalledProcessError as err:
            msg = f"failed to run QMEAN with cmd `{args}`: {err}"
            raise err(msg)
        finally:
            os.chdir(original_dir)

        json.loads(qmean_results)

        return qmean_results

    def run_remote(self):
        LOG.debug("Running remote QMEAN analysis on PDB: %s", self.pdb_file)

        app = self.app
        pdb_file = self.pdb_file

        submit_response = self._submit(pdb_file)
        check_uri = submit_response.json()["results_json"]

        qmean_results = None
        while True:
            check_response = self._check(check_uri)
            status = check_response.json()["status"]
            if status in ('QUEUEING', 'RUNNING'):
                pass
            elif status == 'COMPLETED':
                qmean_results = check_response.json()
                break
            else:
                raise ValueError(
                    f"failed check: unknown status '{status}' ({check_uri})")
            time.sleep(5)

        return qmean_results

    def _submit(self, pdb_file):
        config = self.app.config
        pdb_file = Path(str(pdb_file)).resolve()
        kwargs = {
            'url': config['QMEAN_SUBMIT_URL'],
            'data': {"email": config['CONTACT_EMAIL']},
            'files': {"structure": open(pdb_file, 'rb')}
        }
        LOG.debug("submit.post: %s", kwargs)
        response = requests.post(**kwargs)
        LOG.debug("submit.response: %s ...", response.text[:50])
        response.raise_for_status()
        return response

    def _check(self, results_uri):
        response = requests.get(results_uri)
        response.raise_for_status()
        return response
