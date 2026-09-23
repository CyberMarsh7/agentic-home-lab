# Agent preset shelf

One folder per role. Deploy any of them with:
```bash
./select-and-deploy-model.sh --role <role> --agent <agent-id> --apply
```
That picks the right-sized model for whatever machine you run it on and
stamps out a ready-to-merge config. Each role also carries a
`trigger.json` explaining the *other* one-time setup it needs — none of
these are "fully wired" just by running the deploy command; the trigger
is always separate and explicit, never assumed.

| Role | What it does | Tool access | Trigger mechanism |
|---|---|---|---|
| `email` | Reads Gmail, reports what needs attention | Locked down: no fs/exec/web | Native Gmail webhook (event-driven) |
| `texts` | Same, for SMS | Locked down: no fs/exec/web | Channel binding (needs SMS plugin configured first) |
| `system-updates-linux` | Checks/applies Linux package updates | Real exec, gated on approval | On-demand, dispatched by voice/CLI |
| `system-updates-windows` | Same, for Victus (the one Windows box) | Real exec, gated on approval | On-demand |
| `installer` | Installs software from GitHub or a package manager | Real exec + write, gated on approval | On-demand, always one-off |
| `esp32-node` | Not its own agent — pairs a bare physical button to an *existing* agent | N/A (binding, not a new agent) | Node pairing (`devices approve` + `nodes approve`) |
| `stackchan` | Full embodied unit — camera, servo, speaker, expressions | Stackchan MCP tools only, still no fs/exec/web | Node pairing + its own dedicated agent per physical unit |
| `gateway-health-watch` | Watches for the crash-loop pattern from `docs/gateway-crash-loop-2026-09-23.md`, silent unless something's wrong | Exec, but `allowlist`-scoped to read-only diagnostic commands only (see note below) | Real cron, every 15 min |
| `daily-briefing` | Summarizes recent memory notes once a day | Read-only, no exec at all | Real cron, once daily |

## Safety pattern, stated once so it doesn't get diluted per-role

Two tiers, on purpose:
- **Read-only roles** (email, texts, stackchan) get `deny: [group:fs, group:runtime, group:web]` — they cannot do anything destructive even if asked to, by design.
- **Roles that touch the system** (system-updates-*, installer) get real `exec`, but `tools.exec.mode: "ask"` — every single command needs Bret's approval. Never flip this to `"allowlist"` or unrestricted without a specific, considered reason; package managers and installers can break a running machine.
- **One deliberate exception: `gateway-health-watch`.** It runs unattended on a cron schedule, so `"ask"` would just hang forever with nobody there to approve it. It uses `"allowlist"` instead, restricted to genuinely read-only diagnostic commands (`gateway status`, `doctor`, `ps`, a port check) — nothing destructive is on that list. This is the specific, considered reason the rule above allows for, not a loosened default to copy elsewhere.

## Adding a new role

1. `mkdir agent-presets/<role>`
2. `agent-template.json` — one config, `__MODEL__` and `__AGENT_ID__` as the only placeholders (the deploy script fills them in — never make more than one copy per role for different model sizes).
3. `AGENTS.md` — what this role actually does and its real limits, not a wish list.
4. `trigger.json` — the *real* mechanism this role needs (cron, webhook, channel binding, node pairing, or on-demand dispatch) — pick the one that's actually true for this role, don't force every role into the same shape.
5. Add a row to the table above.
