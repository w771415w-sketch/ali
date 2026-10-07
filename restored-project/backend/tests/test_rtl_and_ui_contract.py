# -*- coding: utf-8 -*-
"""Deterministic tests for the production UI direction contract."""
from __future__ import annotations
from config.i18n import normalize_language, is_rtl, tr
from ui.rtl import start_side, end_side, anchor_start, justify


def test_arabic_is_rtl():
    assert normalize_language("ar-SA") == "ar"
    assert is_rtl("ar") is True
    assert start_side("ar") == "right"
    assert end_side("ar") == "left"
    assert anchor_start("ar") == "e"
    assert justify("ar") == "right"
    assert tr("send", "ar") == "إرسال"


def test_english_is_ltr():
    assert normalize_language("en-US") == "en"
    assert is_rtl("en") is False
    assert start_side("en") == "left"
    assert end_side("en") == "right"
    assert anchor_start("en") == "w"
    assert justify("en") == "left"
    assert tr("send", "en") == "Send"


def test_unknown_language_defaults_to_english():
    assert normalize_language("fr") == "en"
