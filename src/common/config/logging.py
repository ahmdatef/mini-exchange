import logging.config

from pyaml_env import parse_config


def get_logging_config():
    """Specify logging configuration"""
    config = parse_config("common/log.yml")
    logging.config.dictConfig(config)
    return config
