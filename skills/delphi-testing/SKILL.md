---
name: delphi-testing
description: Use when writing or changing tests for a Delphi XE7 application, when a change needs a test before it can be trusted, or when legacy code without tests must be changed safely. Covers which kind of test to write, DUnitX and DUnit, fakes for devices and the cloud, characterization (golden master) tests, captured-frame fixtures and leak detection. Triggers on "test", "unit test", "DUnitX", "DUnit", "fake", "mock", "fixture", "regression", "golden master", "characterization test", "no tests", "memory leak in tests".
---

# Testing a Delphi XE7 application

A change is done when a test proves it. The agent writes the test, runs it (`delphi-build-test`) and shows
the result; "it should work" is not a result.

## Which test

| Level | What it proves | Speed | Where it runs |
|-------|----------------|-------|---------------|
| **Unit** | one unit's logic: encoding, validation, parameter rules, state machines | ms | every build, CI |
| **Characterization** | legacy code still does exactly what it did before a refactoring | ms | every build, CI |
| **Protocol** | frames, CRC, firmware-version capabilities against captured traffic and a fake device | ms | every build, CI |
| **UI smoke** | the application starts, the main flows can be clicked through | s–min | CI on an interactive runner, see `vcl-ui-testing` |
| **Hardware in the loop** | the real device accepts what we send | min | nightly or before release, on a stand |

Most tests belong to the first three rows. A UI test that checks what a unit test could check is slow and fragile.

## DUnitX

```delphi
unit Config.Encoder.Tests;

interface

uses
  DUnitX.TestFramework,
  Config.Encoder;

type
  [TestFixture]
  TConfigEncoderTests = class
  public
    [Test]
    [TestCase('zero', '0,00')]
    [TestCase('max', '255,FF')]
    procedure EncodesByte(const AValue: Integer; const AHex: string);

    [Test]
    procedure RejectsValueOutOfRange;
  end;

implementation

procedure TConfigEncoderTests.EncodesByte(const AValue: Integer; const AHex: string);
begin
  Assert.AreEqual(AHex, BytesToHex(EncodeByteParam(AValue)));
end;

procedure TConfigEncoderTests.RejectsValueOutOfRange;
begin
  Assert.WillRaise(
    procedure
    begin
      EncodeByteParam(256);
    end,
    EConfigError);
end;

initialization
  TDUnitX.RegisterTestFixture(TConfigEncoderTests);

end.
```

- DUnitX is bundled with RAD Studio only from XE8. On XE7 it comes from its GitHub repository; pin the
  version the team uses and check that it still compiles with XE7.
- DUnit ships with XE7. In a project that already uses DUnit, write DUnit tests; do not mix frameworks in one test project.
- One behaviour per test, named after the behaviour. Arrange, act, assert, nothing else.

## Fakes, not hardware

Code that talks to a device or the cloud takes an interface, so a test can pass a fake:

```delphi
type
  IDevicePort = interface
    ['{8B0E1F3A-4C2D-4E5F-9A1B-2C3D4E5F6A7B}']
    procedure Send(const AFrame: TBytes);
    function TryReadFrame(out AFrame: TBytes; const ATimeoutMs: Cardinal): Boolean;
  end;
```

- **Hand-written fakes** first: a `TFakeDevicePort` that answers from a queue of captured frames and records
  what was sent. Readable, debuggable, no framework.
- A mocking library (Delphi-Mocks) only when hand-written fakes multiply. It relies on `TVirtualInterface`, which XE7 has.
- Generate a new GUID for every interface. Never copy one.
- Time is a dependency too: inject a clock instead of calling `Now` in logic that has timeouts or schedules.

## Characterization tests — before touching legacy code

Legacy code without tests is changed in this order:

1. Find the seam: the function or class whose output the change could affect.
2. Feed it many realistic inputs (real configurations, captured frames, edge values) and **record the current
   output** as fixture files. Do not judge whether the output is right; record what it is.
3. Commit the test that compares against the fixtures. It is green by definition.
4. Make the change. Every fixture that changes is either intended (update it in the same MR and say why)
   or a regression.

This is how an agent refactors code it does not fully understand without breaking it.

## Fixtures

- Captured frames as hex text files next to the tests, one frame per line, with a comment saying which
  device and firmware version produced them.
- Never put customer data or real installer codes into fixtures. Anonymise before committing.

## Memory leaks

In the test project `.dpr`:

```delphi
ReportMemoryLeaksOnShutdown := True;
```

A test run that reports a leak is a failed run. For a stack trace of where the leaked object was allocated,
use FastMM4 in FullDebugMode in the test build.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
