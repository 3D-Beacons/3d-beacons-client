from typing import Optional

from fastapi import FastAPI

from .models import (
    UniprotEntry,
    UniprotProvider,
    UniprotSummaryResponse,
    ModelStructure)

app = FastAPI()


@ app.get("/uniprot/summary/{uniprot_id}.json")
async def uniprot_summary(uniprot_id: str,
                          provider: Optional[UniprotProvider] = None,
                          template: Optional[str] = None,
                          range: Optional[str] = None):

    unp_entry = UniprotEntry(
        ac=uniprot_id,
        id=uniprot_id,
        uniprot_md5="123ABC123ABC123ABC123ABC",
        sequence_length=543,
        segment_start=23,
        segment_end=123,
    )
    structures = [
        ModelStructure(
            model_identifier="1foo",
            model_category="DEEP-LEARNING",
            model_format="MMCIF",
            model_type="ATOMIC",
            model_url="http://foo.com/bar",
            provider="genome3d",
            number_of_conformers=3,
            created="2021-01-01",
            sequence_identity=0.85,
            uniprot_start=2,
            uniprot_end=134,
            coverage=0.5,
            experimental_method="ELECTRON CRYSTALLOGRAPHY",
            resolution=1.4,
            confidence_type="QMEAN",
            confidence_version="v1.0.2",
            confidence_avg_local_score=0.95,
        )
    ]
    upr_sum = UniprotSummaryResponse(
        uniprot_entry=unp_entry,
        structures=structures)
    return upr_sum
