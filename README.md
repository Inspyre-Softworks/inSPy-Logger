# InspyLogger

InspyLogger is a colorful, hierarchical logging library for Python CLI
applications. It keeps the standard library's logging semantics while adding
named singleton devices, child loggers, Rich console output, file output, and
one-time warnings.

Version 3.2.2 supports Python 3.10 and newer.

## Installation

```console
python -m pip install inspy-logger
```

## Quick start

```python
from inspy_logger import InspyLogger

log = InspyLogger(
    "my-app",
    console_level="info",
    file_level="debug",
    file_name="my-app.log",
)

log.debug("Written to the file, but hidden from the console")
log.info("Started %s", "successfully")
log.warning("Something may need attention")
```

`InspyLogger(name, ...)` returns the same logger device for repeated uses of a
name. Log methods accept the same positional formatting arguments as
`logging.Logger`.

## Console-only logging

```python
log = InspyLogger(
    "console-app",
    console_level="warning",
    no_file_logging=True,
)
```

With `no_file_logging=True`, no file handler is installed and no log file is
created.

## Child loggers

```python
database_log = log.get_child("database")
query_log = log.get_child("database.query")

database_log.info("Connected")
query_log.debug("Executing %s", statement)
```

Child retrieval is stable: requesting the same child name returns the same
device and does not add duplicate handlers.

## Logging-enabled classes

```python
from inspy_logger import Loggable


class Worker(Loggable):
    def run(self):
        self.method_logger.info("Worker started")


worker = Worker(parent_log_device=log)
worker.run()
```

`method_logger` resolves to a child named for the calling method. It remains a
descriptor, so each method gets the correct child rather than an instance
attribute captured during initialization.

## Levels and handlers

Console and file levels are independent. The wrapped `logging.Logger` is kept
at the lowest enabled handler level, so a configuration such as console
`WARNING` plus file `DEBUG` works as expected.

The supported named levels are `internal`, `debug`, `info`, `warning`, `error`,
`critical`, and `fatal`. Integer levels from `logging` are also accepted.

## Compatibility

The v2 `start()` method remains available as a deprecated compatibility shim.
New code should use the logger returned by `InspyLogger(...)` directly.

## Development

```console
poetry install --with dev
poetry run pytest
poetry build
```

The contract suite covers identity, hierarchy, handler configuration,
independent levels, caller attribution, `Loggable`, and `warn_once()`.

## License

InspyLogger is distributed under the MIT License. See `LICENSE.md`.
