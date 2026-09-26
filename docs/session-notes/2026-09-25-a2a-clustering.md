# Victus ↔ Pyramid A2A clustering — done (2026-09-25)

Following on from a long overnight session (2026-09-24) that fixed Victus
(duplicate OpenClaw installs, broken Ollama runtime, agent DB schema
migrations) and Pyramid (recovered SSH access, connected it to Victus's
Ollama over Tailscale, fixed its dashboard), this session tackled the
actual "agents talk to each other" piece of the README's Vision section.

## What was tried first, and ruled out

`openclaw connect` was the first idea — investigated via its real `--help`
output and live docs. Ruled out: a "node" created this way is a subordinate
**peripheral** of one gateway's agent (exposes camera/exec/screen etc.), not
an independent agent acting as a peer. `agents team` was also checked and
ruled out for the same reason from the other direction — it coordinates
multiple agents *within one gateway process*, not across separate machines.

## What actually works: A2A

OpenClaw ships a real, documented **A2A (Agent2Agent)** channel plugin — a
standard JSON-RPC protocol for two independent gateways to send each other
tasks directly, each keeping its own agent. This is the feature that
fulfills the original Vision section, not a workaround.

**Setup**: each gateway advertises an Agent Card at
`/.well-known/agent-card.json` and accepts authenticated `SendMessage`
calls at `/a2a/v1`. Configured both directions with fresh random bearer
tokens (`openssl rand -hex 32`, one per direction — Victus's outbound token
is Pyramid's inbound token, and vice versa) via `channels.a2a.peers` in
each gateway's `openclaw.json`. Both gateways already had working public
HTTPS addresses over Tailscale Serve from the prior session
(`https://marshinvic.tail2f8a97.ts.net`,
`https://pyramid-openclaw-1.tail2f8a97.ts.net`), so no new networking was
needed — just the A2A config block on each side.

## Gotchas hit during setup

- Pyramid's gateway needed a full restart to pick up the new `channels.a2a`
  config (Victus applied live, no restart needed — same patch, different
  reload behavior, worth remembering).
- The known Tailscale Serve fragility from the prior session recurred on
  this restart too (OpenClaw's own `tailscale-route-owner.worker.js`
  process needs to be reconciled after every gateway restart on Pyramid) —
  confirmed this is now a standing thing to check after any Pyramid
  restart, not a one-off from last time.
- Pyramid's agent-card endpoint returned `502`/connection-refused for about
  20-25 seconds right after the restart before the gateway finished
  loading its sessions and started actually listening — normal startup
  time on this hardware, not a failure, just needs a beat before testing.

## Verification (both directions, real evidence not just exit codes)

- `openclaw agent --channel a2a --to pyramid --message "..." --deliver`
  from Victus → got a clean "OK" back, and Pyramid's own
  `openclaw sessions list --agent main` showed a new session
  `agent:main:a2a:...pyramid`, `owner: victus`, timestamped "1m ago."
- Same test in reverse (`--to victus` from Pyramid) → clean "OK," and
  Victus's own session list showed the matching `owner: pyramid` session.
- Confirmed no regressions: Pyramid can still reach Victus's Ollama over
  Tailscale, and both dashboards are still reachable.

Interesting side note: task turns sent through the A2A channel returned
clean text replies, not the raw unexecuted tool-call JSON bug that's still
open on Pyramid's regular webchat/dashboard path — A2A appears to route
differently and isn't affected by that bug. Worth investigating *why*
whenever that bug gets picked up properly, since it might point at the
actual cause.

## Division of labor (decided this session, not evenly split)

Not a symmetric carousel. **Pyramid** = the artistic/light-agent side —
vision-oriented and creative work, plus MCP-server hosting for the
ESP32-S3/Stackchan hardware once that's built. **Victus** = the heavy
horse — anything needing real reasoning weight or a larger model, via its
GPU. Pyramid should hand heavy work to Victus far more often than the
reverse; Victus mostly only calls Pyramid when a task specifically needs
Pyramid's vision capability or its MCP-connected hardware.

**Still unverified**: exactly what "Pyramid's vision capability" consists
of in hardware terms — its public spec sheet lists dual HDMI in/out and a
24 TOPS INT8 NPU, no camera. The NPU itself is well-suited to vision
*inference* even without an attached camera (processing images handed to
it), but whether there's an actual camera or capture device physically
attached needs checking (`lsusb`, `v4l2-ctl --list-devices`, what's
plugged into HDMI-in) before assuming either way. Not done yet.

## Voice pipeline: fixed the raw-tool-call-JSON bug (root cause)

The Stackchan/Watcher voice pipeline (mic → Pyramid STT → agent → Pyramid
TTS → speaker) was working but slow (56s/reply) because it called `main`
(Samantha), whose `full` tool profile generates a ~28k-char system prompt
every turn. Fix: added a dedicated `voice` agent
(`ollama/qwen2.5-coder:1.5b`) for fast, low-latency replies — 85x speedup
(56s → ~5-7s).

That surfaced the long-standing raw-tool-call-JSON leak bug (small models
emitting unexecuted tool-call JSON as visible text) on this new agent too.
Tried, in order, and none of these fixed it: `tools.profile: minimal`,
`tools.alsoAllow: []`, `tools.allow: []` (the "absolute allowlist"
override). All of them still left OpenClaw's own baseline bridge tools
(`tool_search`/`tool_describe`/`tool_call`) attached to every request
regardless of agent-level tool config — those three are apparently always
injected unless the *model itself* is declared tool-incapable.

**Actual fix**: `models.providers.ollama.models[<idx>].compat.supportsTools:
false` on the specific model entry (`qwen2.5-coder:1.5b`), both on Victus
and on Pyramid (which had the identical bug on its own default chat path).
This is model-level, not agent-level — declaring a model doesn't support
tools means OpenClaw never attaches any tool schema to its requests, so
there's nothing for the model to hallucinate a call format around. Several
other already-registered models in this config (`embeddinggemma`,
`deepseek-ocr`, `gemma2:2b`, `codellama:13b`, `yi-coder`, `qwen:latest`) had
already been marked this way, so this is the established, intended
mechanism for exactly this problem — just not one we'd used for
`qwen2.5-coder:1.5b` before.

Verified clean (no leaked JSON, no tool-schema-in-prompt) on both machines,
then ran the full pipeline end-to-end via Pyramid's `/greet` endpoint:
clean reply text, real WAV audio returned. Also found and fixed two
unrelated bugs blocking that end-to-end test: `pyramid-bridge.service` was
running stale code (needed a restart to pick up an earlier session-key
edit), and Pyramid's local `llm-melotts` TTS service was returning HTTP 200
with empty audio bodies (fixed by `systemctl restart llm-melotts.service`).

If this reappears on a new small/local model added later, the fix is the
same: mark that model's `compat.supportsTools` false rather than trying to
fight it at the agent tool-profile level.

## Explicitly not done in this session

- No routing logic implemented yet that actually uses the division of
  labor above (A2A is the transport; nothing currently decides
  automatically when to hand a task off — that's manual/future work).
- No MCP server for ESP32-S3/Stackchan.
- No work on the SSD/"portable agent gallery" migration (separate,
  still-open plan from earlier the same night — see
  `docs/portable-agent-drive-plan-2026-09-24.md`).
- CardputerZero and Brilliant Labs Halo integration — both researched and
  documented as future work, neither built (CardputerZero doesn't ship
  until ~November 2026; Halo needs a custom BLE-to-Tailscale bridge app,
  likely via the user's iPhone, since Halo has no WiFi radio at all).
