from datetime import date
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class UniprotProvider(str, Enum):
    swissmodel = "swissmodel"
    genome3d = "genome3d"
    foldx = "foldx"
    pdb = "pdb"
    ped = "ped"


class ModelType(str, Enum):
    ATOMIC = "ATOMIC"
    DUMMY = "DUMMY"
    MIX = "MIX"


class ModelCategory(str, Enum):
    EXPERIMENTALLY_DETERMINED = 'EXPERIMENTALLY DETERMINED'
    TEMPLATE_BASED = 'TEMPLATE-BASED'
    AB_INITIO = 'AB-INITIO'
    CONFORMATIONAL_ENSEMBLE = 'CONFORMATIONAL ENSEMBLE'
    DEEP_LEARNING = 'DEEP-LEARNING'


class ExperimentalMethod(str, Enum):

    ELECTRON_CRYSTALLOGRAPHY = "ELECTRON CRYSTALLOGRAPHY"
    ELECTRON_MICROSCOPY = "ELECTRON MICROSCOPY"
    EPR = "EPR"
    FIBER_DIFFRACTION = "FIBER DIFFRACTION"
    FLUORESCENCE_TRANSFER = "FLUORESCENCE TRANSFER"
    INFRARED_SPECTROSCOPY = "INFRARED SPECTROSCOPY"
    NEUTRON_DIFFRACTION = "NEUTRON DIFFRACTION"
    XRAY_POWDER_DIFFRACTION = "X-RAY POWDER DIFFRACTION"
    SOLID_STATE_NMR = "SOLID-STATE NMR"
    SOLUTION_NMR = "SOLUTION NMR"
    XRAY_SOLUTION_SCATTERING = "X-RAY SOLUTION SCATTERING"
    THEORETICAL_MODEL = "THEORETICAL MODEL"
    XRAY_DIFFRACTION = "X-RAY DIFFRACTION"
    HYBRID = "HYBRID"


class ModelFormat(str, Enum):
    PDB = "PDB"
    MMCIF = "MMCIF"
    BCIF = "BCIF"


class UniprotEntry(BaseModel):
    ac: Optional[str] = Field(
        description="UniProt accession", example="P00520")
    id: str = Field(
        description="UniProt identifier", example="ABL1_MOUSE")
    uniprot_md5: Optional[str] = Field(
        description="MD5 hash of the UniProt sequence", example="5F9BA1D4C7DE6925")
    sequence_length: Optional[int] = Field(
        description="Length of the UniProt sequence", example=76)
    segment_start: Optional[int] = Field(
        description="Index of the first residue of the UniProt sequence segment", example=2)
    segment_end: Optional[int] = Field(
        description="Index of the last residue of the UniProt sequence segment", example=86)


class ModelStructure(BaseModel):
    model_identifier: str = Field(
        description="Identifier of the model, such as PDB id", example="8kfa")
    model_category: ModelCategory = Field(
        description="Category of the model", example="DEEP-LEARNING")
    model_url: str = Field(
        description="URL of the model coordinates",
        example="https://www.ebi.ac.uk/pdbe/static/entry/1t29_updated.cif")
    model_format: ModelFormat = Field(
        description="File format of the coordinates", example="MMCIF")
    model_type: Optional[ModelType] = Field(
        description="Atomic coordinates or dummy atoms", example="ATOMIC")
    model_page_url: Optional[str] = Field(
        description="URL of a web page of the data provider that show the model",
        example="https://alphafold.ebi.ac.uk/entry/Q5VSL9")
    provider: UniprotProvider = Field(
        description="Name of the model provider", example="PED")
    number_of_conformers: Optional[int] = Field(
        description="The number of conformers in a conformational ensemble", example=42)
    ensemble_sample_url: Optional[str] = Field(
        description="URL of a sample of conformations from a conformational ensemble",
        example="https://proteinensemble.org/api/ensemble_sample/PED00001e001")
    ensemble_sample_format: Optional[ModelFormat] = Field(
        description="File format of the sample coordinates, e.g. PDB", example="PDB")
    created: date = Field(
        description="Date of release of model generation in the format of YYYY-MM-DD", example="2021-12-21")
    sequence_identity: float = Field(
        description="Sequence identity (0 to 1) of the model to the UniProt sequence", example=0.97)
    uniprot_start: int = Field(
        description="The index of the first residue of the model according to UniProt sequence numbering",
        example=2)
    uniprot_end: int = Field(
        description="The index of the last residue of the model according to UniProt sequence numbering",
        example=142)
    coverage: float = Field(
        description="Percentage (0 to 1) of the UniProt sequence covered by the model",
        example=0.4)
    experimental_method: ExperimentalMethod = Field(
        description="Experimental method used to determine the structure, if applicable",
        example="ELECTRON CRYSTALLOGRAPHY")
    resolution: float = Field(
        description="The resolution of the model in Angstrom, if applicable",
        example=1.4)
    confidence_type: str = Field(
        description="Type of the confidence measure",
        example="QMEAN")
    confidence_version: str = Field(
        description="Version of confidence measure software used to calculate quality",
        example="v1.0.2")
    confidence_avg_local_score: float = Field(
        description="Average of the confidence measures, i.e. QMEAN or pLDDT",
        example=0.95)


class UniprotSummaryResponse(BaseModel):
    uniprot_entry: UniprotEntry
    structures: List[ModelStructure]
