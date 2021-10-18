from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.params import Path, Query
from starlette import status
from starlette.responses import JSONResponse

from bio3dbeacons.api.constants import UNIPROT_QUAL_DESC, UNIPROT_RANGE_DESC
from bio3dbeacons.api.models.uniprot_model import ResultSummary
from bio3dbeacons.api.utils import query_solr

app = FastAPI()


@app.get(
    "/uniprot/summary/{qualifier}.json",
    status_code=status.HTTP_200_OK,
    summary="Get summary details for a UniProt residue range",
    description="Get all Alpha Fold models for the UniProt residue range.",
    response_model=ResultSummary,
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
                detail="range parameter should be residue start and residue "
                + "end separated by -",
            )
        if res_range is not None:
            [residue_start, residue_end] = res_range.split("-")

            if not (residue_start.isnumeric() and residue_end.isnumeric()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="residue ranges should be numbers",
                )

    response = await query_solr(qualifier)

    if response["response"]["numFound"] == 0:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    for item in response["response"]["docs"]:
        out = {
            **{
                "uniprot_entry": {
                    "sequence_length": len(item["uniprotSequence"]),
                    "ac": item["uniprotAccession"],
                    "id": item["uniprotId"],
                },
                "structures": [
                    {
                        "model_identifier": item["entryId"],
                        "model_category": "DEEP-LEARNING",
                        "model_url": "URL",
                        "provider": "AlphaFold DB",
                        "created": item["modelCreatedDate"],
                        "sequence_identity": 1,
                        "coverage": 100,
                        "uniprot_start": item["uniprotStart"],
                        "uniprot_end": item["uniprotEnd"],
                        "model_format": "MMCIF",
                    }
                ],
            }
        }

        return JSONResponse(
            content=out, headers={"Cache-Control": "public, max-age=2592000"}
        )
