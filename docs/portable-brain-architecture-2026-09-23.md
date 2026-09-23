# The "portable brain" architecture (2026-09-23)

Bret's plan, written down properly. This replaces the earlier "Hermes on
Victus" draft in PR #2 with a cleaner, verified design.

## The core idea

One orchestrator (Pyramid), one heavy-compute box (Victus), an SSD that
holds a library of models and premade agent templates, and a growing set
of thin client devices that never run any model themselves — they just
talk to Pyramid.

```
                         Bret (voice, any device)
                                  |
        PineTab2 --- Halo glasses (via phone, BLE) --- phone --- laptop
                                  |
                                  v
                    PYRAMID (the one gateway, the front door)
                    - SSD attached here: model library +
                      premade agent config templates
                    - Picks which preset agent handles a request
                    - Decides: light enough to run here, or
                      does this need Victus's GPU?
                                  |
                        (Tailscale, only when needed)
                                  v
                        VICTUS (GPU, heavy lifting)
                    - Samantha (existing, hardened, local model)
                    - Runs whichever preset agent Pyramid handed
                      off, using Victus's real VRAM
```

**Key correction from the original framing:** the SSD doesn't get
physically unplugged and moved between devices. It stays attached to
Pyramid (which is short on storage) and Pyramid reaches Victus's compute
*over Tailscale*, not by moving hardware. Network routing already solves
what physical swapping was meant to solve, and it's instant instead of
requiring anyone to touch anything.

## Why this is a real, buildable plan (not a guess)

- **Single gateway, no lock/port conflicts** — directly fixes the
  restart-every-10-seconds crash loop from `docs/gateway-crash-loop-2026-09-23.md`.
- **Per-agent model routing to a different machine** is a real, documented
  OpenClaw capability — the Kali Pi already does exactly this today,
  routing inference to Victus's Ollama over Tailscale without running its
  own gateway.
- **Premade agent configs as portable files** matches OpenClaw's own
  recommended pattern: git-init the workspace, commit config/personas,
  never commit credentials. A shelf of ready `agents.entries.*` blocks +
  `AGENTS.md`/`SOUL.md` templates is just files — copy the right one in
  when a new device or use-case shows up.

## Client tier — devices that never run a model, they just reach Pyramid

| Device | Status | Path |
|---|---|---|
| Phone (iOS/Android) | Documented, native | OpenClaw companion app, `talk.ptt.*` — see `docs/voice-interface-2026-09-13.md` |
| PineTab2 | Target: days | Real Linux ARM tablet. Browser hitting Pyramid's Control UI, or the `openclaw` CLI dispatching directly (`openclaw agent --agent <id> --message ...` pointed at Pyramid over Tailscale). No custom firmware needed. |
| Halo glasses (Brilliant Labs — official name is "Halo," not "Halo Frames"; confirm which product Bret actually has, since Brilliant also sells an older "Frame") | Target: weeks, real but unverified timeline | **Confirmed against brilliantlabs.xyz:** $399, shipping since early August, open-source hardware/software, dual bone-conduction speakers, dual mics, Brilliant SDK + Flutter SDK for iOS/Android. **Ships with its own built-in assistant, "Noa" (long-term memory).** Real open question, not yet resolved: whether the bridge to Pyramid goes through Noa (if Brilliant exposes a webhook/API for it) or bypasses Noa with a custom app using their SDK. **Bluetooth-5.3-only / no-WiFi claim is from a secondary review source, not Brilliant's own page — unverified, don't design around it as fact yet.** Needs the actual SDK repo (`github.com/brilliantlabsAR/brilliant_sdk`) read before committing to a bridge design. Not yet built, no promised date. |
| ESP32-S3 boards on Pyramid | Confirmed working per Bret, 2026-09-13 | Physical push-to-talk button, network call already functional — see `docs/voice-interface-2026-09-13.md`. Was talking to the factory 0.5B demo model; needs rewiring to call Pyramid's real gateway instead. |

Sources for Halo: [Brilliant Labs Halo product page](https://brilliant.xyz/products/halo), [Halo open-source SDK monorepo](https://github.com/brilliantlabsAR/brilliant_sdk), [designboom coverage](https://www.designboom.com/technology/halo-open-source-glasses-private-ai-agent-brilliant-labs-08-01-2025/).

## Preset agents — starter list (grows over time, not "everything" at once)

Named, scoped, each with a real reason already established in this repo —
not a blank wish list:

1. **Secretary** (Samantha, Victus) — email/text triage. Decided
   2026-09-13, see `docs/agent-jobs-backlog-2026-09-13.md`.
2. **Front door / general assistant** (`claude` agent, Pyramid) — what
   answers when Bret just talks to Pyramid with no specific task.
3. **Security** (Kali Pi's existing agent) — already built, per
   `docs/session-notes/2026-08-25-session-summary.md`.
4. **Orchestrator** (Hermes, Victus) — drives Pyramid's gateway via CLI,
   uses Victus's own Claude CLI login for its own reasoning. Replaces the
   "Hermes runs its own gateway" idea from PR #2.
5. **Coder** — not yet scoped. Add when there's a real task for it.
6. **Weekly memory fold** — not an agent, a config change
   (`plugins.entries.memory-core.config.dreaming.frequency`), already
   documented in `docs/stackchan-mcp-and-memory-2026-09-03.md`.

New presets get added to this list **only when there's a specific task
driving them** — "a ton of agents for everything" grows this list one
real need at a time, not by inventing categories nobody asked for.

## What's actually still needed before any of this runs

1. Fix the gateway crash loop (diagnosis already done,
   `docs/gateway-crash-loop-2026-09-23.md`) — has to happen first, nothing
   else is stable until this is fixed.
2. Decide: does Victus keep running any OpenClaw gateway at all, or purely
   contribute compute? (This doc assumes purely compute — no gateway on
   Victus.)
3. Physically get the SSD onto Pyramid and confirm it can actually run
   larger local models there.
4. Build the Halo↔Pyramid bridge (real software project, scope it
   separately when ready to start).
5. All of this still needs a local session with real hands on the
   hardware — this document was written from a cloud session with no LAN
   access, same limitation as everything else in this repo.
