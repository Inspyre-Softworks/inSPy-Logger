from inspy_logger import InspyLogger


APP_LOGGER = InspyLogger('ExampleApp', console_level='DEBUG', no_file_logging=True)

APP_LOGGER.debug(f'{APP_LOGGER.name} logger initialized...')

__all__ = [
    'APP_LOGGER'
]
