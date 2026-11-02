---
name: vcl-ui-testing
description: Use when a change to a Delphi VCL application has to be checked in the running UI — clicking through a form, verifying that a dialog opens, that a value appears, that a flow completes — or when writing automated UI smoke tests for it. Drives the real application through Windows UI Automation with pywinauto, inspects the control tree, takes screenshots. Triggers on "UI test", "click through", "proklikat", "smoke test", "UI Automation", "UIA", "pywinauto", "screenshot of the app", "does the form work", "end-to-end".
---

# Driving and testing the VCL UI

The agent cannot see the screen the way a person does, but Windows exposes every window and most controls
through **UI Automation (UIA)**: a tree of elements with a type, a name, a state and actions (click, set
text, select). pywinauto reads and drives that tree from Python. The agent writes a short script, runs it,
reads the printed tree or the screenshot, and knows whether the change works in the real application.

## What UIA sees in a VCL application

| Control | Visible to UIA | Notes |
|---------|----------------|-------|
| `TForm`, `TButton`, `TEdit`, `TMemo`, `TCheckBox`, `TRadioButton`, `TComboBox`, `TListBox` | yes | wrap standard Windows controls; class name is the Delphi class (`TButton`, `TEdit`) |
| `TListView`, `TTreeView`, `TPageControl`, `TStatusBar`, `TProgressBar` | yes | wrap Windows common controls; items and tabs are reachable |
| `TPanel`, `TGroupBox`, `TScrollBox` | yes, as containers | useful to scope a search |
| `TLabel`, `TSpeedButton`, `TImage`, `TShape`, `TBevel` | **no** | `TGraphicControl` has no window handle, so UIA has nothing to find |
| `TStringGrid`, `TDrawGrid`, custom-painted controls | the control only, **not its cells** | needs a custom UIA/MSAA provider, a screenshot, or a test hook |
| Third-party suites (DevExpress, TMS…) | depends on the suite and its version | inspect before planning tests around them |

Consequences:

- An edit box has no caption, and its `TLabel` is invisible. Locate it by its container and order
  (`found_index`), and keep that stable, or give the container a meaningful caption.
- A toolbar of `TSpeedButton`s cannot be clicked through UIA. Use the menu or keyboard shortcut for the same
  action, or switch that toolbar to `TToolBar` / `TButton`.
- Verify the tree before writing a test: `scripts/dump_tree.py` prints it. Never guess control names.

## Explore the running application

```bat
pip install pywinauto pillow
python scripts\dump_tree.py --exe "C:\build\App.exe --fake-device" --title-re "Configurator.*"
python scripts\dump_tree.py --title-re "Configurator.*" --screenshot main.png
```

The first form starts the application, the second attaches to one that is already running. The output lists
every element with the exact identifiers pywinauto accepts. Microsoft's Accessibility Insights for Windows
shows the same tree interactively.

## Write a smoke test

`scripts/conftest.py` and `scripts/smoke_test.py` are a pytest template: start the application against a
**fake device**, open the main form, run one flow, assert on what UIA can read, and save a screenshot on failure.

Rules:

- **Never against real hardware and never against production cloud.** The application needs a switch
  (command-line parameter or config) that selects a fake transport. See `delphi-architecture`.
- Wait for state, never `sleep`: `window.wait("visible enabled", timeout=…)`, `wait_until_passes`.
- Prefer `invoke()` / `set_edit_text()` (UIA actions) over `click_input()` / `type_keys()` (real mouse and
  keyboard). Real input breaks when another window takes focus.
- Assert on values UIA reads (edit text, check state, list items, status bar text), not on pixels.
  Screenshots are evidence for a human, not assertions.
- One flow per test, short. The detailed logic is covered by unit tests (`delphi-testing`).

## In CI

- UI tests need an **interactive desktop session**. A GitLab runner installed as a Windows service runs in
  session 0 without a desktop, and UI tests fail there. Run a separate runner in a logged-in user session
  (auto-logon on a dedicated VM), with the screen lock and screensaver off and a fixed resolution.
- Tag that runner (e.g. `windows-ui`) and run UI tests in their own stage after unit tests, so a broken
  build fails fast.
- Store screenshots and the pytest JUnit report (`--junitxml`) as job artifacts.

## Commercial alternative

TestComplete (SmartBear) records and replays VCL UI and has deeper Delphi support, including some
non-windowed controls when the application is built with its open-application units. Worth it when the team
already owns a licence; pywinauto is enough for smoke tests and for the agent's own checks.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
