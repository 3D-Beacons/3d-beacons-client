from typing import List

from pydantic import BaseModel, Field


class Entry(BaseModel):
    entryId: str = Field(..., description="Model identifier")
    gene: str = Field(..., description="Gene")
    sequenceChecksum: str = Field(..., description="Sequence checksum")
    sequenceVersionDate: str = Field(
        ..., description="Sequence version date in format yyyy-mm-dd"
    )
    uniprotAccession: str = Field(..., description="UniProt accession, e.g. P00520")
    uniprotId: str = Field(..., description="UniProt identifier, e.g. ABL1_MOUSE")
    uniprotDescription: str = Field(..., description="Description for the protein")
    taxId: int = Field(
        ...,
        description="The NCBI taxonomy identifier (taxid) that points to a node of the"
        " taxonomy tree",
    )
    organismScientificName: str = Field(
        ..., description="The scientific name of the taxonomy node"
    )
    globalMetricValue: float = Field(..., description="Global metric value")
    uniprotStart: int = Field(
        ...,
        description="The index of the first residue of the model according to UniProt"
        " sequence numbering, e.g. 1",
    )
    uniprotEnd: int = Field(
        ...,
        description="The index of the last residue of the model according to UniProt "
        "sequence numbering, e.g. 142",
    )
    uniprotSequence: str = Field(
        ..., description="Aligned amino acid one-letter code sequence"
    )
    modelCreatedDate: str = Field(
        ...,
        regex="^[1-2][9|0][0-9]{2}-[0-1][0-9]-[0-3][0-9]$",
        description="Date of release of model generation in the format of YYYY-MM-DD",
    )
    organismCommonNames: List[str] = Field(
        ..., description="Common names for the organism"
    )
    organismSynonyms: List[str] = Field(..., description="Synonyms for the organism")
    proteinFullNames: List[str] = Field(..., description="Full names for the protein")
    proteinShortNames: List[str] = Field(..., description="Short names for the protein")
