---
name: delphi-review
description: Use when reviewing a Delphi change (own or someone else's) before it is merged, or when hunting a leak, an access violation or a freeze. A defect-first checklist ordered by what each finding costs at runtime. Triggers on "review", "code review", "merge request", "MR", "is this OK", "memory leak", "access violation", "AV", "freeze", "double free".
---

# Reviewing Delphi code

Inspired by `delphi-code-smells` in [danieleteti/delphi-ai-skills](https://github.com/danieleteti/delphi-ai-skills).

**Let the machine go first.** Build with warnings on (`delphi-build-test`) and run the tests with
`ReportMemoryLeaksOnShutdown := True`. Then review by hand, in this order. Report what each finding costs
at runtime; a style remark is not a finding.

## 1. Lifetime and ownership

- Every `Create`: who frees it, on every path, including the one that raises?
- `Create` inside `try` (AV in the `finally` when the constructor fails).
- Object freed manually but still referenced through an interface, or owned by a `TObjectList` / an Owner.
- Interface cycles (leak).

## 2. Exceptions

- `except` without `on`, empty handlers, exceptions turned into silent `False` results.
- `try/except` where `try/finally` was meant.
- Errors from the device or the cloud reach the user and the log (Sentry) with context.

## 3. Threads

- Any VCL access from `Execute`, `TTask.Run` or an anonymous thread.
- `WaitFor` on a thread that may `Synchronize`.
- Variables captured by reference in a queued anonymous method.
- Blocking reads without timeout.

## 4. Protocol and firmware compatibility

- Does the change behave correctly with the **oldest** firmware still supported?
- Version checks in the capability table, not scattered in the UI.
- Bounds and CRC checks before parsing.
- Firmware upload: is every state recoverable?

## 5. XE7 compatibility

- Nothing from the "Not in XE7" table of the `delphi-xe7` skill.

## 6. Everything else

`with`, long methods, magic numbers, naming. Only when 1–5 are clean.

## When the review finds an agent mistake

If the finding is a mistake an agent could make again, propose a rule for the right skill
(`skill-maintenance`). The review then improves the next change, not only this one.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
