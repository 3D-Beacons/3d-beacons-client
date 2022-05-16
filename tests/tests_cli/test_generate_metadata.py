import tempfile
import pytest
import shutil
import logging
from pathlib import Path

from bio3dbeacons.cli.metadata_generators import pfam_baker
from .utils import compare_files

LOG = logging.getLogger(__name__)
DATA_ROOT = Path(__file__).parent.parent / "data" / "pfam_baker"


@pytest.fixture
def example():

    tmpdir = tempfile.TemporaryDirectory()

    tmproot = Path(tmpdir.name)
    for subdir in ["pdb", "metadata", "a3m"]:
        p = tmproot / subdir
        p.mkdir()

    class Example:
        file_stem = "PF06625"
        first_seq_id = "W5MWU3_LEPOC/50-163"
        pdb_path = tmproot / "pdb"
        a3m_path = tmproot / "a3m"
        metadata_path = tmproot / "metadata"
        model_category = "TEMPLATE-BASED"

    eg = Example()

    # copy over starting files
    shutil.copy(str(DATA_ROOT / "pdb" / (eg.file_stem + ".pdb")), str(eg.pdb_path))
    shutil.copy(str(DATA_ROOT / "a3m" / (eg.file_stem + ".a3m")), str(eg.a3m_path))

    yield eg

    tmpdir.cleanup()


def test_generate_pfam_baker_metadata(example):
    pfam_baker.run(
        example.pdb_path,
        example.a3m_path,
        example.metadata_path,
        example.model_category,
    )

    filename = str(example.file_stem + ".json")

    assert compare_files(
        got=(example.metadata_path / filename),
        expected=(DATA_ROOT / "metadata" / filename),
    )


def test_get_first_seqhdr_from_a3m(example):
    a3m_file = example.a3m_path / (example.file_stem + ".a3m")
    hdr = pfam_baker.get_first_seqhdr_from_a3m(a3m_file)
    assert hdr.hdr == example.first_seq_id


def test_split_baker_pfam_header(example):

    Hdr = pfam_baker.SeqHeader
    seqid, start, end = Hdr("W5MWU3_LEPOC/50-163").get_uniprot_start_end()
    assert [seqid, start, end] == ["W5MWU3", 50, 163]

    seqid, start, end = Hdr("A0A0R4FPS1.1/31-143").get_uniprot_start_end()
    assert [seqid, start, end] == ["A0A0R4FPS1", 31, 143]


def test_seq_header():
    hdr = pfam_baker.SeqHeader("W5MWU3_LEPOC/50-163")
    assert hdr.uniprot_acc is None
    assert hdr.version is None
    assert hdr.seq_id == "W5MWU3_LEPOC"
    assert hdr.start == 50
    assert hdr.end == 163

    hdr = pfam_baker.SeqHeader("A0A0R4FPS1.1/31-143")
    assert hdr.uniprot_acc == "A0A0R4FPS1"
    assert hdr.version == "1"
    assert hdr.seq_id == "A0A0R4FPS1"
    assert hdr.start == 31
    assert hdr.end == 143
