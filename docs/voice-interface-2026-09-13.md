# Voice interface: push-to-talk, no always-on listening (2026-09-13)

## Requirement (from README, restated precisely)

Bret cannot type or click precisely, and explicitly does **not** want an
always-listening microphone. He wants a physical button he presses to
talk, and a spoken reply back. This is the actual reason the two ESP32-S3
boards were bought and plugged into Pyramid (per
`docs/session-notes/2026-08-25-session-summary.md`) — confirmed by Bret
directly on 2026-09-13.

## What OpenClaw actually supports (verified against docs.openclaw.ai)

**Wake-word listening (`voicewake`) and push-to-talk (`talk.ptt.*`) are
two separate, independently controllable systems.** Wake-word can be left
completely off. Push-to-talk is the one Bret wants.

### The underlying primitive — this is the important part

Every OpenClaw "node" (macOS, iOS, Windows) exposes these Gateway-callable
commands:

```
talk.ptt.start    # begin capturing audio
talk.ptt.stop     # stop capturing, send what was captured
talk.ptt.cancel   # abort, send nothing
talk.ptt.once     # single-shot capture-and-send
talk.speak        # speak a reply back (TTS)
```

(iOS's own docs spell it `talk.ppt.*` — same feature, inconsistent docs.)

These are called over the Gateway's WebSocket/CLI, **not tied to any
specific GUI element**. That means a genuinely "dumb" physical button —
a GPIO button on a Pi, or a USB/Bluetooth HID button — can drive real
push-to-talk by calling these commands directly, once wired up. This is
not a documented off-the-shelf feature (no existing GPIO/hardware-button
binding ships with OpenClaw) — it would need to be built, but the API to
build it against is real and confirmed.

**This is likely exactly what the ESP32-S3 boards on Pyramid were for**:
firmware on the board reads a physical button press, then calls
`talk.ptt.start`/`talk.ptt.stop` on the Gateway (Pyramid) over the network,
and plays back whatever `talk.speak` sends. That work never got past
"boards identified, mic/speaker unconfirmed" per the August session note.

### Two already-built (no custom firmware needed) alternatives, if a phone is workable

- **iOS: bind the Action Button (or a Shortcut) to "Start Live Voice."**
  Best-documented, fully native path — press one physical button, live
  voice session starts, spoken reply comes back automatically. No wake
  word, no typing, no precise tapping. (`docs.openclaw.ai/platforms/ios`)
- **macOS: hold the Right Option key to talk, release to send.** A global
  hotkey monitor (not a GUI click) — in principle remappable from an
  external USB/Bluetooth macro button, since it listens for the raw key
  event, not a specific on-screen target. (`docs.openclaw.ai/platforms/mac/voicewake`,
  `.../voice-overlay`)

### Platform caveat that matters for this lab

**Linux (Pyramid, Kali Pi) cannot do Talk-mode microphone capture through
its own desktop companion app** — the embedded WebView has no mic
permission. Voice on a Linux box has to go through a real browser pointed
at the Gateway's Control UI (`http://<host>:18789`), not the bundled app.
This doesn't block the custom-hardware-button approach (that talks to the
Gateway API directly, not through the companion app's UI).

### Getting the reply spoken back, regardless of trigger

`tts.auto` (config key) makes every agent reply auto-spoken without Bret
asking each time. Telephony and Talk sessions get real audio streams;
other channels get an audio attachment.

## Recommended path (not yet built — needs a decision + local hands)

1. **Fastest to something real today, if Bret carries a phone:** set up
   the iOS Action Button → "Start Live Voice" shortcut. Zero new hardware,
   confirmed native feature.
2. **The actual original vision (a dedicated physical button on/near
   Pyramid):** finish identifying the ESP32-S3 boards' mic/speaker
   capability (still unconfirmed since August), then write firmware that
   calls `talk.ptt.start` on button-press and `talk.ptt.stop` on release,
   using the Gateway's pairing flow (`docs/gateway/pairing` —
   `openclaw devices approve` then `openclaw nodes approve` for the new
   node) so the board is a trusted node.

**Open decision only Bret can make:** which of these two to pursue first,
or both.

## Sources (fetched live, 2026-09-13)

- [nodes/voicewake](https://docs.openclaw.ai/nodes/voicewake)
- [nodes/talk](https://docs.openclaw.ai/nodes/talk)
- [nodes/audio](https://docs.openclaw.ai/nodes/audio)
- [platforms/mac/voicewake](https://docs.openclaw.ai/platforms/mac/voicewake)
- [platforms/mac/voice-overlay](https://docs.openclaw.ai/platforms/mac/voice-overlay)
- [platforms/windows](https://docs.openclaw.ai/platforms/windows)
- [platforms/linux](https://docs.openclaw.ai/platforms/linux)
- [platforms/ios](https://docs.openclaw.ai/platforms/ios)
- [platforms/android](https://docs.openclaw.ai/platforms/android)
- [gateway/pairing](https://docs.openclaw.ai/gateway/pairing)
- [channels/pairing](https://docs.openclaw.ai/channels/pairing)
- [web/control-ui](https://docs.openclaw.ai/web/control-ui)
- [tools/tts](https://docs.openclaw.ai/tools/tts)
- [cli/voicecall](https://docs.openclaw.ai/cli/voicecall)
