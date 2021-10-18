from fastapi.testclient import TestClient

from bio3dbeacon.main import app

client = TestClient(app)


def test_read_main():
    uniprot_id = "P12345"
    response = client.get(f"/uniprot/summary/{uniprot_id}.json")
    assert response.status_code == 200
    data = response.json()
    assert data['uniprot_entry']['ac'] == uniprot_id
