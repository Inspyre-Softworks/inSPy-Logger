"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/common/meta/helpers/data_classes.py
 

Description:
    

"""
from dataclasses import dataclass
from typing import Any, List
from datetime import datetime


@dataclass
class Release:
    """
    The release dataclass.

    Attributes:
        version (str):
            The version of the release.
        upload_time (datetime):
            The upload time of the release.
        locations (List[str]):
            The locations of the release.
    """
    version: str
    upload_time: datetime
    locations: List[str]


@dataclass
class ConstantData:
    name: str
    value: Any
