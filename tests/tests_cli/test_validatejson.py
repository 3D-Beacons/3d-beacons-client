import json
import os
import tempfile

from bio3dbeacons.cli.validatejson.validatejson import ValidateJSON


class TestValidateJson:
    def test_validate_single_json(self):
        _, temp_index_json = tempfile.mkstemp()
        valid_dict = {
            "entryId": "someId",
            "experimentalMethod": "someMethod",
            "mappingAccession": "someAccession",
            "mappingAccessionType": "uniprot",
            "start": 1,
            "end": 10,
            "modelCategory": "someCategory",
            "modelType": "single",
            "mappingId": "someMappingId",
            "mappingDescription": "someDescription",
            "confidenceType": "pLDDT",
            "confidenceAvgLocalScore": 98.76,
            "_id": "someId",
        }
        json.dump(valid_dict, open(temp_index_json, "w+"))
        assert ValidateJSON.validate(temp_index_json)

        # remove temp file
        os.unlink(temp_index_json)

    def test_validate_single_json_invalid(self):
        _, temp_index_json = tempfile.mkstemp()
        invalid_dict = {"entryId": "someId"}

        json.dump(invalid_dict, open(temp_index_json, "w+"))

        # remove temp file
        os.unlink(temp_index_json)

        assert not ValidateJSON.validate(temp_index_json)
