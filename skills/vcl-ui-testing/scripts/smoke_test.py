"""UI smoke test template for a Delphi VCL application, driven through UI Automation.

The main_window fixture (conftest.py) starts the application with --fake-device, so no hardware
and no cloud are touched. Replace the identifiers below with the ones dump_tree.py prints for
the real application.
"""

from pywinauto.timings import wait_until_passes

TIMEOUT = 30


def test_application_starts(main_window):
    assert main_window.is_visible()


def test_read_configuration_from_device(main_window):
    main_window.child_window(title="Read", control_type="Button").invoke()

    status = main_window.child_window(control_type="StatusBar")
    status.wait("visible", timeout=TIMEOUT)

    def configuration_loaded():
        assert "loaded" in status.window_text().lower()

    wait_until_passes(TIMEOUT, 0.5, configuration_loaded, AssertionError)
