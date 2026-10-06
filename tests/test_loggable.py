from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from inspy_logger import Loggable, Logger


def test_method_logger_descriptor_creates_and_reuses_method_child(tmp_path):
    parent = Logger(
        f"test-{uuid4()}",
        no_file_logging=True,
        file_path=tmp_path,
        announce_on_init=False,
    )

    class Service(Loggable):
        class_logger = None

        def run(self):
            return self.method_logger

    service = Service(parent)

    method_logger = service.run()
    same_method_logger = service.run()

    assert "method_logger" not in service.__dict__
    assert method_logger is same_method_logger
    assert method_logger.name == f"{parent.name}.Service.run"
    assert service.log_device.child_names == [method_logger.name]


def test_method_logger_can_be_accessed_outside_an_instance_method(tmp_path):
    parent = Logger(
        f"test-{uuid4()}",
        no_file_logging=True,
        file_path=tmp_path,
        announce_on_init=False,
    )

    class Service(Loggable):
        class_logger = None

    service = Service(parent)

    assert service.method_logger is service.log_device.logger


def test_concurrent_method_logger_access_reuses_one_child(tmp_path):
    parent = Logger(
        f"test-{uuid4()}",
        no_file_logging=True,
        file_path=tmp_path,
        announce_on_init=False,
    )

    class Service(Loggable):
        class_logger = None

        def run(self):
            return self.method_logger

    service = Service(parent)

    with ThreadPoolExecutor(max_workers=16) as executor:
        loggers = list(executor.map(lambda _: service.run(), range(64)))

    assert all(logger is loggers[0] for logger in loggers)
    assert service.log_device.child_names == [loggers[0].name]
