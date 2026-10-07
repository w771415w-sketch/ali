# -*- coding: utf-8 -*-
import os, pytest

def test_ui_import():
    if os.name != 'nt' and os.environ.get('ALI_GUI_TESTS') != '1':
        pytest.skip('Tk display is unavailable in this headless test environment')
    import ali_agent  # noqa: F401
