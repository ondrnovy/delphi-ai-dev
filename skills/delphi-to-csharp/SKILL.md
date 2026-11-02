---
name: delphi-to-csharp
description: Use when porting logic from a Delphi desktop application to C# / .NET (for example a web successor of a desktop tool), or when both implementations must behave identically during a transition period. Covers type and idiom mapping, the traps that change behaviour silently, and how to prove equivalence with shared test vectors. Triggers on "port to C#", "migrate from Delphi", "rewrite in .NET", "same behaviour as the Delphi version", "C# equivalent".
---

# Porting Delphi logic to C#

## Strategy

1. **Port logic, not screens.** Protocol, configuration model, validation and rules move; the UI is redesigned for the new platform.
2. **Pin the Delphi behaviour first.** Characterisation tests in Delphi produce **test vectors**: inputs and
   expected outputs (encoded frames, decoded configurations, validation results) stored as files.
3. **Run the same vectors against the C# code.** Equivalence is proven by data, not by reading code side by side.
4. **Port module by module**, smallest dependency first, and keep both implementations green on the same vectors.

## Type mapping

| Delphi | C# | Watch out |
|--------|----|-----------|
| `Integer` / `Cardinal` | `int` / `uint` | |
| `Int64` / `UInt64` | `long` / `ulong` | |
| `Byte`, `Word`, `LongWord` | `byte`, `ushort`, `uint` | |
| `Currency` | `decimal` | Currency is fixed 4 decimals |
| `Double` / `Extended` | `double` | `Extended` is 80-bit on Win32; results can differ in the last digits |
| `TDateTime` | `DateTime` via `DateTime.FromOADate` / `ToOADate` | same epoch (1899-12-30); time zones are not part of `TDateTime` |
| `string` (1-based) | `string` (0-based) | every index and `Copy(s, i, n)` call shifts by one |
| `TBytes` | `byte[]` / `ReadOnlySpan<byte>` | |
| set of enum | `[Flags] enum` | |
| `record` | `struct` or `record struct` | value semantics match; check copies in loops |
| `TObjectList<T>` | `List<T>` | ownership disappears with the GC; `IDisposable` for real resources |
| interface (refcounted) | interface (GC) | deterministic destruction is gone; use `using` where it mattered |
| `TThread` + `Synchronize` | `Task` / `async` | in a web app there is no UI thread to synchronise with |

## Behaviour that changes silently

- **Integer overflow:** Delphi without `{$Q+}` wraps; C# wraps too unless `checked`. Match the original, and say which it is.
- **`div` and `mod` with negative numbers** behave like C# `/` and `%` on integers (truncation). Keep a test anyway.
- **Rounding:** Delphi `Round` uses banker's rounding; C# `Math.Round` defaults to the same (`ToEven`). `Trunc` → `Math.Truncate`.
- **Byte order:** use `BinaryPrimitives.ReadUInt16BigEndian` etc. explicitly, never `BitConverter` without checking `IsLittleEndian`.
- **String comparison:** Delphi `SameText` vs `string.Equals(…, StringComparison.OrdinalIgnoreCase)` — choose the comparison explicitly.
- **Default values:** Delphi zeroes object fields; C# does too, but local variables in Delphi are not initialised.

## Done means

- All shared test vectors pass in both implementations.
- Differences that are intended are listed in the merge request, with the reason.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
