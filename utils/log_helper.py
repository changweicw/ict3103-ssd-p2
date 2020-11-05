import logging
from utils.appConfig import DefaultConfig
import platform
import socket

def prepareLogger(name_origin,filename,formatter):
    logger = logging.getLogger(name_origin)
    fh = logging.FileHandler(DefaultConfig.LOGGING_FOLDER+'/'+filename)
    sh = logging.StreamHandler()
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)
    return logger