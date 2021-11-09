import json
import logging
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Dict

from fastapi.encoders import jsonable_encoder

from bio3dbeacons.cli.ciftojson.models import Entry
from bio3dbeacons.cli.utils import (
    get_uniprot_xml,
    prepare_data_dictionary,
    prepare_data_dictionary_from_json,
)
from gemmi import cif

LOG = logging.getLogger(__name__)


class Cif2Json:
    cif_path: str
    output_index_json_path: str
    entry: Entry

    def __init__(
        self, cif_path: str, metadata_json_path: str, output_index_json_path: str
    ) -> None:
        self.cif_path = cif_path
        self.metadata_json_path = metadata_json_path
        self.output_index_json_path = output_index_json_path
        self.entry: Entry
        self.interim_entry: Dict = {}

    def read_cif(self):
        """Reads the mmcif file and populates them in entry"""
        LOG.info(f"Reading {self.cif_path}")
        try:
            # copy all the data from mmCIF file
            doc = cif.read_file(self.cif_path)
            block = doc.sole_block()  # mmCIF has exactly one block

            # run the mapping from CIF
            entry = prepare_data_dictionary(block, "cif_json_mapping")

            self.interim_entry.update(entry)

        except Exception as e:
            LOG.error("Error in parsing the cif file!", e)
            LOG.debug(e)

    def read_json(self):
        """Reads the json file and populates them in entry"""
        LOG.info(f"Reading {self.metadata_json_path}")

        # run the mapping from JSON, this will override any data in CIF
        entry = prepare_data_dictionary_from_json(self.metadata_json_path)

        self.interim_entry.update(entry)

    def add_extra_uniprot_info(self):
        """Adds extra info from UniProt XML"""

        entry = {}
        # parse UniProt xml
        xml_root = get_uniprot_xml(self.interim_entry["mappingAccession"])

        LOG.info(
            f"Parsing XML for {self.interim_entry['mappingAccession']}")
        if xml_root:
            namespace = "{http://uniprot.org/uniprot}"
            # fetch accession related data
            ac_id = xml_root.find(f"./{namespace}entry/{namespace}name").text
            description = xml_root.find(
                f"./{namespace}entry/{namespace}protein/{namespace}recommendedName"
                f"/{namespace}fullName"
            ).text

            # fetch gene related data
            gene = xml_root.find(
                f"./{namespace}entry/{namespace}gene/{namespace}name"
            ).text

            # fetch organism related data
            scientific_name = xml_root.find(
                f"./{namespace}entry/{namespace}organism/{namespace}name"
            ).text
            tax_id = xml_root.find(
                f"./{namespace}entry/{namespace}organism/{namespace}dbReference"
            ).attrib.get("id")

            entry["mappingId"] = ac_id
            entry["mappingDescription"] = description
            entry["gene"] = gene
            entry["organismScientificName"] = scientific_name
            entry["taxId"] = int(tax_id)

        self.interim_entry.update(entry)

    def transform(self):
        """Performs transformation on the fields"""

        self.interim_entry["entryId"] = self.interim_entry["entryId"].strip(
            "'")
        self.interim_entry["experimentalMethod"] = self.interim_entry[
            "experimentalMethod"
        ].strip("'")

        # add unique ID
        self.interim_entry["_id"] = self.interim_entry["entryId"]

    def write(self):
        """Writes the data in entry to the output json"""
        try:
            with open(self.output_index_json_path, "w+") as f:
                json.dump(self.entry, f)
        except Exception as e:
            LOG.error("Error in writing to output JSON file! (err:%s)", e)
            LOG.debug(e)
            return 1

        LOG.info(f"Data written to {self.output_index_json_path}")

        return 0


def process(cif_path: str, metadata_json_path: str, output_index_json_path: str):
    cif2json = Cif2Json(
        cif_path=cif_path,
        metadata_json_path=metadata_json_path,
        output_index_json_path=output_index_json_path,
    )
    cif2json.read_cif()
    cif2json.read_json()

    # add extra uniprot info for uniprot accessions
    if cif2json.interim_entry.get("mappingAccessionType") == "uniprot":
        cif2json.add_extra_uniprot_info()

    cif2json.transform()
    cif2json.entry = jsonable_encoder(cif2json.interim_entry)
    cif2json.write()


def run(cif_path: str, metadata_json_path: str, output_index_json_path: str):
    """Generates JSON from mmcif file

    Args:
        cif_path (str): Path to the cif file, if a directory is passed,
            process all .cif files inside it
        output_index_json_path (str): Path to output json file,
            if cif_path is a directory, this must be a directory too.
    """

    # if a directory is provided, convert all .cif files in it
    if os.path.isdir(cif_path):
        if os.path.isfile(output_index_json_path):
            LOG.error(
                f"{output_index_json_path} is a file, must provide a directory"
            )
            return 1
        if os.path.isfile(metadata_json_path):
            LOG.error(
                f"{metadata_json_path} is a file, must provide a directory")
            return 1
        # make the output dir
        os.makedirs(output_index_json_path, exist_ok=True)
        LOG.info(f"Created directory {output_index_json_path}")

        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() + 1) as p:
            for _, _, filenames in os.walk(cif_path):
                for cif_file in list(filter(lambda x: x.endswith(".cif"), filenames)):
                    index_json_file = cif_file.replace(".cif", ".json")
                    cif_file_path = f"{cif_path}/{cif_file}"
                    output_index_json_file_path = (
                        f"{output_index_json_path}/{index_json_file}"
                    )
                    metadata_json_file_path = f"{metadata_json_path}/{index_json_file}"
                    p.submit(
                        process,
                        cif_file_path,
                        metadata_json_file_path,
                        output_index_json_file_path,
                    )

    else:
        if not os.path.isfile(cif_path):
            LOG.error("CIF file not found!")
            return 1

        cif2json = Cif2Json(
            cif_path=cif_path,
            metadata_json_path=metadata_json_path,
            output_index_json_path=output_index_json_path,
        )

        cif2json.read_cif()
        cif2json.read_json()

        # add extra uniprot info for uniprot accessions
        if cif2json.interim_entry.get("mappingAccessionType") == "uniprot":
            cif2json.add_extra_uniprot_info()

        cif2json.transform()
        cif2json.entry = jsonable_encoder(cif2json.interim_entry)
        cif2json.write()

    return 0
