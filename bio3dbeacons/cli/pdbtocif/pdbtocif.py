import multiprocessing
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

from bio3dbeacons.cli import logger


class Pdb2Cif:
    pdb_path: str
    output_cif_path: str

    def __init__(self, pdb_path: str, output_cif_path: str) -> None:
        self.pdb_path = pdb_path
        self.output_cif_path = output_cif_path

    def convert(self) -> int:
        """Converts PDB to CIF"""
        logger.info(f"Converting {self.pdb_path}")
        try:
            cmd_args = [
                "gemmi",
                "convert",
                "--to",
                "mmcif",
                self.pdb_path,
                self.output_cif_path,
            ]
            subprocess.check_call(cmd_args)
            logger.info(f"Converted {self.pdb_path} to {self.output_cif_path}")

        except Exception as e:
            logger.error(f"Error in converting the PDB file!: {self.pdb_path}")
            logger.debug(e)
            return 1

        return 0


def process(pdb_path: str, output_cif_path: str):
    pdbtocif = Pdb2Cif(pdb_path=pdb_path, output_cif_path=output_cif_path)
    return pdbtocif.convert()


def run(pdb_path: str, output_cif_path: str) -> int:
    """Converts PDB to CIF file

    Args:
        pdb_path (str): Path to the PDB file, if a directory is passed,
            process all .pdb files inside it
        output_cif_path (str): Path to output cif file, if pdb_path is a directory,
            this must be a directory too.
    """

    # if a directory is provided, convert all .pdb files in it
    if os.path.isdir(pdb_path):
        if os.path.isfile(output_cif_path):
            logger.error(f"{output_cif_path} is a file, must provide a directory")
            return 1

        # make the output dir
        os.makedirs(output_cif_path, exist_ok=True)
        logger.info(f"Created directory {output_cif_path}")

        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() + 1) as p:
            for _, _, filenames in os.walk(pdb_path):
                for pdb_file in list(filter(lambda x: x.endswith(".pdb"), filenames)):
                    cif_file = pdb_file.replace(".pdb", ".cif")
                    pdb_file_path = f"{pdb_path}/{pdb_file}"
                    output_cif_file_path = f"{output_cif_path}/{cif_file}"
                    p.submit(process, pdb_file_path, output_cif_file_path)

    else:
        if not os.path.isfile(pdb_path):
            logger.error("PDB file not found!")
            return 1

        pdbtocif = Pdb2Cif(pdb_path=pdb_path, output_cif_path=output_cif_path)
        return pdbtocif.convert()

    return 0
