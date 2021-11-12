import json
import logging
import os
from typing import Tuple
from pathlib import Path
import re

from prettyconf import config

from bio3dbeacons.cli.models import ModelMetadata
from bio3dbeacons.cli.sparql import UniprotSparql

LOG = logging.getLogger(__name__)

UNIPROT_SPARQL = UniprotSparql()


def run(pdb_path: str, a3m_path: str, metadata_path: str, model_category: str):
    """
    Create metadata json documents for PFAM/Baker models

    Args:
        pdb_path (str): Path to the PDB file, if a directory is passed,
            process all .pdb files inside it
        a3m_path (str): Path to the A3M file, if a directory is passed,
            process all .a3m files inside it
        metadata_path (str): Path to the output metadata file, if a
            directory is passed, output to .json
    """

    pdb_path = Path(str(pdb_path)).resolve()
    a3m_path = Path(str(a3m_path)).resolve()
    metadata_path = Path(str(metadata_path)).resolve()

    def process_pdb_file(pdb_file, rel_path):
        stem = pdb_file.stem
        a3m_file = a3m_path / rel_path / (stem + '.a3m')
        metadata_file = metadata_path / rel_path / (stem + '.json')
        seq_header = get_first_seqhdr_from_a3m(a3m_file)
        uniprot_acc, start, end = seq_header.get_uniprot_start_end()
        md = ModelMetadata(
            mappingAccession=uniprot_acc,
            mappingAccessionType='uniprot',
            start=start,
            end=end,
            modelCategory=model_category,
            modelType='single',
        )
        write_metadata_to_file(metadata_file, md)

    # if a directory is provided, convert all .pdb files in it
    if pdb_path.is_dir() and a3m_path.is_dir() and metadata_path.is_dir():
        LOG.info(f"Processing all PDB files in {pdb_path}")

        for path, _, files in os.walk(pdb_path):
            for pdb_file in files:
                rel_path = Path(path).relative_to(pdb_path)
                process_pdb_file(Path(pdb_file), rel_path)

    elif pdb_path.is_file() and a3m_path.is_file() and metadata_path.is_file():
        process_pdb_file(pdb_path, '.')
    else:
        msg = (f"expected either all dirs or all files (not a mixture): "
               f"{pdb_path}, {a3m_path}, {metadata_path}")
        raise Exception(msg)

    return 0


class SeqHeader:

    WITH_SEGDATA = re.compile(r'^(?P<seq_id>.*)/(?P<start>[0-9]+)-(?P<end>[0-9]+)$')
    WITH_VERSION = re.compile(r'^(?P<seq_id>.*)\.(?P<version>[0-9]+)$')
    UNIPROT_ACC = re.compile(
        r'^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$')

    def __init__(self, hdr: str):
        self.hdr = hdr

        seq_id = hdr
        version = None
        uniprot_acc = None
        start = None
        end = None

        seg_match = self.WITH_SEGDATA.match(hdr)
        if seg_match:
            seq_id = seg_match.group('seq_id')
            start = seg_match.group('start')
            end = seg_match.group('end')

        ver_match = self.WITH_VERSION.match(seq_id)
        if ver_match:
            seq_id = ver_match.group('seq_id')
            version = ver_match.group('version')

        if self.UNIPROT_ACC.match(seq_id):
            uniprot_acc = seq_id

        self.seq_id = seq_id
        self.version = version
        self.uniprot_acc = uniprot_acc
        self.start = int(start)
        self.end = int(end)

    def get_uniprot_start_end(self) -> Tuple[str, int, int]:

        uniprot_acc = self.uniprot_acc
        if not uniprot_acc:
            gene_name = self.seq_id
            uniprot_acc = UNIPROT_SPARQL.get_uniprot_acc_for_gene_name(gene_name)

        return uniprot_acc, int(self.start), int(self.end)


def get_first_seqhdr_from_a3m(a3m_path: Path) -> SeqHeader:
    with a3m_path.open('rt') as fp:
        for line in fp:
            if line.startswith('>'):
                return SeqHeader(line[1:].strip())


def write_metadata_to_file(metadata_path: Path, md: ModelMetadata) -> None:
    with metadata_path.open('wt') as fp:
        data = md.dict()
        LOG.info("data: %s", data)
        json.dump(data, fp)
