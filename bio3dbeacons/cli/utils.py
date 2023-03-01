import json
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict

import requests

from bio3dbeacons.config.config import get_config, get_config_keys

LOG = logging.getLogger(__name__)


def get_avg_plddt_from_pdb(pdb_path) -> float:
    """Returns the average pLDDT score from PDB file (from temp factor)

    Args:
        pdb_path: Path to PDB file

    """

    # ATOM      1  N   GLU A   1       0.599  -0.769  -0.906  1.00  6.85           N

    plddt_total = 0
    residue_count = 0
    current_res_seq_num = None
    with open(f"{pdb_path}", "r") as fh:
        for line in fh:
            if not line.startswith("ATOM"):
                continue
            res_seq_num = int(line[22:26].strip())
            temperature_factor = float(line[60:66].strip())

            if current_res_seq_num != res_seq_num:
                current_res_seq_num = res_seq_num
                plddt_total += temperature_factor
                residue_count += 1

    avg_plddt = "{:.2f}".format(plddt_total / residue_count)

    LOG.info(f"residues: {residue_count}")
    LOG.info(f"avg_plddt: {avg_plddt}")

    return avg_plddt


def prepare_data_dictionary_from_cif(cif_block: Any) -> Dict:
    """Returns a Python object from a CIF block (read by GEMMI)

    Args:
        cif_block (Any): CIF block for the data

    Returns:
        Dict: Python object which maps the configuration from CIF block.
    """
    data_dict = dict()
    
    data_dict["entryId"] = cif_block.find_value("_entry.id")
    data_dict["experimentalMethod"] = cif_block.find_value("_exptl.method")
    
    entity_dict = dict()
    entity_mmcif_cat = cif_block.find_mmcif_category("_entity.")
    
    for row in entity_mmcif_cat:
        entity_dict[row["id"]] = {
            "entityType": row["type"],
            "entityDescription": row["pdbx_description"] if "pdbx_description" in entity_mmcif_cat.tags else "",
            "chainIds": [],
        }
    for row in cif_block.find_mmcif_category("_struct_asym."):
        chain_id = row["id"]
        entity_dict[row["entity_id"]]["chainIds"].append(chain_id)
    
    
    data_dict["entities"] = list(entity_dict.values())

    return data_dict
    

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
