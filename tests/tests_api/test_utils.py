from bio3dbeacons.api import utils


class TestUtils:
    def test_get_model_asset_url_default(self):
        result = utils.get_model_asset_url("someEntryId")
        assert result == "/static/cif/someEntryId.cif"

    def test_get_model_asset_url_pdb(self):
        result = utils.get_model_asset_url("someEntryId", "pdb")
        assert result == "/static/pdb/someEntryId.pdb"
