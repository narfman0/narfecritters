from configparser import ConfigParser
import logging

LOGGER = logging.getLogger(__name__)
config = ConfigParser()
result = config.read("config.ini")
if not result:
    LOGGER.warning("Failed to read config.ini! Using sample.")
    config.read("config.ini.sample")

DEFAULT_DOMAIN = "app"


def get(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.get(domain, name, fallback=fallback)


def get_boolean(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.getboolean(domain, name, fallback=fallback)


def get_int(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.getint(domain, name, fallback=fallback)


def get_float(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.getfloat(domain, name, fallback=fallback)


def get_config_region(name, domain=DEFAULT_DOMAIN, fallback=None):
    """Parse a region str from ini"""
    return get_list(name, domain=domain, fallback=fallback)


def get_list(name, domain=DEFAULT_DOMAIN, fallback=None):
    """Parse a region str from ini"""
    list_str = config.get(domain, name, fallback=fallback)
    if list_str:
        return list(map(int, list_str.split(",")))
    return None


def set(name, value, domain=DEFAULT_DOMAIN):
    return config.set(domain, name, value)
