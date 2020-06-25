# pylint: disable=no-member
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSON

from bio3dbeacon.database import db


class ModelStructure(db.Model):
    __tablename__ = 'model_structure'

    id = db.Column(db.String, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    original_path = db.Column(db.String, nullable=False)

    identity = db.Column(db.Numeric, nullable=True)
    similarity = db.Column(db.Numeric, nullable=True)
    oligo_state = db.Column(db.String, nullable=True)
    coverage = db.Column(db.Numeric, nullable=True)
    qmean_version = db.Column(db.String, nullable=True)
    qmean_avg_local_score = db.Column(db.Numeric, nullable=True)

    # store a data structure that provides a summary of this model, eg
    # https://beta.swissmodel.expasy.org/repository/uniprot/P01308.json
    model_data = db.Column(JSON, nullable=True)

    pdb_created_at = db.Column(db.DateTime, nullable=True)
    mmcif_created_at = db.Column(db.DateTime, nullable=True)
    qmean_created_at = db.Column(db.DateTime, nullable=True)
    model_data_created_at = db.Column(db.DateTime, nullable=True)
