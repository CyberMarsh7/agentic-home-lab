# How to actually give an OpenClaw agent a job (not just create one) — 2026-09-13

## Why this doc exists

Every prior doc in this repo (`openclaw-setup-2026-09-03.md`,
`restore-and-upgrade-runbook-2026-09-03.md`) only ever covers **creating and
configuring** an agent:

```bash
openclaw agents add <name> --workspace <dir> --model <id>
openclaw agents list --bindings
```

None of them cover **giving an already-configured agent a task to run**.
That's a different command, and the gap between the two is the reason work
kept getting done by whichever assistant Bret was talking to directly,
instead of by the OpenClaw agent it was supposed to go to — the agent
existed, but nothing ever actually dispatched a job to it, so it never
built up any track record or learning from real use.

Verified against the live docs at docs.openclaw.ai on 2026-09-13 (not
assumed, not from training data) — see sources at the bottom.

## The two commands, and when to use each

| Command | Purpose |
|---|---|
| `openclaw agents add/list/delete` | Manage **which agents exist** — config, model, workspace, routing bindings |
| `openclaw agent --agent <id> --message "..."` | Give **one existing agent** an actual task to work on right now |

**Rule going forward: if Bret says "have \<agent\> do X," the answer is a
`openclaw agent --agent <id> --message "X"` command, not the assistant
doing X directly in chat.** If no local session is available to run it
immediately, write the exact command down for Bret to say to whichever
local Claude Code / OpenClaw session he's actually talking to — never
substitute doing the task yourself as a stand-in for dispatching it.

## `openclaw agent` — full syntax

Session selector (pick one):
- `--to <dest>` — recipient to derive session key
- `--session-key <key>` / `--session-id <id>` — explicit session
- `--agent <id>` — the agent ID directly (overrides routing bindings — this
  is the one to use for "give agent X a job")

Message (pick one):
- `-m, --message <text>`
- `--message-file <path>` — for a longer task written out first

Useful flags:
- `--deliver` — send the reply back out to a channel/target (e.g. back to
  Bret's phone/companion app) instead of just returning it to the terminal
- `--reply-channel <channel>` / `--reply-to <target>` / `--reply-account <id>`
  — where to deliver the reply
- `--model <provider/model>` — override model for just this run
- `--local` — run the embedded agent directly rather than through the gateway
- `--timeout <seconds>` — default 600
- `--json` — machine-readable output

### Examples

```bash
# Give the "claude" agent on Pyramid a one-off task, reply back to the terminal
openclaw agent --agent claude --message "Summarize today's Kali Pi scan logs"

# Same, but deliver the reply to Bret's companion app / phone channel
openclaw agent --agent claude --message "Check gateway status --deep and report anything red" \
  --deliver --reply-channel <companion-channel> --reply-to <bret-device-id>

# Longer task, written to a file first (useful when dictating by voice —
# dictate the task into a file, then hand off the file path)
openclaw agent --agent samantha --message-file ./today-task.md
```

## Recurring jobs (the weekly-memory-folding case)

For anything that should happen on a schedule — like the weekly memory-fold
requirement in `docs/stackchan-mcp-and-memory-2026-09-03.md` — the dispatch
command above is still the right building block, wrapped in
`openclaw automations create`:

```bash
openclaw automations create "0 6 * * 1" \
  "Run the weekly memory fold: openclaw memory rem-backfill --path ./memory --stage-short-term" \
  --name "weekly-memory-fold" --agent claude --session isolated
```

```bash
openclaw automations list              # see what's scheduled
openclaw automations get <jobId>       # inspect one job
openclaw automations edit <jobId> --message "..." --model "..."
```

This still hasn't been set up on any device as of this doc — it's the
concrete next step for the weekly-folding requirement, now that the actual
dispatch mechanism is documented.

## Sources (fetched live, 2026-09-13)

- [CLI reference · OpenClaw](https://docs.openclaw.ai/cli)
- [Agents · OpenClaw](https://docs.openclaw.ai/cli/agents)
- [`openclaw agent` command reference · OpenClaw](https://docs.openclaw.ai/cli/agent)
- [Manage automations · OpenClaw](https://docs.openclaw.ai/automation/cron-jobs/managing-jobs)
