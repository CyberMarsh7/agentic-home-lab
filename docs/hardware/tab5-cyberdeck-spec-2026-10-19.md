# Tab5 Cyberdeck — exact build spec (2026-10-19)

**Read this whole file before touching any code. Do not improvise. Do not
"improve" the layout. If anything here is unclear, stop and ask Bret by
voice-friendly question. Do not guess.**

## Why this doc exists

For three days an agent was asked to build the Tab5 cyberdeck screen and
instead shipped a tiny split box (cyan panel + green grid panel) jammed in a
screen corner, then "fixed" a rotation problem by moving that same small box
to the opposite corner. That is not what was asked for. This spec replaces
whatever the agent invented. Bret was in the room and confirmed every point
below by voice on 2026-10-19.

## The device and the goal

- **Tab5** (M5Stack, ESP32-P4) with the **Tab5 Keyboard case** attached at the
  bottom. Bret types with his thumbs on the physical keyboard.
- **S3U** (M5Stack Atom S3U) plugs into the *target* computer and acts as the
  USB HID keyboard/mouse. Bret never touches the target computer. Nothing is
  installed on the target.
- The Tab5 is the remote control. The S3U is the receiver.
- Bret has limited use of his hands (disability). Thumb typing and a big
  forgiving touch surface are the whole point. Precision-click UI is a bug.

## Requirement 1 — S3U link is a WebSocket (unchanged)

- The S3U already runs as a WiFi access point named `SecBot` and serves a web
  page (keyboard area + touchpad) that Bret's phone uses today. Phone to S3U
  works. **Do not break it.**
- Keep the same WebSocket pattern the phone already uses. Do not invent a new
  protocol and do not write new HID firmware if the existing one covers it.
- Bluetooth is NOT the path. Tab5 Bluetooth is broken under the current
  firmware. WiFi to `SecBot` only. No wired Tab5-to-S3U tether (it would cost
  Bret the Tab5 SD card).

## Requirement 2 — Tab5 scans, finds, and joins the S3U by itself

- On boot the Tab5 must **scan for the `SecBot` network, find it, and connect
  without Bret typing anything on the Tab5 screen.**
- **The password/auth step is part of the connection flow from the start.**
  This has been forgotten every single time and Bret has had to remind the
  agent. It is not optional and not a follow-up task. Store the credential in
  config on the device (not hardcoded in source, not committed to git; use
  `.env.example` style placeholders) and send it as part of connect.
- If the scan finds nothing, show a plain large message and retry on its own.
  Do not dead-end on a silent black screen.

## Requirement 3 — Phone stays supported in parallel

- Adding the Tab5 must not remove or replace the phone path. Both can be used.
  The S3U accepts the phone as it does today and also accepts the Tab5.

## Requirement 4 — Tab5 screen layout (the part that went wrong)

- **Landscape. The ENTIRE touchscreen is ONE trackpad.** Like an Apple
  trackpad. Full screen. No split. No second panel. No grid box. No small
  rectangle in a corner. Nothing is "a quarter size."
- Bret said it plainly: "Use the whole goddamn screen as a mouse pad. I don't
  care. Just build it."
- Touch behavior (standard trackpad):
  - one-finger drag moves the cursor
  - one-finger tap is left click
  - two-finger tap is right click
  - two-finger drag scrolls
- The physical Tab5 Keyboard case handles all typing. **Do NOT draw an
  on-screen keyboard.** The physical keyboard is attached; a software one is
  wrong.
- Rotation: the layout must match how the device is actually held with the
  keyboard case at the bottom. Fix the real display rotation setting. Do not
  fake a rotation fix by translating or shrinking the drawing.

## Out of scope for this task (do not build now)

- The text-preview/staging window and mic-to-text button. Those were an
  earlier idea and Bret has dropped them for this pass to keep it simple.
- The SD-card debug/triage agents and quarantine partition. Separate project.
- Anything involving OpenClaw. The cyberdeck stays self-contained.

## Definition of done (verify, don't claim)

1. Tab5 powers up, scans, finds `SecBot`, joins with the password, with no
   typing on the Tab5.
2. The whole screen is the trackpad, landscape, correct orientation for the
   keyboard case at the bottom. Screenshot or photo from Bret confirms it.
3. Dragging on the screen moves the cursor on a computer the S3U is plugged
   into. Tap clicks. Typing on the Tab5 keyboard types on that computer.
4. The phone still connects and works.
5. Report what was actually tested on real hardware and what was not.

## Working rules for the agent

- Work step by step. Finish and confirm one requirement before the next.
- Restate the spec back in plain words before changing code.
- If a change doesn't produce the stated result, say so. Do not report
  success based on "it compiled." Do not loop on the same failed approach;
  after two tries, stop and tell Bret what you saw.
- Commands for Bret must be short, single line, and dictation-safe. Bret works
  entirely by voice.
