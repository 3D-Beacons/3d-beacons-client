import json
import logging
import os
from pathlib import Path
import re

from bio3dbeacons.cli.models import ModelMetadata
from bio3dbeacons.cli.utils import get_avg_plddt_from_pdb
from bio3dbeacons.error import ParseError
from bio3dbeacons.api.models.uniprot_model import (
    ConfidenceType,
    Metadata,
    ModelCategory,
)

LOG = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_VERSION = "v1.0.0"

# /SAN/cath/cath_v4_3_0/alphafold/species/cleaned/arabidopsis_thaliana/AF-A0A140JWM8-F1-model_v1.pdb
AF_MODEL_FILENAME = re.compile(
    r"^AF-(?P<uniprot_acc>[A-Z0-9]+)-(?P<model_number>F[0-9]+)-model_v(?P<model_version>[0-9]+).pdb$"
)

# /SAN/cath/cath_v4_3_0/alphafold/results/cath_expanded/1.10.1000.11/af_O08967_140_263
AF_CATH_MODEL_FILENAME = re.compile(
    r"^af_(?P<uniprot_acc>[A-Z0-9]+)_(?P<uniprot_start>[0-9]+)-model_v(?P<uniprot_end>[0-9]+)$"
)


def parse_keyvalue_from_pdb_remark(filepath, prefix="CATH") -> dict:
    """
    Returns a key/value dict from REMARK fields in PDB file

    ::

    REMARK  CATH CATH_SFAM_ID 1.10.630.10
    REMARK  CATH EVALUE 0.0
    REMARK  CATH MATCH c3106fcb1d43b5aed0678513f9d73d54/24-470

    """

    keyvalue_dict = dict()

    with open(filepath, "r") as fh:
        for line_count, line in enumerate(fh, 1):
            if not line.startswith("REMARK"):
                continue
            line = line.strip()
            fields = line.split()
            if not fields[1] == prefix:
                continue

            if len(fields) != 4:
                raise ParseError(
                    f"expected 4 fields, got {len(fields)} ('{line}', line {line_count})"
                )

            keyvalue_dict[fields[2]] = fields[3]

    return keyvalue_dict


def parse_metadata_from_pdb(
    filepath,
    *,
    model_category=ModelCategory.DEEP_LEARNING,
    confidence_version=DEFAULT_CONFIDENCE_VERSION,
) -> Metadata:
    """
    Parse required metadata information from AlphaFold PDB file

    ::

    REMARK  CATH AF_MODEL /SAN/cath/cath_v4_3_0/alphafold/species/cleaned/arabidopsis_thaliana/AF-A0A140JWM8-F1-model_v1.pdb
    REMARK  CATH CATH_SFAM_ID 1.10.630.10
    REMARK  CATH EVALUE 0.0
    REMARK  CATH MATCH c3106fcb1d43b5aed0678513f9d73d54/24-470
    REMARK  CATH PFAM_ID N/A
    REMARK  CATH QUERY c3106fcb1d43b5aed0678513f9d73d54
    ATOM    195  N   HIS A  24     -22.980 -13.274  22.072  1.00 84.31           N
    ATOM    196  CA  HIS A  24     -22.861 -12.577  20.796  1.00 84.31           C
    ATOM    197  C   HIS A  24     -23.941 -11.494  20.653  1.00 84.31           C

    """

    filepath = Path(f"{filepath}").absolute()
    filename = filepath.name
    match = AF_CATH_MODEL_FILENAME.match(filename)

    if not match:
        raise ParseError(
            f"failed to parse details from alphafold filename '{filename}'"
        )

    uniprot_acc = match.group("uniprot_acc")
    uniprot_start = match.group("uniprot_start")
    uniprot_end = match.group("uniprot_end")

    # remarks_dict = parse_keyvalue_from_pdb_remark(filepath)

    avg_plddt = get_avg_plddt_from_pdb(filepath)

    Metadata(
        mappingAccession=uniprot_acc,
        mappingAccessionType="uniprot",
        start=int(uniprot_start),
        end=int(uniprot_end),
        modelCategory=model_category,
        modelType="single",
        confidenceType=ConfidenceType.pLDDT,
        confidenceVersion=confidence_version,
        confidenceAvgLocalScore=float(f"{avg_plddt:.02f}"),
    )


def run(pdb_path: str, metadata_path: str, model_category: str):
    """
    Create metadata json documents for AlphaFold models

    Args:
        pdb_path (str): Path to the PDB file, if a directory is passed,
            process all .pdb files inside it
        metadata_path (str): Path to the output metadata file, if a
            directory is passed, output to .json
    """

    pdb_path = Path(str(pdb_path)).resolve()
    metadata_path = Path(str(metadata_path)).resolve()

    def process_pdb_file(pdb_file, rel_path):
        stem = pdb_file.stem
        metadata_file = metadata_path / rel_path / (stem + ".json")
        metadata = parse_metadata_from_pdb(pdb_file)
        write_metadata_to_file(metadata_file, metadata)

    # if a directory is provided, convert all .pdb files in it
    if pdb_path.is_dir() and metadata_path.is_dir():
        LOG.info(f"Processing all PDB files in {pdb_path}")

        for path, _, files in os.walk(pdb_path):
            for pdb_file in files:
                rel_path = Path(path).relative_to(pdb_path)
                process_pdb_file(Path(pdb_file), rel_path)

    elif pdb_path.is_file() and metadata_path.is_file():
        process_pdb_file(pdb_path, ".")
    else:
        msg = (
            f"expected either all dirs or all files (not a mixture): "
            f"{pdb_path}, {metadata_path}"
        )
        raise Exception(msg)

    return 0


def write_metadata_to_file(metadata_path: Path, md: ModelMetadata) -> None:
    with metadata_path.open("wt") as fp:
        data = md.dict()
        LOG.info("data: %s", data)
        json.dump(data, fp)
