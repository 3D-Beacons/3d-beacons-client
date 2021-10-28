import click
from exitstatus import ExitStatus

from bio3dbeacons.cli.ciftojson import ciftojson
from bio3dbeacons.cli.mongoload import mongoload
from bio3dbeacons.cli.pdbtocif import pdbtocif


@click.group("CLI", help="CLI application for 3D Beacons utilities")
def main() -> ExitStatus:  # pragma: no cover
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
def cif_to_json(
    input_mmcif: str, input_metadata_json: str, output_index_json: str
):  # pragma: no cover
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
def pdb_to_cif(input_pdb: str, output_cif: str):  # pragma: no cover
    pdbtocif.run(pdb_path=input_pdb, output_cif_path=output_cif)


@main.command("mongo_load")
@click.option(
    "-h",
    "--mongo-db-url",
    help="Mongo DB URL",
    required=True,
)
@click.option(
    "-i",
    "--index-path",
    help="Path to index file, can be a directory as well. In case of directory, "
    "will index all json files in it.",
    required=True,
)
@click.option(
    "-b",
    "--batch-size",
    help="Number of documents to load in a batch, default 1000",
    required=False,
    default=1000,
    type=int,
)
def load_mongo(mongo_db_url: str, index_path: str, batch_size: int):  # pragma: no cover
    mongoload.run(index_path, mongo_db_url, batch_size)


if __name__ == "__main__":  # pragma: no cover
    main()
