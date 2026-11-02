---
name: vcl-threading
description: Use when Delphi VCL code talks to a device, the network or the disk, or anything else that can block, and whenever code runs in TThread, TTask or an anonymous thread. Keeps the UI responsive and prevents the access violations and deadlocks of cross-thread VCL access. Triggers on "TThread", "TTask", "Synchronize", "Queue", "freeze", "UI hangs", "not responding", "deadlock", "background", "worker thread", "serial port", "COM port".
---

# Threads in a VCL application (Delphi XE7)

## Rule 1 — the VCL is single-threaded

Only the main thread touches forms, controls, `Application` and `Screen`. A worker thread that sets
`Label1.Caption` produces access violations that reproduce once a week on a customer's machine.

## Rule 2 — nothing that can block runs on the main thread

Device communication, file I/O, network calls and `Sleep` belong in a worker thread. The UI shows progress
and stays clickable.

## Getting results back to the UI

| Call | Behaviour | Use when |
|------|-----------|----------|
| `Queue(procedure begin … end)` | asynchronous, the worker continues | progress, log lines, status — the default |
| `Synchronize(procedure begin … end)` | the worker waits until the main thread ran it | the worker needs a value back from the UI |

Inside a `TThread` descendant call the instance methods (`Queue(…)`, not `TThread.Queue(nil, …)`). Calls
queued by the thread are discarded when it is destroyed; calls queued with `nil` are not, and can run
against a form that is already gone. Destroy the worker before the form it reports to. From `TTask` or an
anonymous thread only the class methods `TThread.Queue(nil, …)` / `TThread.Synchronize(nil, …)` are
available; then the form must outlive the task.

In XE7, `Queue` called **from the main thread** runs the code immediately, not later (`ForceQueue` arrived
in 10.2). A fake device that answers synchronously on the main thread therefore causes reentrant calls.

Capture copies, not shared variables: anonymous methods capture variables **by reference**, so a loop
variable or a field changed by the worker may have moved on by the time the queued code runs.

## Stopping a thread

- `Terminate` only sets `Terminated`. The `Execute` loop must check it and exit.
- A blocking read never sees `Terminated`. Use timeouts on every device or socket read, or an event the
  stop path can signal (`TEvent`).
- **Deadlock:** the main thread blocks on something the worker cannot release while the worker sits in
  `Synchronize`: `TEvent.WaitFor`, `WaitForSingleObject`, a critical section the worker needs, a busy loop.
  Both wait forever. `TThread.WaitFor` itself is safe from the main thread, because it processes pending
  `Synchronize` calls while it waits; calling it from inside a synchronized method is not.
  Prefer `Queue`, and never block the main thread on anything else a worker might need.
- An exception that escapes `Execute` ends the thread silently and is stored in `FatalException`. Catch,
  log and report it to the UI, or check `FatalException` in `OnTerminate`.
- `FreeOnTerminate := True` means nobody may touch the object after `Start`. Pick one owner.

## Shared state

- Protect shared data with `TCriticalSection` (`System.SyncObjs`) or `TMonitor.Enter/Exit` on a private lock object.
- Counters and flags: `TInterlocked`.
- Keep the locked section short and never call `Synchronize` while holding a lock.

## Do not

- `Application.ProcessMessages` inside a long operation. It lets the user click again into a half-finished
  operation (reentrancy) and hides the real problem.
- One thread per request. Long-lived device sessions get one dedicated worker; short CPU work goes to `TTask`.

## Skeleton — a device session worker

```delphi
type
  TFrameEvent = reference to procedure(const AFrame: TBytes);

  TDeviceWorker = class(TThread)
  private
    FPort: IDevicePort;
    FOnFrame: TFrameEvent;
    procedure Deliver(const AFrame: TBytes);
  protected
    procedure Execute; override;
  public
    constructor Create(const APort: IDevicePort; const AOnFrame: TFrameEvent);
  end;

constructor TDeviceWorker.Create(const APort: IDevicePort; const AOnFrame: TFrameEvent);
begin
  inherited Create(True);
  FPort := APort;
  FOnFrame := AOnFrame;
end;

procedure TDeviceWorker.Deliver(const AFrame: TBytes);
var
  Frame: TBytes;
  Handler: TFrameEvent;
begin
  Frame := Copy(AFrame);
  Handler := FOnFrame;
  Queue(
    procedure
    begin
      Handler(Frame);
    end);
end;

procedure TDeviceWorker.Execute;
var
  Frame: TBytes;
begin
  NameThreadForDebugging('DeviceWorker');
  while not Terminated do
    if FPort.TryReadFrame(Frame, 200) then
      Deliver(Frame);
end;
```

`Deliver` gives every queued call its own captured copy. Capturing `Frame` from `Execute` directly would
hand the UI whatever the next read put there.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
