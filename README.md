# agentic-home-lab

Bret's home lab of AI agents running across physical hardware. This repo is
the durable record of that setup — so device reflashes, session resets, and
lost desktop files don't wipe out the knowledge of how it's built and how
to fix it.

## The actual goal (read this before anything else)

Bret cannot type — it physically hurts. **Every agent, every interface, every
setup step in this lab must be usable entirely by voice, with no typing and
no precise clicking required.** This isn't a nice-to-have; it's the reason
the whole lab exists, built for his wife and kids too. If a fix, a doc, or
a setup step assumes typing, it's not done yet — it needs a voice-first path
before it counts as finished. When in doubt, optimize for "can Bret just
talk to it," not for technical completeness.

## Devices

| Device | Role | Reachable at | Notes |
|---|---|---|---|
| **Victus** | Main machine (Windows laptop, RTX 4050 / 6GB VRAM) | local | Runs its **own OpenClaw gateway** (hosts Samantha, hermes), plus Ollama (local models) and Claude Code installed locally. Pyramid is physically docked into it |
| **Pyramid** (aka "Oracle") | Gateway — everything routes through this first | `192.168.1.227`, SSH as `marshinpyramid` | Runs its **own OpenClaw gateway**. Two installs exist on disk — always use the explicit path `/root/.npm-global/lib/node_modules/openclaw/dist/index.js`, not the stale `/usr/bin/openclaw`. No monitor attached; managed headlessly over SSH or the Control UI at `http://192.168.1.227:18789` |
| **Kali Pi** | Security-tooling agent (Raspberry Pi, genuine Kali Linux) | `marshinpi-1` on Tailscale | No GPU/NPU, 921MB RAM — routes model inference to Victus's Ollama over Tailscale |
| Old Kali box | Possibly superseded by the Kali Pi above, unconfirmed | `192.168.1.117` | Never confirmed reachable — needs clarifying |

## Agents

- **Samantha** — runs on Victus, local model (`qwen2.5:3b-instruct`), security-hardened (web/browser tools disabled, cautious exec policy). Do not swap her to a cloud model without deciding that on purpose.
- **hermes** — also on Victus, currently stopped (was competing with Samantha for GPU memory). Config is lightened for whenever it's restarted.
- **claude** — being added to the Pyramid gateway alongside Samantha, backed by Claude (`claude-cli/claude-opus-5`), reusing the local Claude Code subscription login rather than a separate API key. See `docs/openclaw-setup-2026-09-03.md`.

## Vision

The intended architecture:

- **Pyramid is the front door.** Everything Bret says goes to Pyramid first.
- **Fallback:** if Pyramid is down or unreachable, it falls back automatically
  to whatever Claude window/device Bret is actually talking through (e.g. a
  local Claude Code session on Victus), so there's never a moment with no
  answer at all.
- **Agents talk to each other** and split up work, instead of each one only
  knowing its own isolated piece.

Real, worth doing, still in progress — not yet built, this is the target.

## Docs in this repo

- `docs/session-notes/` — dated logs of what was actually done in each session, verified not assumed.
- `docs/hardware/` — hardware-specific fixes and handoff notes (e.g. the Pyramid gateway-down fix).
- `docs/guides/` — reusable how-tos for problems solved here that don't have good docs elsewhere.
- `docs/portfolio/` — writeups of finished builds.
- `docs/openclaw-setup-2026-09-03.md` — current OpenClaw agent setup steps and open issues.

## Why this repo exists

Two Pyramid devices were reflashed and lost their agents; setup knowledge
had been living only in scattered desktop files. This repo is the fix for
that — the goal is that nothing here has to be rebuilt from memory again.
