import logging
import logging.config

logging.config.fileConfig('logging.conf')

def get_logger(provider:str):
    return logging.getLogger(provider)