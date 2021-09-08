import datetime
import json
from pathlib import Path

from ..app import DB as db
from ..database.models import (
    ModelStructure,
    ModelChain,
    ModelChainSegment,
    ModelChainSegmentTemplate)

QMEAN_VERSION = '4.1'


def create_model_structures(*, json_file):

    sm_response = None
    with open(json_file, 'rt') as json_fh:
        sm_response = json.load(json_fh)

    dt_now = datetime.datetime.now()

    sm_res = sm_response.get('result')
    sm_query = sm_response.get('query')

    uniprot_acc = sm_query.get('ac')
    uniprot_md5 = sm_res.get('md5')
    uniprot_sequence = sm_res.get('sequence')
    uniprot_length = sm_res.get('sequence_length')

    structures = []
    for sm_str in sm_res.get('structures'):
        coordinates_uri = sm_str.get('coordinates')
        sm_qmean = sm_str.get('qmean')
        chains = []
        for sm_chain in sm_str.get('chains'):

            segments = []
            for sm_seg in sm_chain.get('segments'):
                smtl = sm_seg.get('smtl')
                uni = sm_seg.get('uniprot')
                seg = ModelChainSegment(
                    seqres_aligned_sequence=smtl.get('aligned_sequence'),
                    seqres_from=smtl.get('from'),
                    seqres_to=smtl.get('to'),
                    uniprot_acc=uniprot_acc,
                    uniprot_id=uniprot_acc,
                    uniprot_length=uniprot_length,
                    uniprot_md5=uniprot_md5,
                    uniprot_aligned_sequence=uni.get('aligned_sequence'),
                    uniprot_from=uni.get('from'),
                    uniprot_to=uni.get('to'),
                )
                segments.append(seg)

            chain = ModelChain(
                chain_id=sm_chain.get('id'),
                segments=segments,
            )

            chains.append(chain)

        structure = ModelStructure(
            created_at=dt_now,
            updated_at=dt_now,
            original_path=coordinates_uri,
            identity=sm_res.get('identity'),
            similarity=sm_res.get('similarity'),
            oligo_state=sm_res.get('oligo_state'),
            coverage=sm_res.get('coverage'),
            qmean_version=QMEAN_VERSION,
            qmean_avg_local_score=sm_qmean.get('avg_local_score'),
            chains=chains,
        )

        structures.append(structure)

    return structures
