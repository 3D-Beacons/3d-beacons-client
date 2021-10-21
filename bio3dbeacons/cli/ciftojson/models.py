from pydantic import BaseModel, Field


class Entry(BaseModel):
    entryId: str = Field(..., description="Model identifier")
    gene: str = Field(..., description="Gene")
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
