# Stackchan MCP integration + weekly memory folding (2026-09-03)

Two new requirements from Bret, recorded here so they don't get lost.

## 1. Weekly memory folding

**Requirement:** agents should fold/summarize their memory every 7 days —
preserve what conversations were about, not necessarily every raw message
forever.

**What OpenClaw actually offers today:** a background "dreaming" system
that consolidates short-term recall into long-term memory (`MEMORY.md`)
automatically — but it's **not time-based**. It promotes items based on
how often they're recalled and how varied the queries touching them are,
not on a calendar. Config keys that exist:

```
plugins.entries.memory-core.config.dreaming.enabled   # on by default
agents.defaults.compaction.memoryFlush.enabled          # flush before compaction
```

There's also a manual replay command for backfilling older notes into
long-term memory:
```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
openclaw memory rem-backfill --rollback   # to undo
```

**Gap:** none of this fires on a fixed weekly schedule by itself. To get
real 7-day folding, the likely path is a small scheduled job (cron, or an
OpenClaw automation hook) that runs the backfill/consolidation command
once a week, rather than relying on the score-based dreaming system alone.
Not yet built — needs a decision on which device runs the schedule
(Pyramid, since it's meant to be the always-on front door).

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
