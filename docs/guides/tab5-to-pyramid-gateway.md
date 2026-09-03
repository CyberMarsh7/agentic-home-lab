# Connecting an M5Stack Tab5 to an AI Pyramid (Pro) as a Remote Controller

*A community writeup — no official M5Stack documentation currently covers
using a Tab5 as a dedicated remote client for a Pyramid/Pyramid Pro. This
covers the working architecture and a real library bug worth knowing about
if you're building something similar.*

## Architecture

The Tab5 does **not** talk to the Pyramid's on-device StackFlow voice
pipeline directly. Instead:

```
Tab5 (ESP32-P4)  <--WSS-->  Gateway service (runs on the Pyramid, Node.js)
                                   |
                                   +--> your LLM backend of choice
                                   +--> STT/TTS endpoints
```

The Tab5 is a thin client: it streams keystrokes and PCM audio out, and
receives text + synthesized speech back. All the actual agent logic and
model calls live in the gateway, not on the device. This keeps the ESP32
side simple and means the "brains" can be swapped out without re-flashing
anything.

- **Text path:** WebSocket (`wss://`), JSON messages, line-buffered on the
  gateway side.
- **Voice path:** plain HTTPS POST/response, deliberately **not** sent over
  the WebSocket connection (see the bug below for why), carrying raw WAV
  audio in both directions.
- **TLS:** self-signed certificate on the gateway, pinned via
  `NetworkClientSecure::setCACert()` on the device. Requires an NTP time
  sync on the ESP32 *before* attempting the TLS handshake — it boots at
  epoch 0 with no RTC battery, and a self-signed cert dated in the future
  relative to the device's clock will fail validation in confusing ways.

## The bug: `RSV2 and RSV3 must be clear`

If you're using the `arduinoWebSockets` library (Links2004) for the Tab5
side, watch out for this one — it cost real debugging time and the failure
mode is misleading.

**Symptom:** the device's serial log shows `WebSocket connected` followed
immediately by `WebSocket disconnected`, in a tight repeating loop. On the
gateway side (a Node.js server using the `ws` package), you'll see the
connection accepted, then immediately:

```
socket error: Invalid WebSocket frame: RSV2 and RSV3 must be clear
```

This looks like — and is often documented elsewhere as — a payload-size
issue (the library has a real, separate 15KB single-frame limit that
corrupts large sends). **But it can also happen on the very first, tiny
message**, before payload size is even a factor. Two causes, either of
which triggers the same server-side error:

1. **Sending from inside the library's own connection callback.** If your
   `onEvent` handler calls `ws.sendTXT()` synchronously when it sees
   `WStype_CONNECTED`, you're re-entering the library while it's still
   mid-handshake internally. Fix: set a flag in the callback and send from
   your main `loop()` on the *next* tick instead.
2. **A custom header via `setExtraHeaders()` on the SSL path.** If you're
   adding something like an `Authorization` header during
   `beginSslWithCA()`, this library's custom-header handling on the SSL
   connection path appears to corrupt subsequent frame construction. If you
   don't strictly need the header (e.g., you're authenticating via a
   message payload instead), removing it resolves the issue outright.

In practice, fix #2 was the one that actually mattered — #1 is good hygiene
regardless, but the header removal is what took the connection from
"reconnects every ~5 seconds, forever" to solid and stable.

## Practical notes

- Send voice audio over a plain HTTPS request, not a WS binary frame — the
  15KB frame-size limit in this library makes WS impractical for real audio
  clips anyway.
- If sending TTS audio *back* over the WebSocket (for typed-message
  replies), you'll need real WS continuation frames (fragmented sends) once
  you exceed that same 15KB ceiling — most `ws`-based Node servers handle
  this automatically if you pass a buffer larger than your chunk size and
  let the library fragment it.
- Test the full loop with a plain `curl`/simulated client against the
  gateway before ever touching the device — it isolates gateway bugs from
  device/library bugs immediately.
