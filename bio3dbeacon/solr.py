
import pysolr

from .models import (
    UniprotEntry, ModelStructure, UniprotSummaryResponse)

SOLR_URL = 'http://localhost:8983/solr/'
SOLR_TIMEOUT = 10


def get_solr():
    _solr = pysolr.Solr(SOLR_URL, always_commit=True, timeout=SOLR_TIMEOUT)
    return Solr(_solr)


class Solr:
    def __init__(self, solr: pysolr.Solr):
        self._solr = solr

    def get_uniprot_summary(self, uniprot_id):

        solr = self._solr

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
