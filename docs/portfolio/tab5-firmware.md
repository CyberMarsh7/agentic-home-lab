# Project: M5Stack Tab5 Remote AI Agent Controller

**Stack:** C++ (Arduino/ESP32-P4), M5Unified/M5GFX, WebSockets (TLS), Node.js gateway, custom 2D graphics rendering

## What it is

Firmware for an M5Stack Tab5 (ESP32-P4) that turns the device into a dedicated
touchscreen client for talking to two distinct AI agent personas — one by
typing (physical keyboard), one by voice (push-to-talk) — over a secure,
auto-reconnecting WebSocket link to a custom gateway service. No off-the-shelf
firmware or app existed for this; the whole client, protocol, and UI were
built from scratch.

## Technical highlights

- **Full custom 2D UI rendered with raw graphics primitives** — no widget
  library available on this stack, so every element (a tabbed agent
  switcher, a bordered "token box" text panel, a volume control with a live
  fill-bar, a HUD-style window frame with corner brackets, a fluted Roman
  column used as a panel divider) is hand-built from `fillTriangle`,
  `fillEllipse`, `drawArc`, and rotation math.
- **Custom rotation/vector math for character art** — a rotating
  "loading spinner" built from six triangles rotated in real time around
  their own center via a hand-rolled 2D rotation matrix, and a full
  character silhouette (robe, cape, hat, arm gesture) that rotates and
  translates as one coherent rigid body to sit convincingly on a tilted
  broom, rather than independent unrotated parts.
- **Real astronomical calculation on embedded hardware** — computes the
  actual current lunar phase from device time (NTP-synced) using a synodic-
  month reference epoch, then renders the correct crescent/gibbous shape
  using a two-circle-overlap clipping technique — no per-pixel rendering,
  just primitive shapes and clip rects.
- **Diagnosed and fixed a real bug in a third-party library**
  (`arduinoWebSockets`, no newer version available): sending data
  synchronously from inside the library's own connection-event callback,
  combined with a custom HTTP header on the SSL handshake, corrupted frame
  construction (`RSV2 and RSV3 must be clear`) and silently killed every
  connection attempt in a tight retry loop. Root-caused via live serial
  capture and gateway-side log correlation, fixed by deferring the send to
  the next event-loop tick and removing the unnecessary header — see the
  companion M5Stack integration writeup for full detail.
- **Accessibility-driven design decisions** — colors chosen against the
  Okabe-Ito colorblind-safe palette rather than arbitrary hues, after a
  real-world report that a standard saturated blue was reading as green for
  the end user; large touch targets throughout for a low-vision user.

## Before / after

Started as a stock two-pane text interface. Ended as a themed, animated,
dual-persona control surface with live agent switching, voice I/O, a
volume subsystem, real-time astronomical data, and original character art —
while fixing two separate hard compile/runtime bugs along the way.
