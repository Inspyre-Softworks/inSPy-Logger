import logging
from pathlib import Path
from uuid import uuid4

from rich.logging import RichHandler

from inspy_logger import Logger


def make_logger(tmp_path, **kwargs):
    options = {
        "name": f"test-{uuid4()}",
        "file_path": tmp_path,
        "file_name": "test.log",
        "announce_on_init": False,
    }
    options.update(kwargs)
    return Logger(**options)


def test_logger_is_singleton_by_name(tmp_path):
    name = f"test-{uuid4()}"
    first = make_logger(tmp_path, name=name)
    second = Logger(name)

    assert first is second


def test_child_retrieval_is_stable_and_registered(tmp_path):
    parent = make_logger(tmp_path, no_file_logging=True)

    child = parent.get_child("worker")
    same_child = parent.get_child("worker")

    assert same_child is child
    assert parent.children == [child]
    assert parent.child_names == [f"{parent.name}.worker"]
    assert child.parent is parent


def test_no_file_logging_installs_only_console_handler(tmp_path):
    logger = make_logger(tmp_path, no_file_logging=True)

    assert len(logger.logger.handlers) == 1
    assert isinstance(logger.logger.handlers[0], RichHandler)
    assert not any(
        isinstance(handler, logging.FileHandler)
        for handler in logger.logger.handlers
    )
    assert not logger.file_path.exists()


def test_no_file_logging_can_be_toggled_without_duplicate_handlers(tmp_path):
    logger = make_logger(tmp_path, no_file_logging=False)

    logger.no_file_logging = True
    assert not any(
        isinstance(handler, logging.FileHandler)
        for handler in logger.logger.handlers
    )

    logger.no_file_logging = False
    logger.no_file_logging = False
    assert sum(
        isinstance(handler, logging.FileHandler)
        for handler in logger.logger.handlers
    ) == 1


def test_handler_setup_is_idempotent(tmp_path):
    logger = make_logger(tmp_path)

    logger.set_up_handlers()

    assert len(logger.logger.handlers) == 2
    assert sum(
        isinstance(handler, RichHandler) for handler in logger.logger.handlers
    ) == 1
    assert sum(
        isinstance(handler, logging.FileHandler)
        for handler in logger.logger.handlers
    ) == 1


def test_file_can_accept_debug_when_console_requires_warning(tmp_path):
    logger = make_logger(
        tmp_path,
        console_level=logging.WARNING,
        file_level=logging.DEBUG,
    )

    logger.debug("file-only debug")
    for handler in logger.logger.handlers:
        handler.flush()

    assert logger.logger.level == logging.DEBUG
    assert "file-only debug" in logger.file_path.read_text(encoding="utf-8")


def test_level_changes_keep_logger_at_lowest_enabled_handler_level(tmp_path):
    logger = make_logger(
        tmp_path,
        console_level=logging.INFO,
        file_level=logging.WARNING,
    )

    logger.console_level = logging.ERROR
    assert logger.logger.level == logging.WARNING

    logger.file_level = logging.DEBUG
    assert logger.logger.level == logging.DEBUG


def test_is_enabled_for_is_a_callable_method(tmp_path):
    logger = make_logger(tmp_path, no_file_logging=True, console_level="warning")

    assert logger.isEnabledFor(logging.WARNING)
    assert not logger.isEnabledFor(logging.INFO)


def test_error_preserves_formatting_arguments_and_stack_attribution(tmp_path):
    logger = make_logger(tmp_path, no_file_logging=True, console_level="debug")
    records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record)

    logger.logger.addHandler(CaptureHandler())

    expected_line = _emit_error(logger)
    record = records[-1]

    assert record.getMessage() == "failed item 7"
    assert Path(record.pathname) == Path(__file__)
    assert record.lineno == expected_line


def _emit_error(logger):
    expected_line = __import__("inspect").currentframe().f_lineno + 1
    logger.error("failed %s %d", "item", 7)
    return expected_line


def test_warn_once_emits_each_message_once(tmp_path):
    logger = make_logger(tmp_path, no_file_logging=True)
    records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record)

    logger.logger.addHandler(CaptureHandler())
    logger.warn_once("careful")
    logger.warn_once("careful")

    assert [record.getMessage() for record in records] == ["careful"]
