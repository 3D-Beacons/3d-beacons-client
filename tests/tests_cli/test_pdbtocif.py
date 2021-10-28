import filecmp
import os
import tempfile

from bio3dbeacons.cli.pdbtocif import pdbtocif


class TestPDBToCif:
    def test_convert_single_pdb_valid(self, pdb_file, cif_file):
        with tempfile.NamedTemporaryFile("w+") as temp_cif:
            s = pdbtocif.run(pdb_file, temp_cif.name)

            # test if generated file is same as the sample file
            assert filecmp.cmp(temp_cif.name, cif_file)

        # test if successful
        assert s == 0

    def test_convert_directory(self, data_dir):
        pdb_path = data_dir / "pdb"

        with tempfile.TemporaryDirectory() as output_cif_dir:
            s = pdbtocif.run(pdb_path, output_cif_dir)
            pdb_files = []
            cif_files = []
            for _, _, files in os.walk(pdb_path):
                for file in files:
                    pdb_files.append(file)

            for _, _, files in os.walk(output_cif_dir):
                for file in files:
                    cif_files.append(file)

        # test if method is successful
        assert s == 0

        # test if all files are converted
        assert len(pdb_files) == len(cif_files)

    def test_no_pdb_file(self):
        s = pdbtocif.run("some/nonexistent/pdbfile", "some/nonexistent/ciffile")

        assert s == 1

    def test_invalid_pdb_file(self):
        non_pdb_file = tempfile.NamedTemporaryFile()
        some_file = tempfile.NamedTemporaryFile()
        s = pdbtocif.run(non_pdb_file.name, some_file.name)

        assert s == 1
