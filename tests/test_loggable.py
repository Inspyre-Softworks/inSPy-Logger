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
