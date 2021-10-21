import json
import xml.etree.ElementTree as ET
from typing import Any, Dict

import requests

from bio3dbeacons.cli import logger
from bio3dbeacons.config.config import get_config, get_config_keys


def prepare_data_dictionary(cif_block: Any, config_section: str):

    data_dict: Dict = dict()

    for key in get_config_keys(config_section):
        mapping = get_config(config_section, key)
        data_dict[key] = cif_block.find_value(mapping)

    return data_dict


def get_uniprot_xml(accession: str) -> ET.Element:

    uniprot_xml_url = get_config("cli", "UNIPROT_XML_URL")

    try:
        response = requests.get(f"{uniprot_xml_url}/{accession}.xml")
        logger.info(f"Received {uniprot_xml_url}/{accession}.xml")
        return ET.fromstring(response.content)
    except Exception as e:
        logger.error(f"Error in parsing UniProt XML for {accession}!")
        logger.debug(e)

    return None


def prepare_data_dictionary_from_json(json_file: str):
    return json.load(open(json_file, "r"))
