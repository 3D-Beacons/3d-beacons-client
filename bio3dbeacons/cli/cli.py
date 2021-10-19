import subprocess

import click
from exitstatus import ExitStatus

from bio3dbeacons.cli.ciftojson import ciftojson


@click.group("CLI", help="CLI application for AlphaFold utilities")  # pragma: no cover
def main() -> ExitStatus:
    """The main CLI application

    Returns:
        int: An integer value as exit status.
    """
    return 0


@main.command("convert_cif_to_metadata_json")
@click.option(
    "-i",
    "--input_mmcif",
    help="Input MMCIF file",
    required=True,
)
@click.option(
    "-o",
    "--output_json",
    help="Output JSON",
    required=True,
)
def cif_to_json(input_mmcif: str, output_json: str):
    ciftojson.run(input_mmcif, output_json)


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
    cmd_args = ["gemmi/gemmi", "convert", "--to", "mmcif", input_pdb, output_cif]
    subprocess.check_call(cmd_args)


if __name__ == "__main__":
    main()
