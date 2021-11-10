from _pytest.fixtures import fixture
import pytest
from bio3dbeacons.cli.sparql import UniprotSparql


@fixture
def sparql():
    return UniprotSparql()


def test_get_uniprot_acc_from_gene_name(sparql):
    uniprot_acc = sparql.get_uniprot_acc_for_gene_name("SMP_YERPE")
    assert uniprot_acc == "Q8ZIQ1"

    uniprot_acc = sparql.get_uniprot_acc_for_gene_name("W5MWU3_LEPOC")
    assert uniprot_acc == "W5MWU3"
