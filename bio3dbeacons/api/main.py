import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.params import Path, Query
from starlette import status
from starlette.responses import HTMLResponse, JSONResponse

from bio3dbeacons.api import SingletonMongoDB
from bio3dbeacons.api.constants import UNIPROT_QUAL_DESC, UNIPROT_RANGE_DESC
from bio3dbeacons.api.models.uniprot_model import UniprotKeyed
from bio3dbeacons.api.utils import get_model_asset_url

app = FastAPI()


@app.get(
    "/uniprot/summary/{qualifier}.json",
    status_code=status.HTTP_200_OK,
    summary="Get summary details for a UniProt residue range",
    description="Get all models for the UniProt residue range.",
    response_model=UniprotKeyed,
    response_model_exclude_unset=True,
)
async def get_uniprot_summary_api(
    qualifier: Any = Path(..., description=UNIPROT_QUAL_DESC),
    res_range: Any = Query(None, alias="range", description=UNIPROT_RANGE_DESC),
):
    f"""Returns summary details details for a UniProt accession

    Args:
        qualifier (Any): {UNIPROT_QUAL_DESC}
        range (Any, optional): {UNIPROT_RANGE_DESC} Defaults to None.

    Raises:
        HTTPException: Raised when there are validation issues with parameters

    Returns:
        Model: A Model object
    """

    range_present = False if not res_range else True
    residue_start = residue_end = None

    if range_present and res_range:
        if "-" not in res_range:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="range parameter should be residue start and residue"
                " end separated by -",
            )
        if res_range is not None:
            [residue_start, residue_end] = res_range.split("-")

            if not (residue_start.isnumeric() and residue_end.isnumeric()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="residue ranges should be numbers",
                )

    models_db = SingletonMongoDB.get_models_db()
    model_collection = models_db.modelCollection

    results = model_collection.find(
        {
            "$or": [
                {"mappingAccession": {"$eq": qualifier}},
                {"mappingId": {"$eq": qualifier}},
            ],
            "$and": [
                {"mappingAccessionType": {"$eq": "uniprot"}},
            ],
        }
    )

    root_obj = None
    models = []

    async for row in results:
        root_obj = {
            "uniprot_entry": {
                "ac": row["mappingAccession"],
                "id": row["mappingId"],
            },
            "structures": List[Dict],
        }
        models.append(
            {
                "model_identifier": row["entryId"],
                "model_category": row["modelCategory"],
                "model_url": get_model_asset_url(
                    row["entryId"], os.environ.get("MODEL_FORMAT", "cif")
                ),
                "provider": os.environ.get("PROVIDER"),
                "uniprot_start": row["start"],
                "uniprot_end": row["end"],
                "model_format": os.environ.get("MODEL_FORMAT", "MMCIF"),
            }
        )

    if not models:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    root_obj["structures"] = models

    return JSONResponse(content=root_obj, status_code=status.HTTP_200_OK)


@app.get("/health-check", include_in_schema=False)
def health_check():
    return HTMLResponse("success", status_code=status.HTTP_200_OK)
