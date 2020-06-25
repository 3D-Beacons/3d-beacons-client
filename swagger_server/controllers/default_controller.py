import connexion
import six

from swagger_server.models.result import Result  # noqa: E501
from swagger_server import util


def sequence_sequence_json_get(sequence, provider=None, template=None):  # noqa: E501
    """sequence_sequence_json_get

     # noqa: E501

    :param sequence: Amino acid sequence
    :type sequence: str
    :param provider: 
    :type provider: str
    :param template: Template is 4 letter PDB code, or 4 letter code with assembly ID and chain for SMTL entries
    :type template: str

    :rtype: Result
    """
    return 'do some magic!'


def uniprot_qualifier_json_get(qualifier, provider=None, template=None, range=None):  # noqa: E501
    """uniprot_qualifier_json_get

     # noqa: E501

    :param qualifier: UniProtKB accession number (AC) or entry name (ID)
    :type qualifier: str
    :param provider: 
    :type provider: str
    :param template: Template is 4 letter PDB code, or 4 letter code with assembly ID and chain for SMTL entries
    :type template: str
    :param range: Specify a UniProt sequence residue range
    :type range: str

    :rtype: Result
    """
    return 'do some magic!'


def uniprot_qualifier_pdb_get(qualifier, sort=None, provider=None, template=None, range=None):  # noqa: E501
    """uniprot_qualifier_pdb_get

     # noqa: E501

    :param qualifier: UniProtKB accession number (AC) or entry name (ID)
    :type qualifier: str
    :param sort: 
    :type sort: str
    :param provider: 
    :type provider: str
    :param template: Template is 4 letter PDB code, or 4 letter code with assembly ID and chain for SMTL entries
    :type template: str
    :param range: Specify a UniProt sequence residue range
    :type range: str

    :rtype: str
    """
    return 'do some magic!'
