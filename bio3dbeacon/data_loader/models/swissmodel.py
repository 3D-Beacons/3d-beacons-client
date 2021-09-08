import json
import datetime
from dataclases import dataclass, field
from typing import List


@dataclass
class SMModelQuery:
    ac: str


@dataclass
class SMModelChainSegment:
    smtl_aligned_sequence: str
    smtl_description: str
    smtl_from: int
    smtl_to: int
    uniprot_aligned_sequence: str
    uniprot_from: int
    uniprot_to: int

    @classmethod
    def from_sm_obj(cls, obj):
        smtl = obj.get('smtl')
        uni = obj.get('uniprot')
        return cls(
            smtl_aligned_sequence=smtl.get('aligned_sequence'),
            smtl_description=smtl.get('description'),
            smtl_from=smtl.get('from'),
            smtl_to=smtl.get('to'),
            uniprot_aligned_sequence=uni.get('aligned_sequence'),
            uniprot_from=uni.get('from'),
            uniprot_to=uni.get('to'),
        )


@dataclass
class SMModelChain:
    id: str
    segments: List[SMModelChainSegment] = field(default_factory=list)


@dataclass
class SMModelSegmentQmean:
    avg_local_score: float
    avg_local_score_error: float


@dataclass
class SMModelStructure:
    coordinates: str
    coverage: float
    created_date: datetime.datetime
    found_by: str
    uniprot_from: int
    uniprot_to: int
    gmqe: float
    identity: float
    md5: str
    method: str
    qmean: SMModelSegmentQmean
    similarity: float
    template: str
    chains: List[SMModelChain] = field(default_factory=list)

    @classmethod
    def from_sm_obj(cls, obj):
        flds = obj.__dict__
        flds['uniprot_from'] = flds['from']
        flds['uniprot_to'] = flds['to']
        del flds['from']
        del flds['to']
        return cls(**flds)


@dataclass
class SMModelResult:
    crc64: str
    md5: str
    sequence: str
    sequence_length: int
    structures: List[SMModelStructure]


@dataclass
class SMModelResponse:
    api_version: str
    query: SMModelQuery
    query_date: datetime.datetime
    result: SMModelResult
