# OpenClaw automation concepts, pinned down (2026-09-13)

Four mechanisms sound similar and get confused easily. Verified against
docs.openclaw.ai directly — this is the real distinction.

| | What it is | Governs | Dispatches work? |
|---|---|---|---|
| **Cron-jobs / Automations** | The scheduler | **When** something runs (`--cron`, `--every`, `--at`) | Yes — each firing creates a task and, depending on payload kind, an agent turn |
| **Standing Orders** | Instructions injected into every session (`AGENTS.md` etc.) | **What the agent is allowed/expected to do** autonomously — scope, approval gates, escalation | No — configures behavior; something else still has to trigger the run |
| **Tasks** | An activity ledger | Nothing — a read/audit surface over what already happened | No — passively records |
| **Task Flow** | Orchestration above tasks, for multi-step pipelines | Coordinates several linked task records as one logical unit | Indirectly — coordinates, underlying tasks do the work |

Composition, as OpenClaw's own docs put it: **Automations (timing) →
deterministic steps → Task Flow (tracking/state) → background Tasks
(execution/ledger).** Standing Orders sit orthogonally on top, defining
what any of this is allowed to do on its own.

## Cron job payload kinds — pick the right one

```bash
openclaw automations add --system-event "<text>"      # enqueued, no model call
openclaw automations add --message "<text>"            # full agent turn (this is "give the agent a job")
openclaw automations add --command "<shell>"            # shell on the Gateway host, no model call
openclaw automations add --script <file>                # headless script using the owning agent's tools
```

## Facts that matter for THIS lab specifically

- **The Gateway process itself must stay running continuously** for any
  cron/automation to fire — it's not a separate OS cron daemon. This is
  exactly why the Pyramid gateway being down (per
  `docs/hardware/pyramid-gateway-handoff-2026-08-14.md`) would have
  silently broken every scheduled job too, not just live chat.
- Each cron run gets its **own fresh session** (`cron:<jobId>`) — it does
  not extend or reset the main chat session's idle/daily timers.
- `openclaw automations status` / `openclaw automations runs <jobId>
  --limit 20` / `openclaw doctor` are the real verification commands —
  "I set up automation X" is not confirmed until one of these shows an
  actual run.
- IMAP (`docs.openclaw.ai/automation/imap`) is a real alternative to the
  native Gmail webhook already documented in
  `docs/agent-jobs-backlog-2026-09-13.md` — it polls instead of using
  Google Pub/Sub, needs no Google Cloud project or public endpoint, and
  might be simpler if a non-Gmail account is ever in play. Same
  restricted-reader-agent pattern applies either way.
- **Dreaming (weekly memory folding) is one line of this same cron
  system** — see the correction in
  `docs/stackchan-mcp-and-memory-2026-09-03.md`.

## Sources (fetched live, 2026-09-13)

- [Automation overview](https://docs.openclaw.ai/automation)
- [How cron jobs work](https://docs.openclaw.ai/automation/cron-jobs/how-it-works)
- [Cron schedules](https://docs.openclaw.ai/automation/cron-jobs/schedules)
- [Cron payloads](https://docs.openclaw.ai/automation/cron-jobs/payloads)
- [Cron delivery](https://docs.openclaw.ai/automation/cron-jobs/delivery)
- [Inbound webhooks](https://docs.openclaw.ai/automation/cron-jobs/webhooks)
- [Cron troubleshooting](https://docs.openclaw.ai/automation/cron-jobs/troubleshooting)
- [Standing orders](https://docs.openclaw.ai/automation/standing-orders)
- [Task Flow](https://docs.openclaw.ai/automation/taskflow)
- [Tasks](https://docs.openclaw.ai/automation/tasks)
- [IMAP](https://docs.openclaw.ai/automation/imap)
- [Multi-agent concepts](https://docs.openclaw.ai/concepts/multi-agent)
- [Session concepts](https://docs.openclaw.ai/concepts/session)
