import json
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict

import requests

from bio3dbeacons.config.config import get_config, get_config_keys

LOG = logging.getLogger(__name__)


def prepare_data_dictionary(cif_block: Any, config_section: str) -> Dict:
    """Returns a Python object from a CIF block (read by GEMMI) from a config

    Args:
        cif_block (Any): CIF bloc for the data
        config_section (str): Section in conf.ini where the mapping is provided

    Returns:
        Dict: Python object which maps the configuration from CIF block.
    """

    data_dict: Dict = dict()

    for key in get_config_keys(config_section):
        mapping = get_config(config_section, key)
        data_dict[key] = cif_block.find_value(mapping)

    return data_dict


def get_uniprot_xml(accession: str) -> ET.Element:
    """Gets UniProt XML

    Args:
        accession (str): A UniProt accession

    Returns:
        ET.Element: An XML element
    """

    uniprot_xml_url = get_config("cli", "UNIPROT_XML_URL")

    try:
        response = requests.get(f"{uniprot_xml_url}/{accession}.xml")
        LOG.info(f"Received {uniprot_xml_url}/{accession}.xml")
        return ET.fromstring(response.content)
    except Exception as e:
        LOG.error(f"Error in parsing UniProt XML for {accession}!")
        LOG.debug(e)

    return None


def prepare_data_dictionary_from_json(json_file: str):
    """Gets a Python object from a JSON file

    Args:
        json_file (str): Path to the JSON file

    Returns:
        [Any]: A Python object
    """
    return json.load(open(json_file, "r"))
