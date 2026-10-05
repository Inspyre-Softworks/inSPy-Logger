import json
import subprocess
import sys


def test_import_does_not_replace_process_log_record_factory():
    script = """
import json
import logging
before = logging.getLogRecordFactory()
import inspy_logger
after = logging.getLogRecordFactory()
print(json.dumps({"same": before is after}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout.strip().splitlines()[-1]) == {"same": True}


def test_optional_modules_do_not_parse_arguments_or_write_to_cwd(tmp_path):
    script = """
import json
from pathlib import Path
import sys
sys.argv = ["program", "--not-a-real-option"]
import inspy_logger.Scripts.main
import inspy_logger.tool.config.arguments
import inspy_logger.helpers.network
print(json.dumps({"files": [path.name for path in Path.cwd().iterdir()]}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    output = json.loads(result.stdout.strip().splitlines()[-1])
    assert output == {"files": []}
