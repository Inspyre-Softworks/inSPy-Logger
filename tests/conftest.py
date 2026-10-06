import logging

import pytest

from inspy_logger import Logger


@pytest.fixture(autouse=True)
def isolate_loggers():
    existing_names = set(Logger.instances)
    yield

    for name in set(Logger.instances) - existing_names:
        logger = Logger.instances.pop(name)
        for handler in list(logger.logger.handlers):
            logger.logger.removeHandler(handler)
            handler.close()
        logging.Logger.manager.loggerDict.pop(name, None)
