import logging
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper


LOG = logging.getLogger(__name__)


class UniprotSparql:

    ENDPOINT = 'https://sparql.uniprot.org/sparql'

    def get_uniprot_acc_for_gene_name(self, gene_name):
        statement = (
            "PREFIX up: <http://purl.uniprot.org/core/> "
            "SELECT ?protein "
            "WHERE { "
            "  ?protein a up:Protein . "
            "  ?protein up:mnemonic '" + gene_name + "'"
            "}")

        sparql = SPARQLWrapper(self.ENDPOINT, returnFormat=JSON)
        sparql.setQuery(statement)

        try:
            ret = sparql.query().convert()
            unp_url = ret['results']['bindings'][0]['protein']['value']
            uniprot_acc = unp_url.split('/')[-1]
            return uniprot_acc
        except Exception as err:
            msg = f"sparql query failed with genename query '{gene_name}': {err}"
            LOG.warning(msg)
            return None
