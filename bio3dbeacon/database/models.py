# pylint: disable=no-member
from datetime import datetime
import uuid

from sqlalchemy.dialects.postgresql import JSON
from ..app import DB as db, MA as ma

# https://realpython.com/flask-connexion-rest-api-part-2/


class ModelStructure(db.Model):
    __tablename__ = 'model_structure'

    id = db.Column(db.Integer, primary_key=True)

    uid = db.Column(db.Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

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

    # https://beta.swissmodel.expasy.org/repository/uniprot/P01308.json
    # model_data = db.Column(JSON, nullable=True)

    pdb_created_at = db.Column(db.DateTime, nullable=True)
    mmcif_created_at = db.Column(db.DateTime, nullable=True)
    qmean_created_at = db.Column(db.DateTime, nullable=True)
    model_data_created_at = db.Column(db.DateTime, nullable=True)


class ModelStructureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ModelStructure
        include_fk = True


class ModelChain(db.Model):
    __tablename__ = 'model_chain'

    id = db.Column(db.Integer, primary_key=True)
    chain_id = db.Column(db.String, nullable=False)

    model_structure_id = db.Column(
        db.Integer, db.ForeignKey('model_structure.id'))

    model_structure = db.relationship(
        "ModelStructure", backref="chains")


class ModelChainSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ModelChain
        include_fk = True


class ModelChainSegment(db.Model):
    __tablename__ = 'model_chain_segment'

    id = db.Column(db.Integer, primary_key=True)

    seqres_from = db.Column(db.Integer)
    seqres_to = db.Column(db.Integer)
    seqres_aligned_sequence = db.Column(db.String)

    # segment_uniprot
    uniprot_acc = db.Column(db.String, nullable=False)
    uniprot_id = db.Column(db.String, nullable=True)
    uniprot_length = db.Column(db.Integer, nullable=False)
    uniprot_md5 = db.Column(db.String)
    uniprot_aligned_sequence = db.Column(db.String, nullable=False)
    uniprot_from = db.Column(db.Integer, nullable=False)
    uniprot_to = db.Column(db.Integer, nullable=False)

    model_chain_id = db.Column(db.Integer, db.ForeignKey('model_chain.id'))

    model_chain = db.relationship(
        "ModelChain", backref="segments")


class ModelChainSegmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ModelChainSegment
        include_fk = True


class ModelChainSegmentTemplate(db.Model):
    __tablename__ = 'model_chain_segment_template'

    id = db.Column(db.Integer, primary_key=True)

    template_id = db.Column(db.String, nullable=False)
    chain_id = db.Column(db.String, nullable=False)
    template_sequence_identity = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    provider = db.Column(db.String, nullable=False)
    experimental_method = db.Column(db.String, nullable=False)
    resolution = db.Column(db.Float, nullable=False)
    preferred_assembly_id = db.Column(db.String, nullable=True)

    model_chain_segment_id = db.Column(
        db.Integer, db.ForeignKey('model_chain_segment.id'))

    model_chain_segment = db.relationship(
        "ModelChainSegment", backref="templates")


class ModelChainSegmentTemplateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ModelChainSegmentTemplate
        include_fk = True
