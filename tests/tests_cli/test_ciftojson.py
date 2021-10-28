import json
import os
import tempfile

from bio3dbeacons.cli.ciftojson import ciftojson

EXPECTED_OBJ = {
    "entryId": "P38398_1jm7.1.A_1_103",
    "experimentalMethod": "THEORETICAL MODEL (SWISS-MODEL SERVER)",
    "mappingAccession": "P38398",
    "mappingAccessionType": "uniprot",
    "start": 1,
    "end": 103,
    "modelCategory": "TEMPLATE-BASED",
    "modelType": "single",
    "mappingId": "BRCA1_HUMAN",
    "mappingDescription": "Breast cancer type 1 susceptibility protein",
    "gene": "BRCA1",
    "organismScientificName": "Homo sapiens",
    "taxId": 9606,
    "_id": "P38398_1jm7.1.A_1_103",
}


class TestCifToJson:
    def test_process_single_cif(self, cif_file, metatdata_file):
        _, temp_index_json = tempfile.mkstemp()
        s = ciftojson.run(cif_file, metatdata_file, temp_index_json)

        # test if operation is successful
        assert s == 0

        result_obj = json.load(open(temp_index_json))

        assert result_obj == EXPECTED_OBJ

        # delete the temporary file
        os.unlink(temp_index_json)

    def test_process_directory_single_cif(self, data_dir):
        cif_dir = data_dir / "cif"
        metadata_dir = data_dir / "metadata"

        with tempfile.TemporaryDirectory() as temp_out_dir:
            ciftojson.run(cif_dir.as_posix(), metadata_dir.as_posix(), temp_out_dir)

            for _, _, files in os.walk(temp_out_dir):

                # test if a single json is created
                assert len(files) == 1

                result_obj = json.load(open(f"{temp_out_dir}/{files[0]}"))

                assert result_obj == EXPECTED_OBJ
