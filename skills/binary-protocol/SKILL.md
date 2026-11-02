---
name: binary-protocol
description: Use when Delphi code builds, parses or transports binary messages between a desktop application and a device (USB, serial/COM port, TCP, or relayed through a cloud service), including firmware upload. Covers TBytes, framing, endianness, CRC, protocol versioning across firmware versions, and how to test it without hardware. Triggers on "protocol", "frame", "packet", "CRC", "checksum", "endianness", "byte order", "serial", "COM port", "USB", "firmware update", "TBytes", "packed record".
---

# Binary device protocols in Delphi

## Bytes are bytes

- Messages live in `TBytes` / `TBytesStream` / `TMemoryStream`. **Never in `string`**: a Unicode
  conversion silently changes the data.
- Every read checks bounds first. A short or corrupt frame must raise a protocol error, not read past the end.

## Serialise field by field

Casting a buffer onto a `packed record` is tempting and fragile: it hard-wires alignment and byte order,
and it breaks when a firmware version adds a field. Prefer a small reader/writer that reads one field at a
time and states the byte order explicitly.

```delphi
function ReadUInt16BE(const ABuf: TBytes; const AOffset: Integer): Word;
begin
  if AOffset + 2 > Length(ABuf) then
    raise EProtocolError.CreateFmt('Frame too short at offset %d', [AOffset]);
  Result := (Word(ABuf[AOffset]) shl 8) or ABuf[AOffset + 1];
end;
```

x86 is little-endian. Write the device's byte order into the function name (`BE` / `LE`).

## Framing

Typical shape: start marker, length, type, payload, CRC. The parser:

1. finds the start marker and resynchronises after garbage,
2. waits for the full length before parsing,
3. verifies the CRC before trusting any field,
4. rejects lengths above the protocol maximum (a corrupt length must not allocate megabytes).

## CRC

Table-driven, with **published test vectors** in a unit test (the check value of the ASCII string
`123456789` is the standard vector). A CRC without a test vector is a guess.

Name the exact variant: polynomial, init, reflection, xorout and check value. "CRC-16/CCITT" alone covers
several incompatible algorithms (CCITT-FALSE `0x29B1`, KERMIT `0x2189`, XMODEM `0x31C3`, X-25 `0x906E`).

## Versions

Devices in the field run many firmware versions. The protocol layer:

- reads the device's firmware/protocol version during the handshake,
- decides capabilities from it in **one** place (a capability table), not in `if` statements spread across the UI,
- tolerates unknown trailing fields from newer firmware,
- never writes a parameter the connected version does not support.

## Security

- Do not invent cryptography. Use a vetted implementation of the agreed algorithm (e.g. AES-GCM/CCM, HMAC).
- No keys or secrets in source code or in the repository.
- Compare MACs and authentication responses in constant time.
- Short PIN-style secrets must not be guessable offline from a recorded session. That is a protocol design
  question for the firmware team, not a client-side fix.

## Serial / COM ports

- Open with `CreateFile('\\.\COM10', …)`. The `\\.\` prefix is required from COM10 upwards.
- Set read timeouts (`SetCommTimeouts`) so a dead device does not hang the worker forever.
- All port I/O runs in a worker thread (see `vcl-threading`).

## Firmware upload

Treat it as a state machine with explicit states (prepare, transfer blocks, verify, activate, reboot,
reconnect) and a defined recovery from every state. A power cut in the middle must leave a device that can
be retried, not a dead one. Log every transition.

## Testing without hardware

- **Captured frames as fixtures:** hex dumps of real traffic, stored next to the tests, parsed in round-trip tests.
- **A fake device** implementing the same port interface, so the protocol and session logic run in CI.
- **A hardware-in-the-loop stand** for the end-to-end checks that need a real device.
- Fakes, fixtures and characterization tests in detail: `delphi-testing`.

## Learned rules

<!-- learned-rules -->
<!-- /learned-rules -->
