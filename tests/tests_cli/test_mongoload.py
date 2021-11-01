import json
import os
import tempfile
from unittest.mock import patch

from bio3dbeacons.cli.mongoload.mongoload import run


class TestMongoLoad:
    def test_single_doc(self, mongo_collection, mongo_load):
        with patch(
            "bio3dbeacons.cli.mongoload.mongoload.MongoLoad.init_collection",
            return_value=mongo_collection,
        ):
            with patch(
                "bio3dbeacons.cli.mongoload.mongoload.MongoLoad",
                return_value=mongo_load,
            ):
                mongo_load.collection = mongo_collection

                _, temp_json = tempfile.mkstemp()
                d = {"test": "test", "another": 1, "_id": 1}
                with open(temp_json, "w+") as f:
                    json.dump(d, f)
                s = run(temp_json, "sample mongo url", 1)

                # test if operation is successful
                assert s == 0

                # delete the temporary file
                os.unlink(temp_json)

        cursor = mongo_load.collection.find()

        # test if there is a single document in the collection
        assert cursor.collection.estimated_document_count() == 1

    def test_directory_single_doc(self, mongo_collection, mongo_load):

        with patch(
            "bio3dbeacons.cli.mongoload.mongoload.MongoLoad.init_collection",
            return_value=mongo_collection,
        ):
            with patch(
                "bio3dbeacons.cli.mongoload.mongoload.MongoLoad",
                return_value=mongo_load,
            ):
                mongo_load.collection = mongo_collection

                temp_dir = tempfile.TemporaryDirectory()
                with open(f"{temp_dir.name}/test.json", "w+") as temp_json:
                    d = {"test": "test", "another": 1, "_id": 1}
                    json.dump(d, temp_json)

                s = run(temp_dir.name, "sample mongo url", 10)

                # test if operation is successful
                assert s == 0

        cursor = mongo_load.collection.find()

        # test if there is a single document in the collection
        assert cursor.collection.estimated_document_count() == 1

    def test_directory_multiple_docs(self, mongo_collection, mongo_load):

        with patch(
            "bio3dbeacons.cli.mongoload.mongoload.MongoLoad.init_collection",
            return_value=mongo_collection,
        ):
            with patch(
                "bio3dbeacons.cli.mongoload.mongoload.MongoLoad",
                return_value=mongo_load,
            ):
                mongo_load.collection = mongo_collection

                temp_dir = tempfile.TemporaryDirectory()
                with open(f"{temp_dir.name}/test1.json", "w+") as temp_json:
                    d = {"test": "test1", "another": 1, "_id": 1}
                    json.dump(d, temp_json)
                with open(f"{temp_dir.name}/test2.json", "w+") as temp_json:
                    d = {"test": "test2", "another": 2, "_id": 2}
                    json.dump(d, temp_json)

                s = run(temp_dir.name, "sample mongo url", 1)

                # test if operation is successful
                assert s == 0

        cursor = mongo_load.collection.find()

        # test if there is a single document in the collection
        assert cursor.collection.estimated_document_count() == 2
