"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/config/__init__.py
 

Description:
    

"""
from inspy_logger.config.dirs import DEFAULT_LOG_FILE_PATH

import logging

logging.addLevelName(5, 'INTERNAL')
