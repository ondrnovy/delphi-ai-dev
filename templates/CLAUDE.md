# CLAUDE.md — project template

Copy to the root of the Delphi repository and fill in the placeholders. The agent reads this file at the
start of every session; the skills in `skills/` hold the general knowledge, this file holds the project's.

## Target

- Delphi **XE7** (CompilerVersion 28.0), VCL, Win32.
- RTL/VCL source to verify APIs against: `C:\Program Files (x86)\Embarcadero\Studio\15.0\source`
- Third-party components and where their source is: `<list>`

## Build and test

- Build: `.claude\skills\delphi-build-test\scripts\build.bat <Main.dproj> Debug Win32`
- Tests: `.claude\skills\delphi-build-test\scripts\test.bat <Tests.dproj> Win32`
- UI smoke tests: `python -m pytest <ui-tests folder>` with `APP_EXE`, `APP_TITLE_RE` and `APP_ARGS` set
- Fake device: start the application with `<--fake-device or the project's switch>`
- A change is done when build and tests pass with no new warnings; a change to a form is also clicked through.

## Map of the code

- `<folder>` — device communication and protocol
- `<folder>` — configuration model (devices, parameters, firmware capabilities)
- `<folder>` — forms
- `<folder>` — tests and captured frame fixtures

## Conventions

- Naming, field prefixes, unit naming: `<house style>`
- Forms are stored as text DFM.
- Logic does not go into form units; forms call into plain units.
- Errors are reported to `<logging / Sentry setup>`.

## Working rules for the agent

- Use the `delphi-xe7` skill for any Delphi code; nothing newer than XE7.
- State the layer and the test in the plan before writing code (`delphi-architecture`).
- Build and test after every change (`delphi-build-test`, `delphi-testing`).
- Check UI changes in the running application against the fake device (`vcl-ui-testing`).
- Never connect to real devices or the production cloud.
- Device I/O never runs on the main thread (`vcl-threading`).
- Every protocol change states which firmware versions it was checked against (`binary-protocol`).
- When a mistake is caught, propose a rule (`skill-maintenance`).
- Never commit secrets, keys or customer data.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
