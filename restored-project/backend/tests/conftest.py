# -*- coding: utf-8 -*-
"""Pytest bootstrap + deterministic headless UI handling."""
import os, sys
# Force TCL/TK to use the bundled runtime tcl before any tkinter import.
_THIS = os.path.dirname(os.path.abspath(__file__))
_RUNTIME_PY = os.path.normpath(os.path.join(_THIS, "..", "..", "runtime", "python"))
os.environ.setdefault("TCL_LIBRARY", os.path.join(_RUNTIME_PY, "tcl", "tcl8.6"))
os.environ.setdefault("TK_LIBRARY", os.path.join(_RUNTIME_PY, "tcl", "tk8.6"))
os.environ.setdefault("TCLLIBPATH", os.path.join(_RUNTIME_PY, "tcl"))

from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))


def pytest_collection_modifyitems(config, items):
    # The build environment used for CI/unit verification has no X/Windows desktop.
    # Real UI tests remain enabled on a machine with a display (Windows desktop).
    if os.name != 'nt' and os.environ.get('ALI_GUI_TESTS') != '1':
        mark=pytest.mark.skip(reason='Desktop GUI display unavailable in headless environment')
        for item in items:
            if item.fspath.basename in {'test_professional_ai.py','test_ui_integration.py'}:
                item.add_marker(mark)
