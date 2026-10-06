import __main__
import sys

from inspy_logger.utils import check_if_interactive


def test_script_context_is_not_interactive(monkeypatch):
    monkeypatch.delattr(sys, "ps1", raising=False)
    monkeypatch.setattr(sys, "modules", dict(sys.modules))
    sys.modules.pop("IPython", None)
    sys.modules.pop("ipykernel", None)
    monkeypatch.setattr(sys, "flags", _Flags(interactive=False))
    monkeypatch.setattr(__main__, "__file__", "script.py", raising=False)

    assert check_if_interactive() is False


def test_ipython_context_is_interactive(monkeypatch):
    monkeypatch.delattr(sys, "ps1", raising=False)
    monkeypatch.setattr(sys, "modules", {**sys.modules, "IPython": object()})

    assert check_if_interactive() is True


class _Flags:
    def __init__(self, interactive):
        self.interactive = interactive
