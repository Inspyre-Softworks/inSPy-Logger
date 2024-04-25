"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/common/meta/helpers/__init__.py
 

Description:
    

"""
from typing import List
from inspy_logger.common.meta.helpers.data_classes import ConstantData


def import_constants(module: str) -> List[ConstantData]:
    """
    Import constants from a module.

    This function will import constants from a module and add them to the current module.

    Parameters:
        module (str):
            The module to import the constants from.

    """
    return [
        ConstantData(name, value)
        for name, value in vars(module).items()
        if not name.startswith('__') and not callable(value)
    ]
