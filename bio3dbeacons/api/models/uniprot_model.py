from __future__ import annotations

from enum import Enum
from typing import List, Optional
from datetime import date

from pydantic import BaseModel, Field

from bio3dbeacons.api.constants import (
    MODEL_CAT_DESC,
    MODEL_CREATED_DESC,
    MODEL_ID_DESC,
    MODEL_PROVIDER_DESC,
    MODEL_URL_DESC,
    SEQ_COVERAGE_DESC,
    SEQ_IDENTITY_DESC,
    UNIPROT_AC_DESC,
    UNIPROT_END_DESC,
    UNIPROT_NAME_DESC,
    UNIPROT_START_DESC,
)


class ModelFormat(Enum):
    BCIF = "BCIF"


class ResultUniprotEntry(BaseModel):
    sequence_length: int = Field(
        ..., description="Length of the UniProt sequence, e.g. 100"
    )
    ac: str = Field(..., description=UNIPROT_AC_DESC)
    id: Optional[str] = Field(None, description=UNIPROT_NAME_DESC)


class ResultStructuresSummary(BaseModel):
    model_identifier: str = Field(..., description=MODEL_ID_DESC)
    model_category: str = Field(..., description=MODEL_CAT_DESC)
    model_url: str = Field(..., description=MODEL_URL_DESC)
    provider: str = Field(..., description=MODEL_PROVIDER_DESC)
    created: date = Field(..., description=MODEL_CREATED_DESC)
    sequence_identity: float = Field(
        ...,
        description=SEQ_IDENTITY_DESC,
    )
    coverage: float = Field(
        ...,
        description=SEQ_COVERAGE_DESC,
    )
    uniprot_start: int = Field(None, description=UNIPROT_START_DESC)
    uniprot_end: int = Field(None, description=UNIPROT_END_DESC)
    model_format: ModelFormat = Field(
        ...,
        description="File format of the coordinates, e.g. BCIF",
    )
    model_page_url: str = Field(
        None, description="URL of a web page of the data provider that show the model"
    )


class ResultSummary(BaseModel):
    uniprot_entry: ResultUniprotEntry
    structures: List[ResultStructuresSummary] = Field(
        ...,
        description="Information on the structures available for the UniProt accession",
    )
