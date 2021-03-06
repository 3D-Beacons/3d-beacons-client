import logging
from flask_restx import Namespace, Resource, fields

LOG = logging.getLogger(__name__)

api = Namespace(
    'uniprot', description='Operations relating to a 3D-Beacon UniProtKB query')

uniprot_entry = api.model('UniprotEntry', {
    'sequence_length': fields.Integer(required=True, description='Sequence length'),
    'ac': fields.String(required=False, description='Accession'),
    'id': fields.String(required=False, description='Identifier'),
})

residue = api.model('Residue', {
    "residue_label": fields.String(),
    "residue_index": fields.Integer(),
})

residues_in_chain = api.model('ResiduesInChain', {
    "chain_id": fields.String(),
    "description": fields.String(),
    "interacting_PDB_residues": fields.List(fields.Nested(residue)),
})

segment_template = api.model('SegmentTemplate', {
    "last_updated": fields.DateTime(),
    "provider": fields.String(),
    "experimental_method": fields.String(),
    "resolution": fields.Float(),
    "preferred_assembly_id": fields.Integer(),
})

segment_seqres = api.model('SegmentSeqres', {
    "aligned_sequence": fields.String(),
    "description": fields.String(),
    "from": fields.Integer(),
    "to": fields.Integer(),
})

segment_uniprot = api.model('SegmentUniprot', {
    "uniprot_md5": fields.String(),
    "aligned_sequence": fields.String(),
    "description": fields.String(),
    "from": fields.Integer(),
    "to": fields.Integer(),
})

model_residue = api.model('ModelResidue', {
    "qmean": fields.Float(),
    "pdb_resnum": fields.Integer(),
    "uniprot_resnum": fields.Integer(),
})

chain_segment = api.model('ChainSegment', {
    "template": fields.Nested(segment_template),
    "seqres": fields.Nested(segment_seqres),
    "uniprot": fields.Nested(segment_uniprot),
    "residues": fields.List(fields.Nested(model_residue))
})

chain = api.model('Chain', {
    "chain_id": fields.String,
    "segments": fields.List(fields.Nested(chain_segment)),
})

structure = api.model('Structure', {
    'created': fields.DateTime,
    'identity': fields.Float,
    'similarity': fields.Float,
    'oligo-stage': fields.String,
    'coverage': fields.Float,
    'qmean_version': fields.String,
    'qmean_avg_local_score': fields.Float,
    'coordinates': fields.String,
    'pubmed_ids': fields.List(fields.String),
    'in_complex_with': fields.List(fields.Nested(residues_in_chain)),
    'bound_ligands': fields.List(fields.Nested(residues_in_chain)),
    'chains': fields.List(fields.Nested(chain)),
})

uniprot_response_query = api.model('UniprotResponseQuery', {
    'qualifier': fields.String(required=True, description='Uniprot accession'),
})

uniprot_response = api.model('UniprotResponse', {
    'uniprot_entries': fields.List(fields.Nested(uniprot_entry)),
    'structures': fields.List(fields.Nested(structure)),
})

uniprot_query = api.model('UniprotQuery', {
    'qualifier': fields.String(required=True),
    'provider': fields.String(required=False),
    'template': fields.String(required=False),
    'range': fields.String(required=False),
})


@api.param('qualifier', 'UniProtKB accession (eg "P00520")', required=True)
@api.param('provider', 'Name of the model provider (eg "PDBe", "SWISS-MODEL", "Genome3D")', required=False)
@api.param('template', 'Template is 4-letter PDB code, or 4 letter code with assembly ID and chain SMTL entries', required=False)
@api.param('range', 'Specify a UniProt sequence residue range', required=False)
class UniprotQuery(Resource):
    pass


@api.route('/<string:qualifier>.json')
@api.response(200, 'Found entries matching this query')
@api.produces('application/json')
class UniprotJsonQuery(UniprotQuery):
    """
    Query with UniProtKB accession and return a JSON data structure 
    """

    @api.doc('Return the results of the query as a data structure in JSON')
    @api.marshal_with(uniprot_response)
    def get(self, qualifier, provider=None, template=None, range=None):
        """
        Returns entries matching Uniprot query
        """
        LOG.info("UniprotJsonQuery.GET: %s", qualifier)
        return {
            'query': {'qualifier': qualifier},
            # 'result': 'foo',
            # 'sequence': 'foo',
            'md5': 'foo',
        }


@api.route('/<string:qualifier>.pdb')
@api.response(200, 'Found entries matching this query')
@api.response(404, 'Failed to find any matches for this query')
@api.produces('chemical/x-pdb')
class UniprotPdbQuery(UniprotQuery):
    """
    Query with UniProtKB accession and return a PDB data file 
    """

    @api.doc('Return the results of the query as a PDB file')
    @api.marshal_with(fields.String)
    def get(self, qualifier, provider=None, template=None, range=None):
        """
        Returns entries matching Uniprot query
        """
        LOG.info("UniprotPdbQuery.GET: %s", qualifier)
        pdb_str = ''
        return pdb_str


@api.route('/<string:qualifier>.mmcif')
@api.response(200, 'Found entries matching this query')
@api.response(404, 'Failed to find any matches for this query')
@api.produces('chemical/x-mmcif')
class UniprotMmcifQuery(UniprotQuery):
    """
    Query with UniProtKB accession and return a mmCIF data file 
    """

    @api.doc('Return the results of the query as a mmCIF file')
    @api.marshal_with(fields.String)
    def get(self, qualifier, provider=None, template=None, range=None):
        """
        Returns entries matching Uniprot query
        """
        LOG.info("UniprotMmcifQuery.GET: %s", qualifier)
        mmcif_str = ''
        return mmcif_str
