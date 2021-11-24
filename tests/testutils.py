
import tempfile
from typing import List
from pathlib import Path
import shutil
import os
import logging
import filecmp

LOG = logging.getLogger(__name__)
BOOTSTRAP_TESTS = os.environ.get('BOOTSTRAP_TESTS', False)


def compare_files(*, got, expected):
    if BOOTSTRAP_TESTS:
        LOG.warning("BOOTSTRAP_TESTS: copying '%s' to '%s'", got, expected)
        shutil.copy(got, expected)
    return filecmp.cmp(got, expected)


class TestDataFile:
    """
    Represents a particular file type
    """

    def __init__(self, subpath, suffix=None):
        if suffix is None:
            suffix = f".{subpath}"

        self.name = subpath
        self.suffix = suffix
        self.subpath = subpath


class TestExample:
    """
    Represents example data used for a test
    """

    datafiles = {
        'pdb': TestDataFile('pdb'),
        'cif': TestDataFile('cif'),
        'metadata': TestDataFile('metadata', '.json'),
        'index': TestDataFile('index', '.json'),
    }

    def __init__(self, src_root: str, stems: List[str], copy_files: bool = True):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.src_root = Path(str(src_root))
        self.stems = stems
        self.create_tmp_subdirs()
        if copy_files:
            self.copy_files()

    @property
    def tmp_root(self) -> str:
        return self.tmpdir.name

    def get_src_path(self, type, stem):
        df = self.datafiles[type]
        return Path(self.src_root) / df.subpath / f"{stem}{df.suffix}"

    def get_tmp_path(self, type, stem):
        df = self.datafiles[type]
        return Path(self.tmp_root) / df.subpath / f"{stem}{df.suffix}"

    def create_tmp_subdirs(self):
        for df in self.datafiles.values():
            df_tmp_path = Path(self.tmp_root) / df.subpath
            if not df_tmp_path.exists():
                df_tmp_path.mkdir(parents=True)

    def copy_files(self, *, types: List[str] = None, stems: List[str] = None):
        """
        Copy specified files from source to tmp dir
        """

        if types is None:
            types = self.datafiles.keys()

        if stems is None:
            stems = self.stems

        for stem in stems:
            for df_type in types:
                src_path = self.get_src_path(df_type, stem)
                tmp_path = self.get_tmp_path(df_type, stem)
                if not src_path.exists():
                    continue

                if not tmp_path.parent.exists():
                    tmp_path.parent.mkdir(parents=True)

                shutil.copy(str(src_path), str(tmp_path))

    def cleanup(self):
        self.tmpdir.cleanup()
