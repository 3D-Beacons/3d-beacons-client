import os
from configparser import ConfigParser
from functools import lru_cache

CONF_FILE = "conf.ini"


@lru_cache(maxsize=None)
def read_config_file(filename):  # pragma: no cover
    config = ConfigParser()
    config.optionxform = str
    config_filepath = os.path.join(os.path.dirname(__file__), filename)
    config.read(config_filepath)
    return config


@lru_cache(maxsize=None)
def get_config_keys(section):  # pragma: no cover
    config_file = CONF_FILE
    config = read_config_file(config_file)

    return config[section].keys()


@lru_cache(maxsize=None)
def get_config(section, key):  # pragma: no cover
    config_file = CONF_FILE
    config = read_config_file(config_file)

    return config[section][key]


@lru_cache(maxsize=None)
def load_config_file():  # pragma: no cover
    config_file = CONF_FILE
    read_config_file(config_file)
    return
