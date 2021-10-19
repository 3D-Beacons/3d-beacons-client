import json
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from typing import List

from gemmi import cif

from bio3dbeacons.cli import logger
from bio3dbeacons.cli.ciftojson.models import Entry
from bio3dbeacons.cli.utils import get_uniprot_xml, prepare_data_dictionary


class Cif2Json:
    cif_path: str
    output_json_path: str

    def __init__(self, cif_path: str, output_json_path: str) -> None:
        self.cif_path = cif_path
        self.output_json_path = output_json_path
        self.entry: Entry

    def read(self):
        """Reads the mmcif file and populates them in entry"""
        logger.info(f"Reading {self.cif_path}")
        try:
            doc = cif.read_file(self.cif_path)  # copy all the data from mmCIF file
            block = doc.sole_block()  # mmCIF has exactly one block

            entry = prepare_data_dictionary(block, "cif_json_mapping")

            # perform transformations
            entry["organismScientificName"] = entry["organismScientificName"].strip('"')
            entry["uniprotSequence"] = (
                entry["uniprotSequence"].strip(";").replace("\n", "")
            )
            entry["uniprotDescription"] = entry["uniprotDescription"].strip('"')

            organism_common_names: List[str] = []
            organism_synonyms: List[str] = []
            protein_full_names: List[str] = []
            protein_short_names: List[str] = []

            # parse UniProt xml
            xml_root = get_uniprot_xml(entry["uniprotAccession"])
            logger.info(f"Parsing XML for {entry['uniprotAccession']}")
            if xml_root:
                # fetch organism data
                for name in xml_root.findall(
                    "./{http://uniprot.org/uniprot}entry/{http://uniprot.org/uniprot}"
                    "organism/{http://uniprot.org/uniprot}name"
                ):
                    if name.attrib.get("type") == "common":
                        organism_common_names.append(name.text)
                    elif name.attrib.get("type") == "synonym":
                        organism_synonyms.append(name.text)

                # fetch protein names
                for alternative_name in xml_root.findall(
                    "./{http://uniprot.org/uniprot}entry/{http://uniprot.org/uniprot}"
                    "protein/{http://uniprot.org/uniprot}alternativeName"
                ):
                    for full_name in alternative_name.findall(
                        "./{http://uniprot.org/uniprot}fullName"
                    ):
                        protein_full_names.append(full_name.text)
                    for short_name in alternative_name.findall(
                        "./{http://uniprot.org/uniprot}shortName"
                    ):
                        protein_short_names.append(short_name.text)

            # add data from xml to the entry object
            entry["organismCommonNames"] = organism_common_names
            entry["organismSynonyms"] = organism_synonyms
            entry["proteinFullNames"] = protein_full_names
            entry["proteinShortNames"] = protein_short_names

            self.entry = Entry(**entry)

        except Exception as e:
            logger.error("Error in parsing the cif file!", e)
            logger.debug(e)

    def write(self):
        """Writes the data in entry to the output json"""
        try:
            with open(self.output_json_path, "w+") as f:
                json.dump(self.entry.dict(), f)
        except Exception as e:
            logger.error("Error in writing to output JSON file!", e)
            logger.debug(e)
            exit(1)

        logger.info(f"Data written to {self.output_json_path}")


def process(cif_path: str, output_json_path: str):
    cif2json = Cif2Json(cif_path=cif_path, output_json_path=output_json_path)
    cif2json.read()
    cif2json.write()


def run(cif_path: str, output_json_path: str):
    """Generates JSON from mmcif file

    Args:
        cif_path (str): Path to the cif file, if a directory is passed,
            process all .cif files inside it
        output_json_path (str): Path to output json file, if cif_path is a directory,
            this must be a directory too.
    """

    # if a directory is provided, convert all .cif files in it
    if os.path.isdir(cif_path):
        if os.path.isfile(output_json_path):
            logger.error(f"{output_json_path} is a file, must provide a directory")
            exit(1)
        # make the output dir
        os.makedirs(output_json_path, exist_ok=True)
        logger.info(f"Created directory {output_json_path}")
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() + 1) as p:
            for _, _, filenames in os.walk(cif_path):
                for cif_file in list(filter(lambda x: x.endswith(".cif"), filenames)):
                    json_file = cif_file.replace(".cif", ".json")
                    cif_file_path = f"{cif_path}/{cif_file}"
                    output_json_file_path = f"{output_json_path}/{json_file}"
                    p.submit(process, cif_file_path, output_json_file_path)

    else:
        if not os.path.isfile(cif_path):
            logger.error("CIF file not found!")
            exit(1)

        cif2json = Cif2Json(cif_path=cif_path, output_json_path=output_json_path)

        cif2json.read()
        cif2json.write()
