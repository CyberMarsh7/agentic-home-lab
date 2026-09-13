# Stackchan MCP integration + weekly memory folding (2026-09-03)

Two new requirements from Bret, recorded here so they don't get lost.

## 1. Weekly memory folding

**Requirement:** agents should fold/summarize their memory every 7 days —
preserve what conversations were about, not necessarily every raw message
forever.

**Correction (2026-09-13): the paragraph below was wrong.** Re-verified
directly against docs.openclaw.ai — "dreaming" IS time-based, driven by an
actual cron expression, not a usage/recall-frequency score as originally
written here. This makes the "gap" described below **not a gap** — the
schedule already exists, it just needs to be set to weekly instead of its
default daily.

**What OpenClaw actually offers, corrected:** a background "dreaming"
sweep that consolidates daily notes into long-term memory (`MEMORY.md`),
scheduled via a real cron expression:

```
plugins.entries.memory-core.config.dreaming.enabled     # on by default
plugins.entries.memory-core.config.dreaming.frequency   # cron expr, default "0 3 * * *" (daily 3am UTC)
plugins.entries.memory-core.config.dreaming.timezone    # IANA tz
plugins.entries.memory-core.config.dreaming.model       # optional model override
agents.defaults.compaction.memoryFlush.enabled          # separate: flush before compaction, not a dreaming sweep
```

**To get Bret's actual 7-day requirement, this is likely all that's
needed** (once on a local session that can run it):
```bash
openclaw config set plugins.entries.memory-core.config.dreaming.frequency "0 3 * * 1"
```
(Monday 3am — pick whatever day/time actually fits.) Within each sweep,
three gates must all pass before something gets promoted to `MEMORY.md`:
a minimum score, a minimum recall count, and a minimum query-diversity —
that scoring logic is real but is about *what* gets kept during a sweep,
not *when* the sweep happens.

Manual/on-demand tools for inspecting or forcing this outside the
schedule:
```bash
openclaw memory promote [--apply] [--limit N]
openclaw memory promote-explain "query text"
openclaw memory status --deep
```
Output is written to `DREAMS.md` for human review. (The
`memory rem-backfill` commands previously listed here are for a different
purpose — one-time backfilling of pre-existing notes — not the recurring
schedule itself.)

Still not yet set on any device — needs a decision on which agent's
dreaming config to change (Pyramid, since it's meant to be the always-on
front door) and confirmation the setting actually took
(`openclaw config get plugins.entries.memory-core.config.dreaming`).

## 2. Stackchan MCP integration

**What Stackchan is:** a real, open-source AI desktop robot from M5Stack
(CoreS3 + ESP32-S3) — camera, dual mics, speaker, touch display, servo
movement. Fits directly into the existing ESP32-S3/Xiaozhi hardware
already on hand.

**The bridge:** [migratorywhale/stackchan-mcp](https://github.com/migratorywhale/stackchan-mcp) —
"Give your AI a body." An MCP server exposing 12 tools: photo capture,
audio transcription, text-to-speech, servo/movement control, facial
expressions. This is exactly the kind of tool an OpenClaw agent (or a
direct Claude Code MCP client) can be given access to.

There's also [kisaragi-mochi/stackchan-mcp](https://github.com/kisaragi-mochi/stackchan-mcp),
which specifically targets the xiaozhi-esp32 firmware path — worth a
closer look given the ESP32-S3 boards already confirmed plugged into
Pyramid are meant for a Xiaozhi-style voice front-end.

**Setup, per the bridge's own docs:**
- Server: `uv sync`, then set env vars for the robot's IP, the host
  machine's IP, and a Fish Audio API key (for TTS) — see `.env.example`
  in this repo's root. Copy it to `.env` (gitignored) and fill in real
  values there, never in a committed file.
- Client: the bridge provides ready-made config blocks for Claude Desktop,
  Claude Code CLI, Cursor, and others.

**Household requirement:** at least **2-3 physical units** —
1-2 personal ones for Bret, plus one shared unit for the rest of the
household (wife and kids). The bridge's own docs don't describe
multi-device or multi-user support out of the box, so this likely needs
one MCP server instance per physical robot, each configured with its own
`.env` block (see the duplicated-prefix note in `.env.example`) and
probably bound to a different agent — e.g. Bret's personal unit talking to
his own agent, the family unit talking to a shared/kid-safe one.

**Not yet decided:**
- Exactly how many physical Stackchan units, and which ESP32-S3 boards
  they'll use (two were already confirmed plugged into Pyramid, board
  mic/speaker capability still unverified — see
  `docs/session-notes/2026-08-25-session-summary.md`).
- Which agent each unit talks to — especially getting the family/kid unit
  right, since it's not just Bret using it.
- Where the MCP server(s) actually run — Pyramid, since it's the front
  door, is the natural candidate, but not yet confirmed.

## Sending real credentials

When Bret is ready to share the actual MCP codes/API keys: they go in a
local `.env` file (see `.env.example`), never pasted into a `.md` file or
committed to git. If shared in chat, they get used to configure the local
`.env` and are not written into any file this repo tracks.
