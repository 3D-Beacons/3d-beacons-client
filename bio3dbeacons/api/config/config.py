import os
from configparser import ConfigParser


class Config:
    conf: ConfigParser = None

    @classmethod
    def get_config(cls) -> ConfigParser:
        if not cls.conf:
            config = ConfigParser()
            config_filepath = os.path.join(os.path.dirname(__file__), "conf.ini")
            config.read(config_filepath)
            cls.conf = config

        return cls.conf

    @classmethod
    def get_config_val(cls, section, key):
        if not cls.conf:
            cls.get_config()

        return cls.conf[section][key]
