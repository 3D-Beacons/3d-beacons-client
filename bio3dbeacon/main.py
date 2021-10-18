from typing import Optional

from fastapi import Depends, FastAPI

from .solr import Solr, get_solr

app = FastAPI()


@app.get("/uniprot/summary/{uniprot_id}.json")
async def uniprot_summary(uniprot_id: str,
                          provider: Optional[str] = None,
                          template: Optional[str] = None,
                          range: Optional[str] = None,
                          solr: Solr = Depends(get_solr)):

    upr_sum = solr.get_uniprot_summary(uniprot_id)
    return upr_sum
