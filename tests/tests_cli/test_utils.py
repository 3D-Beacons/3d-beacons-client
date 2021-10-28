import json
import tempfile

import gemmi
from bio3dbeacons.cli import utils


class TestUtils:
    def test_prepare_data_dictionary_from_json(self):

        tmp_file = tempfile.NamedTemporaryFile("w+")
        d = {"test": "some content"}
        json.dump(d, open(tmp_file.name, "w+"))
        r = utils.prepare_data_dictionary_from_json(tmp_file.name)

        assert r == d

    def test_get_uniprot_xml_valid(self):
        x = utils.get_uniprot_xml("P07550")

        assert x is not None

    def test_get_uniprot_xml_invalid(self):
        x = utils.get_uniprot_xml("0")

        assert x is None

    def test_prepare_data_dictionary(self, cif_doc):
        b = cif_doc.sole_block()
        r = utils.prepare_data_dictionary(b, "cif_json_mapping")

        for item in r:
            assert r.get(item)

    def test_prepare_data_dictionary_invalid(self):
        b = gemmi.cif.Block("test_block")
        r = utils.prepare_data_dictionary(b, "cif_json_mapping")

        assert not r.get("entryId") and not r.get("experimentalMethod")
