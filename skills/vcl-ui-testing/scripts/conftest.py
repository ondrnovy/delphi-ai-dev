"""Shared pytest setup for UI smoke tests: starts the application against a fake device
and saves a screenshot of the main window when a test fails.

    set APP_EXE=C:\\build\\Win32\\Debug\\App.exe
    set APP_TITLE_RE=Configurator.*
    python -m pytest --junitxml=ui-report.xml
"""

import os
from pathlib import Path

import pytest
from pywinauto import Application

APP_EXE = os.environ["APP_EXE"]
APP_TITLE_RE = os.environ["APP_TITLE_RE"]
SCREENSHOT_DIR = Path(os.environ.get("UI_SCREENSHOT_DIR", "ui-screenshots"))
TIMEOUT = 30


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def main_window(request):
    app = Application(backend="uia").start(f'"{APP_EXE}" --fake-device')
    window = app.window(title_re=APP_TITLE_RE)
    window.wait("visible enabled", timeout=TIMEOUT)
    yield window
    call_report = getattr(request.node, "rep_call", None)
    if call_report is not None and call_report.failed:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        window.capture_as_image().save(SCREENSHOT_DIR / f"{request.node.name}.png")
    app.kill()
