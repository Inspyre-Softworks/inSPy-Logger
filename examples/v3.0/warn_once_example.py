from inspy_logger import InspyLogger, Loggable
from time import sleep


# Create a global logger instance with the name 'ExampleFile' and set its console logging level to 'info'.
MOD_LOGGER = InspyLogger('ExampleFile', console_level='info')


class MyClass(Loggable):
    def __init__(self):
        # Initialize the parent class (Loggable) with the global logger instance.
        super().__init__(MOD_LOGGER)

    def some_method(self, n_iters=10, warn_once=False):
        # Create a child logger for this method to use.
        log = self.create_child_logger()
        # Define a warning message to be logged.
        WARNING_MSG = 'This is a warning message!'

        for _ in range(n_iters):
            if warn_once:
                # Log the warning message only once if warn_once is True.
                log.warn_once(WARNING_MSG)
            else:
                # Log the warning message every iteration if warn_once is False.
                log.warning(WARNING_MSG)
            # Sleep for 0.3 seconds to simulate work being done.
            sleep(.3)

    def run(self, n_iters=10):
        # Call some_method without the one-time warning functionality.
        self.some_method(n_iters, False)
        print('Now with "warn_once"')
        # Sleep for 1 second before calling some_method again.
        sleep(1)
        # Call some_method with the one-time warning functionality.
        self.some_method(n_iters, True)


if __name__ == '__main__':
    # Create an instance of MyClass.
    my_class = MyClass()
    # Run the example by calling the run method.
    my_class.run()
