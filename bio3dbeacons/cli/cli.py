import click
from exitstatus import ExitStatus

from bio3dbeacons.cli.ciftojson import ciftojson
from bio3dbeacons.cli.pdbtocif import pdbtocif


@click.group("CLI", help="CLI application for AlphaFold utilities")  # pragma: no cover
def main() -> ExitStatus:
    """The main CLI application

    Returns:
        int: An integer value as exit status.
    """
    return 0


@main.command("convert_cif_to_metadata_json")
@click.option(
    "-ic",
    "--input-mmcif",
    help="Input MMCIF file",
    required=True,
)
@click.option(
    "-im",
    "--input-metadata-json",
    help="Input metadata JSON",
    required=True,
)
@click.option(
    "-o",
    "--output-index-json",
    help="Output SOLR index JSON",
    required=True,
)
def cif_to_json(input_mmcif: str, input_metadata_json: str, output_index_json: str):
    ciftojson.run(
        cif_path=input_mmcif,
        metadata_json_path=input_metadata_json,
        output_index_json_path=output_index_json,
    )


@main.command("convert_pdb_to_cif")
@click.option(
    "-i",
    "--input-pdb",
    help="Input PDB to convert",
    required=True,
)
@click.option(
    "-o",
    "--output-cif",
    help="Output CIF",
    required=True,
)
def pdb_to_cif(input_pdb: str, output_cif: str):
    pdbtocif.run(pdb_path=input_pdb, output_cif_path=output_cif)


if __name__ == "__main__":
    main()
