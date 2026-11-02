"""Shared pytest setup for UI smoke tests: starts the application against a fake device
and saves a screenshot of the main window when a test fails.

    set APP_EXE=C:\\build\\Win32\\Debug\\App.exe
    set APP_TITLE_RE=Configurator.*
    set APP_ARGS=--fake-device
    python -m pytest --junitxml=ui-report.xml
"""

import os
from pathlib import Path

import pytest
from pywinauto import Application

SCREENSHOT_DIR = Path(os.environ.get("UI_SCREENSHOT_DIR", "ui-screenshots"))
TIMEOUT = 30


def required_env(name):
    value = os.environ.get(name)
    if not value:
        pytest.fail(f"Environment variable {name} is not set, see conftest.py", pytrace=False)
    return value


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def main_window(request):
    app_exe = required_env("APP_EXE")
    title_re = required_env("APP_TITLE_RE")
    app_args = required_env("APP_ARGS")

    app = Application(backend="uia").start(f'"{app_exe}" {app_args}')
    window = app.window(title_re=title_re)
    window.wait("visible enabled", timeout=TIMEOUT)
    yield window

    call_report = getattr(request.node, "rep_call", None)
    if call_report is not None and call_report.failed:
        try:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            window.capture_as_image().save(SCREENSHOT_DIR / f"{request.node.name}.png")
        except Exception as error:
            print(f"screenshot failed: {error}")
    app.kill()
