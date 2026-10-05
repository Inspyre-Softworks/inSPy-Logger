from inspy_logger import Loggable

from log_engine import APP_LOGGER


MOD_LOGGER = APP_LOGGER.get_child('app')


class App(Loggable):
    def __init__(self) -> None:
        super().__init__(parent_log_device=MOD_LOGGER)
        self.class_logger.debug('App initialized.')

    def run(self) -> None:
        log = self.method_logger

        log.debug('App is running.')
        log.info('App is doing something important.')
        log.warning('Example warning-level message.')
        log.error('Example error-level message.')

        print('Done! Check the console for log messages.')


def main() -> None:
    log = MOD_LOGGER.get_child('main')
    log.debug('Main function started.')

    app = App()
    app.run()


if __name__ == '__main__':
    main()
