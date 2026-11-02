---
name: delphi-architecture
description: Use when deciding where new code goes in a large Delphi VCL application, when logic sits in form event handlers and needs to move out, when adding a new device type, protocol version or cloud call, or when planning a refactoring of legacy code. Defines the layers, the dependency direction, the seams that make testing possible and the order of safe refactoring steps. Triggers on "architecture", "where should this go", "refactor", "OnClick handler", "god form", "untestable", "legacy", "new device type", "layer", "dependency", "seam".
---

# Architecture of a VCL application that configures hardware

## Layers

```
Forms (VCL)            ── show state, forward user intent; no protocol, no rules
   │
Application services   ── use cases: read configuration, write configuration, upload firmware
   │
Domain model           ── devices, parameters, validation rules, firmware capabilities
   │
Protocol               ── frames, encoding, CRC, session state machine
   │
Transport              ── USB / serial / cloud behind one interface (IDevicePort)
```

- **Dependencies point down only.** The domain model does not know a form exists; the protocol does not know
  the domain's validation rules.
- **Every layer below the forms is testable without a window and without hardware.** If a test needs a form
  or a device, the code is in the wrong layer.
- **The transport is chosen in one place** (the composition root, usually the `.dpr` or the main form's
  creation). That is where `--fake-device` selects `TFakeDevicePort` for UI tests and demos.

## Where new code goes

| Change | Layer | Test |
|--------|-------|------|
| New parameter or validation rule | domain model | unit |
| New frame type or field | protocol | protocol test with captured frames |
| New firmware version with different capabilities | domain model (capability table) + protocol | both, one per supported version |
| New device type | domain model + protocol, form last | unit + protocol + one UI smoke flow |
| New cloud call | transport / service behind an interface | unit with a fake |
| New dialog | form + service call | UI smoke flow if it is a main path |

Data that describes devices (parameter lists, ranges, capability tables) is better as data than as code:
a table the agent and the reviewer can read in one place, with a test that every entry round-trips.

## Getting logic out of forms — safe order

A typical legacy `Button1Click` validates input, builds a frame, talks to the device and updates labels.
Move it out in small, separately merged steps:

1. **Characterization test first** (`delphi-testing`): record what the current code produces for realistic inputs.
2. **Extract the pure part** (validation, encoding) into a plain unit as functions. The handler calls them.
   Behaviour identical, tests green.
3. **Introduce the interface** for the device or cloud and pass it in instead of creating it inside the handler.
4. **Extract the use case** into a service class. The handler shrinks to reading controls, calling the
   service, showing the result.
5. **Move the blocking call off the main thread** (`vcl-threading`).

Each step builds, passes the tests and could be released on its own. Never combine a refactoring with a
behaviour change in one merge request; the reviewer cannot tell which diff line is which.

## Rules for the agent

- Propose the layer and the test **before** writing the code, in the plan.
- Do not introduce a framework (DI container, MVVM library) into a legacy codebase as a side effect of a
  task. That is a team decision.
- Follow the existing structure even where it is not ideal; improve it in its own refactoring MR.
- When code that would be shared with a C# implementation is written, keep it in the domain or protocol
  layer with test vectors (`delphi-to-csharp`).

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
