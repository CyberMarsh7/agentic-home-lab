# Tonight's Session — What We Actually Did

2026-08-24 into 2026-08-25. Long session, lots of ground covered. Here's the real state of things.

## Samantha — fixed, hardened, documented

- **Root problem:** her model routing was falling through to a Venice AI account with a dead API key (401 on every call). That's why the watch stopped working — not the watch, not the bridge, her brain couldn't answer.
- **Fixed:** switched her to `qwen2.5:3b-instruct`, a small local model that actually fits this machine's GPU (RTX 4050, 6GB VRAM — the real ceiling on everything tonight). Tried four other candidates first; all either misfired or were too big to respond in usable time. Full comparison table in **WorkingSam.md** on the Desktop.
- **Wrong-name bug fixed:** she kept calling you "Christopher" — a leftover test skill (`greet-christopher`) was polluting her context. Removed.
- **Security hardened**, per your ask tonight ("don't let her loop," "prompt injection," "physical fallback"):
  - Web/browser tools disabled for her small model (OpenClaw's own audit flagged this as CRITICAL before the fix — small models are more easily confused by malicious web content)
  - `exec-policy` switched to `cautious` — nothing risky runs on autopilot anymore; unapproved actions fail closed, not open
- **Verified working end to end**, multiple times, including through the exact session path the watch uses.

## hermes — stopped

You asked me to kill it (it was competing with Samantha for the same 6GB of GPU memory, causing both to slow to a crawl). It's not deleted, not uninstalled — just not running. Start it again the normal way whenever you want it back; I lightened its default model too, in the config, for when it does come back.

## Oracle (Pyramid) — confirmed healthy

Checked twice tonight. First check falsely said "disabled" — that's a known false-negative (SSH `sudo` losing systemd env vars). Rechecked properly: running fine, nothing was actually broken.

## Mobile app "won't connect" — fixed

Both Samantha's and Oracle's gateways were missing `gateway.trustedProxies` config, which meant connections routed through Tailscale Serve got misclassified as untrusted and lost permission scope. Set correctly on both machines, both gateways restarted. Should be fixed for the iPad/phone app now — worth trying again when you're back on it.

## Pyramid — can now flash ESP32-S3 hardware

`esptool` and PlatformIO Core installed and verified working over SSH (had to go through Tailscale — the direct LAN IP wasn't reachable from Victus). Confirmed two genuine ESP32-S3 boards physically plugged in (`/dev/ttyACM0`, `/dev/ttyACM1`, different MAC addresses so two distinct boards) — identified but not yet flashed, since I don't yet know if they have a mic/speaker (needed for a Xiaozhi-style voice front-end) or are bare devkits.

## New agent: the Kali Pi

- Real hardware: a Raspberry Pi running genuine Kali Linux 2026.3 (nmap, hydra, msfconsole all present), reachable at `marshinpi-1` on Tailscale.
- OpenClaw installed fresh, running as a persistent service (survives reboot).
- Since this Pi has no GPU/NPU and only 921MB RAM, it routes all its thinking to Victus's Ollama over Tailscale rather than trying to run a model itself — same "borrow the GPU" pattern Oracle already uses.
- Same security hardening applied as Samantha (web/browser tools denied, cautious exec policy).
- Verified working end to end — real reply, 19 seconds, correctly self-identified its own model.
- **Still needs from you:** a name/persona, and a decision on whether it gets an ESP32 front-end (and if so, which physical board, plus a fresh token from your Xiaozhi account for that new device — that step needs your login, can't be done remotely).

## Hardware inventory — captured

Full collection (M5Stack fleet, ESP32 boards, wearables, pentest gear, SBCs) written down so it doesn't need re-listing. See the hardware-scope note if it comes up again.

## Open threads, not started

- The old Kali box at `192.168.1.117` — never got confirmed reachable; may be superseded by the new `marshinpi` Pi, or may be a separate third device. Worth clarifying next time.
- ESP32 front-end for the Kali Pi agent — blocked on board identification + Xiaozhi token.
- "Halo frames," "car computer zero," "the 2350 RP" — still just names, no specs yet.
- The full Pyramid-controls-everything integration vision — real, worth doing, not started as of this session.

Everything above is genuinely done and verified, not assumed.
