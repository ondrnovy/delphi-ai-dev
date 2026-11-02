---
name: delphi-build-test
description: Use after every change to Delphi code, to build the project from the command line and run the unit tests, and to read compiler errors and test failures. Closes the loop so the agent fixes its own compile errors before a human sees the change. Triggers on "build", "compile", "msbuild", "dcc32", "run tests", "DUnitX", "DUnit", "it does not compile", "E2003", "W1035".
---

# Build and test Delphi XE7 from the command line

An agent that cannot build guesses. An agent that builds after every change fixes its own mistakes.
**Never report a change as done until it builds and the tests pass.**

## Build

```bat
scripts\build.bat <Project.dproj> <Debug|Release> <Win32|Win64>
```

The script calls `rsvars.bat` (sets up the Delphi environment) and then `msbuild`, exactly like the IDE
and like CI. Default XE7 location of `rsvars.bat`:

```
C:\Program Files (x86)\Embarcadero\Studio\15.0\bin\rsvars.bat
```

Override with the `BDS_RSVARS` environment variable when the install lives elsewhere.

## Read the compiler output

`msbuild` prints compiler messages in this shape:

```
Panel.Session.pas(42): error E2003: Undeclared identifier: 'ForceQueue'
Panel.Config.pas(118): warning W1035: Return value of function 'TConfig.Load' might be undefined
```

- **Errors:** fix, rebuild, repeat. Do not stop at the first green build if you added warnings.
- **Warnings that are bugs:** `W1035` (undefined Result), `W1036` (variable might not be initialized),
  `W1010` (method hides virtual method of base type). Treat them as errors in code you touch.
- **An identifier the compiler does not know** usually means a newer-Delphi API. Check the `delphi-xe7` skill
  table and the 15.0 source tree before trying another name.

## Tests

```bat
scripts\test.bat <Tests.dproj> <Win32|Win64>
```

- Builds the test project and runs it. A failing test must make the exit code non-zero, and that is not
  automatic: the test project has to be a **console** runner that sets the exit code.
- **DUnitX** (open source, added to the project separately) — in the test `.dpr`:

  ```delphi
  Runner.AddLogger(TDUnitXXMLJUnitFileLogger.Create(TDUnitX.Options.XMLOutputFile));  // DUnitX.Loggers.XML.JUnit
  Results := Runner.Execute;
  if not Results.AllPassed then
    System.ExitCode := EXIT_ERRORS;
  ```

  GitLab shows test results on the merge request only from **JUnit** XML (`artifacts:reports:junit`).
- **DUnit** (ships with XE7) — the default wizard project is a GUI runner that opens a window and hangs CI.
  Define `CONSOLE_TESTRUNNER` and call `TextTestRunner.RunRegisteredTests(rxbHaltOnFailures)`.
- If `test.bat` cannot find the executable (custom `DCC_ExeOutput`), set `TEST_EXE`.
- Win64 builds only when the platform is enabled in the `.dproj`.
- Logic that lives inside a form should not be unit tested there (slow, fragile). When a change touches
  such logic, move it to a plain unit first, cover it with a test, then change it (`delphi-architecture`).
- A new unit must be added to the `.dpr` `uses` and the `.dproj`; a file that only exists on disk is not built.
- What to test and how: `delphi-testing`. UI checks in the running application: `vcl-ui-testing`.

## CI (GitLab)

The same two commands run in the pipeline on a Windows runner with RAD Studio XE7 and every third-party
component the project uses installed. What the agent runs locally and what CI runs must be identical.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
