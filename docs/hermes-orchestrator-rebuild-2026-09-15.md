# Rebuilding Hermes as master orchestrator (2026-09-15)

Goal: bring Hermes back on Virgil, not as a standalone agent competing with
Samantha again, but as the thing Bret talks to that then drives both
OpenClaw gateways on his behalf — so scheduling a job is a sentence, not a
CLI session.

**Naming note:** this doc uses the names Bret used when asking for this
(Dante, Virgil) because that's what he'll say out loud. They map onto the
devices already documented elsewhere in this repo like this:

| This doc calls it | Repo's existing name | Agent(s) on it |
|---|---|---|
| **Dante** | Pyramid (aka "Oracle") — `192.168.1.227` | Oracle (was being set up as `claude`, `claude-cli/claude-opus-5`) |
| **Virgil** | Victus (HP laptop, RTX 4050 / 6GB VRAM) | Samantha (local `qwen2.5:3b-instruct`), + Hermes (this rebuild) |

If "Dante" and "Virgil" are meant to *replace* the Pyramid/Victus names
going forward rather than just be nicknames, say so next session and this
repo's device table should be renamed throughout — not done here, to avoid
silently rewriting history in docs that other sessions still reference by
the old names.

**Assumption flagged for correction:** the task description says Virgil
"previously ran Hermes (agent name 'Samantha')" — but the repo's own
history (`README.md`, `docs/session-notes/2026-08-25-session-summary.md`)
shows **Samantha and hermes as two separate agents** on Victus: Samantha is
the hardened local-model agent, hermes was a second, separate slot that got
stopped for competing with her over the 6GB of VRAM. This plan treats them
as still separate — Samantha keeps running untouched, Hermes comes back as
a new, additional agent slot. Correct me if that's wrong.

## Why the old Hermes died, and why this rebuild doesn't repeat it

The 2026-08-24/25 session notes are explicit: Hermes was killed because it
was running a local model and fighting Samantha for the same 6GB of GPU
VRAM on Virgil. **This rebuild backs Hermes with the Claude Code CLI
subscription login instead of a local Ollama model** — the same
`claude-cli/claude-opus-5` pattern already proven working for the `claude`
agent on Dante (`docs/openclaw-setup-2026-09-03.md`). That means:

- Zero VRAM footprint. Hermes cannot re-trigger the original failure mode,
  structurally, not just by promise.
- No new API key or subscription cost — reuses the existing Claude Code
  login already on Virgil.
- Orchestration reasoning (routing, job-wording, multi-step planning)
  benefits from a stronger model than the 3B local one anyway.

## Architecture in one paragraph

Hermes runs as its own OpenClaw agent on Virgil. It reaches Virgil's own
gateway over loopback and Dante's gateway over Tailscale — **not** a wider
LAN bind, and **not** a manual SSH tunnel per request (that fails the
voice-only requirement). Two channels do the actual work: an MCP bridge
into each gateway's live conversations for routing tasks and reading
replies, and direct `openclaw automations` (cron) CLI calls against each
gateway's WebSocket URL for creating/editing/removing scheduled jobs. Both
channels are built into OpenClaw itself — nothing here is a custom API
layer Bret has to maintain.

```
Bret (voice) --> Hermes (Virgil, claude-cli agent)
                     |
                     +-- MCP bridge --> Virgil gateway (loopback)   --> Samantha
                     +-- MCP bridge --> Dante gateway (tailnet)     --> Oracle
                     |
                     +-- `openclaw automations ...--url wss://<host>:18789`
                             (job create/edit/list/remove on either gateway)
```

---

## Part 1 — Expose both gateways safely, without SSH tunnels

The constraint doc mentions `openclaw config set gateway.bind lan` to get
past loopback-only. **Don't use `lan`** — that binds `0.0.0.0`, i.e. the
whole home network, not just the tailnet. OpenClaw has a purpose-built
option for exactly this case:

```bash
openclaw config set gateway.bind tailnet
```

This binds the gateway to the machine's Tailscale IPv4 address specifically
(falls back to loopback if Tailscale isn't up), so it's reachable from any
other device on the tailnet — Virgil, Dante, phone, iPad — and from
nowhere else. Run this **on both Dante and Virgil**, then restart each
gateway:

```bash
# On Dante
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 \
  "sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js config set gateway.bind tailnet && \
   sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway restart"

# On Virgil (run locally)
openclaw config set gateway.bind tailnet
openclaw gateway restart
```

Source: [OpenClaw gateway config](https://docs.openclaw.ai/gateway/config-gateway) —
`bind` accepts `loopback` (default), `lan` (`0.0.0.0`), `tailnet`
(Tailscale IPv4, falls back to loopback), or a `custom` IPv4.

### Auth: new scoped keys, not the existing tokens

Constraint says don't rotate existing Tailscale tokens — this doesn't touch
Tailscale auth at all, only OpenClaw's own gateway auth, and it doesn't
rotate that either. Each gateway gets one *new, additional* named key for
Hermes to use, leaving whatever token the existing companion apps/UI use
untouched:

```bash
# On Dante — creates a key just for Hermes, doesn't touch the existing one
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 \
  "sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway keys create --name hermes-orchestrator --expires 365d"

# On Virgil
openclaw gateway keys create --name hermes-orchestrator --expires 365d
```

Save each printed key into its own token file on Virgil (where Hermes
runs), e.g. `~/.openclaw/tokens/hermes-to-dante.token` and
`~/.openclaw/tokens/hermes-to-virgil.token` — never commit these, never
paste them into a `.md` file (same rule this repo already uses for the
Stackchan `.env`, per `docs/stackchan-mcp-and-memory-2026-09-03.md`).

Source: [OpenClaw gateway authentication](https://docs.openclaw.ai/gateway/authentication) —
`gateway keys create --name <name> --expires <duration>` issues an
independent, expiring key without touching the primary token.

---

## Part 2 — Create the Hermes agent (fully CLI, no wizard)

Same non-wizard pattern already proven for the `claude` agent on Dante
(`docs/openclaw-setup-2026-09-03.md`) — `openclaw agents add` creates a
fully-configured agent in one command, no setup wizard involved:

```bash
# Run locally on Virgil
openclaw agents add hermes \
  --workspace ~/.openclaw/workspace-hermes \
  --model claude-cli/claude-opus-5
openclaw gateway restart
```

Verify: `openclaw agents list --bindings`, `openclaw models list --provider anthropic`.

### Give it the orchestrator persona (also no wizard — plain text files)

OpenClaw agents load a fixed set of bootstrap files from their workspace at
session start: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`. Writing
these is a file write, not a GUI step:

```bash
cat > ~/.openclaw/workspace-hermes/SOUL.md <<'EOF'
You are Hermes, the master orchestrator across Bret's OpenClaw fleet.
You do not just answer questions — when Bret asks for something scheduled,
you create/edit/remove the actual automation job yourself via the
`openclaw automations` CLI against the right gateway. You never hand back
copy-paste CLI instructions for Bret to run himself; he operates by voice
only and cannot type or run commands. Route vision/visual-skill tasks to
Oracle on Dante; keep everything else local to Virgil unless Oracle is
unreachable, in which case say so and do the best you can locally.
EOF
```

Source: [OpenClaw system prompt](https://docs.openclaw.ai/concepts/system-prompt),
[Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) —
`SOUL.md`/`AGENTS.md`/`IDENTITY.md`/`USER.md` are loaded every session as
the persona/instruction layer; no wizard touches these.

**Flagged manual step:** none so far. Everything above is SSH/CLI only.

---

## Part 3 — The actual job-scheduling integration layer

This is the piece that replaces "OpenClaw hands back copy-paste
instructions." `openclaw automations` (alias `openclaw cron`) already
accepts `--url <ws-url>` to target a **remote** gateway — this is a real,
documented capability, not something built for this plan:

```bash
openclaw automations add "every 1h" "check the mailbox sensor and alert if it's been open >10 min" \
  --agent oracle --url wss://<dante-tailscale-ip>:18789 --token-file ~/.openclaw/tokens/hermes-to-dante.token

openclaw automations add "0 9 * * 1" "summarize last week's home lab session notes" \
  --agent hermes --url wss://127.0.0.1:18789 --token-file ~/.openclaw/tokens/hermes-to-virgil.token

openclaw automations list --all --url wss://<dante-tailscale-ip>:18789 --token-file ~/.openclaw/tokens/hermes-to-dante.token
openclaw automations edit <job-id> --agent oracle --url wss://<dante-tailscale-ip>:18789 --token-file ~/.openclaw/tokens/hermes-to-dante.token
openclaw automations remove <job-id> --url wss://<dante-tailscale-ip>:18789 --token-file ~/.openclaw/tokens/hermes-to-dante.token
```

**How this becomes "Hermes just does it":** Hermes has ordinary shell/exec
access as part of its agent capabilities (same mechanism Samantha and the
`claude` agent already have, gated by `exec-policy`). When Bret says
"schedule the mailbox check hourly on Dante," Hermes runs the
`openclaw automations add ... --url wss://<dante> ...` command itself and
reports back in plain language — it does not print the command for Bret to
copy. Its `SOUL.md` above states this explicitly because it's the exact
failure mode being fixed.

Source: [OpenClaw automations/cron CLI](https://docs.openclaw.ai/cli/cron) —
"Every automation subcommand accepts the shared Gateway connection
options... `--url <url>` for an explicit WebSocket URL," schedules accept
cron syntax, `every 1h`/`20m` shorthand, or `--at` for one-shot ISO
timestamps.

### Live routing (not just scheduled jobs): the MCP bridge

For "route this visual task to Dante right now," Hermes needs live
conversation access, not just cron. OpenClaw can run itself as an MCP
server bridged to a remote gateway over the same WebSocket/token auth:

```bash
openclaw mcp serve --url wss://<dante-tailscale-ip>:18789 --token-file ~/.openclaw/tokens/hermes-to-dante.token
openclaw mcp serve --url wss://127.0.0.1:18789 --token-file ~/.openclaw/tokens/hermes-to-virgil.token
```

Register both as MCP servers in Hermes's own agent config (two entries —
one remote bridge process can only carry one gateway connection at a time,
per the docs, so it's one process per target, not one shared process).
That gives Hermes the tools `messages_send`, `messages_read`,
`conversations_list`, `events_poll`/`events_wait`, and
`permissions_list_open`/`permissions_respond` against **both** gateways —
enough to hand a task to Oracle and read the reply back, or approve a
pending exec request on either box, without SSH.

**What's explicitly not available this way:** cron/job management is not
exposed over MCP (confirmed against the docs — the MCP tool set is
conversation/message/permission-only). That's why job scheduling goes
through the `openclaw automations --url` CLI path above instead, run
directly by Hermes's own shell access.

Source: [Run OpenClaw as an MCP server](https://docs.openclaw.ai/cli/mcp/serve) —
tool list confirmed as `conversations_list`, `conversation_get`,
`messages_read`, `attachments_fetch`, `events_poll`, `events_wait`,
`messages_send`, `permissions_list_open`, `permissions_respond`; explicitly
no agent/cron management; "HTTP/SSE/streamable-http transport connects to
a single remote server" (current limit), so stdio + one process per target
is the correct shape today.

---

## Part 4 — Seeing the fleet at a glance (the orphan-instance fix)

The failure mode last time was untracked OpenClaw instances with no clear
owner. Two things fix that together:

1. **One registry, in this repo** — the table below is the source of
   truth for "what's supposed to exist." Anything live that isn't in this
   table is an orphan by definition; anything in this table that doesn't
   respond is down, not gone.

2. **One script, `scripts/fleet-status.sh`** (added in this change) — run
   it from Virgil and it checks both gateways' real state (`gateway status
   --deep`, `agents list --bindings`, `automations list --all`) against
   this same registry and prints a short table with anything mismatched
   flagged. Bret can ask Hermes to "run the fleet check" instead of typing
   anything.

### Current registry (update this table whenever an agent is added/removed)

| Host | Gateway reach | Agent | Backed by | Owner/status |
|---|---|---|---|---|
| Dante (Pyramid, `192.168.1.227`) | tailnet | Oracle | `claude-cli/claude-opus-5` | standalone, vision/visual-skill tasks |
| Virgil (Victus) | loopback + tailnet | Samantha | local `qwen2.5:3b-instruct` | standalone, hardened, do not touch |
| Virgil (Victus) | loopback + tailnet | Hermes | `claude-cli/claude-opus-5` | **orchestrator** — this rebuild |

Run `scripts/fleet-status.sh` after finishing Parts 1–3 to confirm the live
state matches this table, and again any time something seems off.

---

## Manual/GUI steps, called out explicitly (so there are no surprises)

Everything in Parts 1–4 is copy-paste-safe, single-line, SSH/CLI-only —
none of it touches the setup wizard. Two things genuinely can't be done by
voice/CLI, both one-time and unrelated to the wizard:

1. **Companion phone/tablet pairing**, if not already paired to the new
   `hermes-orchestrator` key — this still needs a QR scan or manually
   typing a short code into the app once (`openclaw qr`, per
   `docs/openclaw-setup-2026-09-03.md`). Not required for Hermes's
   orchestrator role itself, only if Bret wants to talk to Hermes directly
   from the phone app.
2. **First-time Claude Code CLI login on Virgil**, if the existing login
   has expired (flagged as an open issue in
   `docs/openclaw-setup-2026-09-03.md` — "Victus now requires an API key
   where it previously reused the CLI subscription login"). This opens a
   browser once (`claude /login`). If Virgil's login is still valid, this
   step is skipped entirely.

The setup wizard itself is not used anywhere in this plan — every step
above is `openclaw agents add` / `openclaw config set` / `openclaw gateway
keys create` / `openclaw automations add`, all scriptable, all things
Hermes itself can eventually run on Bret's behalf once it exists.

## Verification checklist

```bash
# Both gateways reachable over tailnet, not just loopback
curl -s -o /dev/null -w 'Dante  %{http_code}\n' http://<dante-tailscale-ip>:18789/
curl -s -o /dev/null -w 'Virgil %{http_code}\n' http://127.0.0.1:18789/

# Hermes exists and is bound to the claude-cli model (no VRAM use)
openclaw agents list --bindings | grep -i hermes

# A real remote cron round-trip against Dante
openclaw automations add --at "$(date -u -d '+2 minutes' +%FT%TZ)" "say hello, this is a test from Hermes" \
  --agent oracle --url wss://<dante-tailscale-ip>:18789 --token-file ~/.openclaw/tokens/hermes-to-dante.token
openclaw automations list --all --url wss://<dante-tailscale-ip>:18789 --token-file ~/.openclaw/tokens/hermes-to-dante.token

# Fleet status agrees with the registry table above
bash scripts/fleet-status.sh
```

## Sources

- [Automations (cron) CLI](https://docs.openclaw.ai/cli/cron)
- [Run OpenClaw as an MCP server](https://docs.openclaw.ai/cli/mcp/serve)
- [Gateway configuration — `bind`](https://docs.openclaw.ai/gateway/config-gateway)
- [Gateway authentication — keys](https://docs.openclaw.ai/gateway/authentication)
- [System prompt / bootstrap files](https://docs.openclaw.ai/concepts/system-prompt)
- [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace)
- This repo: `docs/openclaw-setup-2026-09-03.md`, `docs/restore-and-upgrade-runbook-2026-09-03.md`, `docs/session-notes/2026-08-25-session-summary.md`
