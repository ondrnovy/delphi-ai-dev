---
name: delphi-xe7
description: Use when writing, reviewing or fixing Delphi / Object Pascal code that must compile with Delphi XE7 (CompilerVersion 28.0) — any .pas, .dpr or .dfm in a VCL desktop application. Covers what XE7 can and cannot compile, memory and lifetime, strings and binary data, exceptions, generics, RTTI and threading. Triggers on "Delphi", "XE7", "Object Pascal", ".pas", "VCL", "TThread", "memory leak", "access violation", "interface reference", "anonymous method", "compiler version".
---

# Delphi XE7 — language and RTL guide

Adapted from the `delphi` skill in [danieleteti/delphi-ai-skills](https://github.com/danieleteti/delphi-ai-skills)
(Apache-2.0), which targets Delphi 11 and newer. This version is cut down to what **Delphi XE7** compiles,
because the most common agent mistake on an old codebase is modern syntax that does not exist there.

---

## The target

| Release | `CompilerVersion` | Conditional | Studio folder |
|---------|------------------|-------------|---------------|
| **XE7** | **28.0** | `VER280` | `15.0` |

Source tree to verify against:

```
C:\Program Files (x86)\Embarcadero\Studio\15.0\source\rtl\sys\      System.pas, System.SysUtils.pas
C:\Program Files (x86)\Embarcadero\Studio\15.0\source\rtl\common\   System.Classes.pas, System.Generics.*, System.Rtti.pas, System.Threading.pas
C:\Program Files (x86)\Embarcadero\Studio\15.0\source\vcl\          Vcl.Forms.pas, Vcl.Controls.pas
```

Docwiki for this release: https://docwiki.embarcadero.com/RADStudio/XE7/en/ and
https://docwiki.embarcadero.com/Libraries/XE7/en/

## Verify, never guess

A plausible API that does not exist in XE7 costs a compile error and the reviewer's trust.

1. **Grep the 15.0 source tree** for the identifier. A declaration plus one real call site is the minimum.
2. **The project's own code** shows the house idiom. When editing an existing file, its conventions win.
3. **The XE7 docwiki** when the source is not available.
4. **If you cannot verify it, say so** and name the unit to check.

---

## Not in XE7 — never generate

| Feature | Introduced in | Write instead |
|---------|---------------|---------------|
| `var x := 0;` inline variables, `for var i := …` | 10.3 Rio | declare in the `var` section |
| inline `const` | 10.3 Rio | `const` section |
| custom managed records (`class operator Initialize`) | 10.4 Sydney | explicit `Init` / `Done` methods or a class |
| `[weak]` / `[unsafe]` on interfaces (desktop compiler) | 10.1 Berlin | a raw `Pointer` back-reference, documented |
| `TNoRefCountObject` | 11 Alexandria | `TSingletonImplementation` (`System.Generics.Defaults`) or own `_AddRef`/`_Release` returning `-1` |
| binary literals `%1010`, digit separators `1_000` | 11 Alexandria | hex `$0A`, plain digits |
| multiline string literals `'''` | 12 Athens | concatenation |
| `if … then … else` as an expression, `NameOf`, `is not` | 13 Florence | `IfThen` (`System.Math` / `System.StrUtils`) or a plain `if` |
| `THashSet<T>`, `TOrderedDictionary<K,V>` | 12 Athens | `TDictionary<T, Boolean>` |
| `TThread.ForceQueue` | 10.2 Tokyo | `TThread.Queue` |
| `System.JSON.Serializers` | 10.3 Rio | `System.JSON` DOM (`TJSONObject`) |

Verify before use (availability in XE7 not confirmed here): `System.Hash`, `System.NetEncoding`,
`TControl.RaiseOnNonMainThreadUsage`, `TStringList.Create(OwnsObjects)`.

## Available in XE7 — fine to use

- Generics, anonymous methods (2009), extended RTTI and attributes (2010)
- `TStringHelper` (`s.ToUpper`, `s.Chars[0]` — **0-based**) (XE3)
- `System.Threading`: `TTask`, `ITask`, `IFuture<T>`, `TParallel.&For` — **new in XE7**
- Dynamic array improvements — **new in XE7**: `[1, 2, 3]` initialisation, `+` concatenation, `Insert`, `Delete`
- `System.JSON` (XE6), `TThread.CreateAnonymousThread`, `TMonitor`, `TInterlocked`

Gate anything else explicitly:

```delphi
{$IF CompilerVersion >= 29.0}   // XE8 and later
  ...
{$ENDIF}
```

XE7 accepts both `{$ENDIF}` and `{$IFEND}` as the closer of `{$IF}`. Match what the project already uses.

---

## Memory and lifetime — the non-negotiables

Objects are **not** garbage collected and **not** reference counted. Interfaces are. Mixing them is where the bugs live.

```delphi
// 1. Create OUTSIDE the try.
List := TStringList.Create;
try
  ...
finally
  List.Free;
end;

// 2. An object reached through an interface is freed by its reference count.
//    Never Free it and never keep a second *object* reference to it.
Logger := TLogger.Create as ILogger;

// 3. Ownership belongs to the container.
People := TObjectList<TPerson>.Create;   // OwnsObjects = True: Remove/Delete/Clear free the item, Extract does not

// 4. A TComponent with an Owner is freed by the Owner.
Timer := TTimer.Create(Self);
```

Two interfaces referencing each other never reach zero: a leak. Break the cycle with a raw pointer (no `[weak]` in XE7).

`FreeAndNil` is for **fields** tested for `nil` later. On a local about to go out of scope it adds nothing.

## Strings and binary data

- `string` = `UnicodeString` (UTF-16), **1-based** on Win32/Win64. `TStringHelper` methods are **0-based**.
- **Binary data goes into `TBytes`, never into `string`.** A string conversion silently rewrites bytes.
- Convert explicitly: `TEncoding.UTF8.GetBytes`, `TEncoding.UTF8.GetString`.
- See the `binary-protocol` skill for framing, endianness and CRC.

## Exceptions

- `try … except on E: EMyError do … end;` — `except` without `on` catches everything, including what you cannot handle.
- Re-raise with a bare `raise;`. Never an empty `except end`.
- `try/except` and `try/finally` cannot share a block. Nest them.
- If a constructor raises, the destructor runs on the half-built object, so the destructor must be `nil`-safe.

## Common mistakes an agent makes in Delphi

| Wrong | Right |
|-------|-------|
| `s[0]` | `s[1]` or `s.Chars[0]` |
| `for i := 0 to List.Count do` | `to List.Count - 1` |
| `return X;` | `Result := X;` or `Exit(X)` |
| `==`, `!=`, `&&` | `=`, `<>`, `and` |
| `with Obj do` | a local variable |
| method without `override` that hides the ancestor | `override` / `reintroduce` / `overload` |
| `procedure Foo(AText: string)` | `const AText: string` |
| `Sleep` or blocking I/O on the main thread | a worker thread, see `vcl-threading` |
| touching a control from a worker thread | `TThread.Synchronize` / `TThread.Queue` |
| `TCriticalSection` from `System.Classes` | `System.SyncObjs` |

## Unit skeleton (XE7)

```delphi
unit Acme.Panel.Session;

interface

uses
  System.SysUtils,
  System.Generics.Collections;

type
  ESessionError = class(Exception);

  TSession = class
  private
    FFrames: TObjectList<TFrame>;
  public
    constructor Create;
    destructor Destroy; override;
    function FindByID(const AID: Integer): TFrame;
  end;

implementation

constructor TSession.Create;
begin
  inherited Create;
  FFrames := TObjectList<TFrame>.Create;
end;

destructor TSession.Destroy;
begin
  FFrames.Free;
  inherited Destroy;
end;

function TSession.FindByID(const AID: Integer): TFrame;
var
  Frame: TFrame;
begin
  for Frame in FFrames do
    if Frame.ID = AID then
      Exit(Frame);
  raise ESessionError.CreateFmt('Frame %d not found', [AID]);
end;

end.
```

## .dfm files

Keep forms in **text** DFM format so diffs are readable and an agent can edit them. Prefer changing
component properties in code or in the IDE. When editing a `.dfm` by hand, keep it in sync with the
`published` fields of the form class, or the form fails to load at runtime.

## Learned rules

Rules added from real mistakes. See the `skill-maintenance` skill for the format and the review process.

<!-- learned-rules -->
<!-- /learned-rules -->
