import json

import pytest
from fastapi.testclient import TestClient
from pymongo.operations import UpdateOne
from starlette import status

from bio3dbeacons.api.main import app

client = TestClient(app)


def test_health_check_api():
    response = client.get("/health-check")

    assert response.status_code == status.HTTP_200_OK
    assert response.content.decode() == "success"


@pytest.mark.asyncio
async def test_uniprot_summary_api(mongo_collection, metadata_file):

    # add some sample entries
    data = json.load(open(metadata_file))
    data["mappingId"] = "someId"
    data["entryId"] = "someEntryId"
    mongo_collection.bulk_write(
        [UpdateOne({"_id": data.get("_id")}, {"$set": data}, upsert=True)]
    )

    # invoke the API
    response = client.get("/uniprot/summary/P38398.json")

    # clean up the collection
    mongo_collection.drop()

    assert response.status_code == status.HTTP_200_OK
