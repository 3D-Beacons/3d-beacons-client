from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, Field


class ModelCategory(Enum):
    EXPERIMENTALLY_DETERMINED = "EXPERIMENTALLY DETERMINED"
    TEMPLATE_BASED = "TEMPLATE-BASED"
    AB_INITIO = "AB-INITIO"
    CONFORMATIONAL_ENSEMBLE = "CONFORMATIONAL ENSEMBLE"
    DEEP_LEARNING = "DEEP-LEARNING"


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Entry(BaseModel):
    id: PyObjectId = Field(
        default_factory=PyObjectId, description="Unique ID", alias="_id"
    )
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
    modelCategory: ModelCategory = Field(
        ..., description="Category of the model, e.g. EXPERIMENTALLY DETERMINED"
    )
