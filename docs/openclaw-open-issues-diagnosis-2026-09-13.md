# The three open issues, actually diagnosed (2026-09-13)

Supersedes the guesses in `docs/openclaw-setup-2026-09-03.md`'s "two open
issues" section and `docs/restore-and-upgrade-runbook-2026-09-03.md`'s
Phase 2 with real mechanisms, verified against docs.openclaw.ai. These are
still **not fixed** — this is the diagnosis, to be run and confirmed from
a local session, not a claim that they're resolved.

## Honesty note on sourcing

The exact phrase "handoff service not available" does not appear anywhere
in OpenClaw's official docs. A deeper search surfaced what looked like
matching GitHub issue content, but that source also reported an
implausible star count for the project (a strong sign of fabricated or
spoofed content) — so that specific error string is **not confirmed** and
should not be repeated as fact until it's seen directly in output from
`openclaw doctor` or `openclaw update --json` on the actual hardware. What
follows instead is the real, documented mechanism underneath that failure
class, which is enough to diagnose and fix it regardless of the exact
wording.

## 1. OpenClaw 2.0 update stuck

**Real mechanism** (`docs.openclaw.ai/cli/update`, verbatim): the updater
launches native service install/restart/stop *through the target CLI*,
and that CLI process must "retain the original update owner while their
child processes settle." It explicitly **refuses** to fall back to an
unmanaged or detached restart (including the Windows Startup-folder path)
that can't preserve that ownership — it fails closed rather than
guessing. Likely triggers on Pyramid specifically: the known duplicate
install (`/usr/bin/openclaw` stale vs. the real
`/root/.npm-global/.../openclaw/dist/index.js` path) could confuse which
binary the updater treats as "the target CLI."

**Fix path, in order:**
```bash
openclaw gateway status --deep
openclaw update status
openclaw doctor --fix
# still stuck:
openclaw triage              # spawns a diagnostic agent specifically for failed updates
# last resort, the documented "post-upgrade fix-all":
openclaw gateway install --force
openclaw gateway restart
```
On Linux, confirm the systemd unit has `KillMode=mixed` — required for the
graceful 5-minute drain the update process depends on.

## 2. Pyramid "can't create memory"

**This was never actually disk-space, most likely** — the original
2026-09-03 doc guessed disk/permissions with no real evidence. The
documented mechanism that produces exactly this symptom is tool policy,
not disk:

> "deny always wins. If `allow` is non-empty, everything else is
> blocked." (`docs.openclaw.ai/gateway/sandbox-vs-tool-policy-vs-elevated`)

Memory tools sit behind a `group:memory` allow entry. If a `tools.allow`
list got set anywhere in that agent's config chain (global `tools.allow`,
a per-agent `tools.profile`, or `tools.byProvider[provider].allow`)
without including `group:memory`, memory silently disappears along with
everything else not explicitly listed — with no loud error, which matches
"can't create memory" being reported as a vague failure rather than a
clear permission-denied message.

**Diagnostic path:**
```bash
openclaw config get agents.entries.<agent-id>.tools --json
openclaw config get tools.allow --json
openclaw config get agents.defaults.sandbox.workspaceAccess --json
openclaw doctor --lint
openclaw policy check
```
If any `tools.allow` is non-empty and missing `group:memory`, add it back;
also confirm `sandbox.workspaceAccess` isn't `"none"`/`"ro"` if the memory
write itself needs filesystem access. Only fall back to checking actual
disk space (`df -h`, `ls -la /root/.openclaw/`) if the tool-policy check
comes back clean.

## 3. Victus: CLI-subscription auth silently demanding an API key

**Confirmed root cause** (`docs.openclaw.ai/cli/models`): for the
Anthropic path, OpenClaw "prefers reusing the Claude CLI (`claude -p`) on
the host when it is available" rather than keeping its own OAuth session.
If that local `claude` CLI becomes unreachable, unauthenticated, or its
own login session expires, OpenClaw has **no loud error for this** — it
just falls through to asking for a `setup-token`/`paste-token`/API key,
which is exactly the symptom reported.

Three other silent-fallback triggers exist
(`docs.openclaw.ai/auth-credential-semantics`), any of which could also be
in play after the reflash/restore history this lab has:
- `selected_auth_profile_unavailable` — a stored auth profile got removed
- `AUTH_PROFILE_MIGRATION_REQUIRED` — a leftover legacy
  `auth-profiles.json` sitting next to an *empty* SQLite store blocks
  OAuth for that provider entirely until migrated
- `excluded_by_auth_order` — a stored OAuth profile exists but isn't
  listed in `auth.order.<provider>`, so it's never retried automatically

**Diagnostic path:**
```bash
claude auth status --text        # is the local Claude CLI itself actually logged in?
openclaw models status --agent <agentId> --json --check
openclaw models auth list --provider anthropic
openclaw doctor --fix
```
Check whether both a legacy `auth-profiles.json` and `openclaw-agent.sqlite`
exist side by side on Victus — that specific combination is the migration
trap above, and given this lab's history of reflashes and restores, it's
a real candidate.

## Sources (fetched live, 2026-09-13)

- [CLI: update](https://docs.openclaw.ai/cli/update)
- [CLI: doctor recovery](https://docs.openclaw.ai/cli/doctor/recovery)
- [Gateway: restart & recovery](https://docs.openclaw.ai/gateway/restart-recovery)
- [Gateway: sandbox vs tool policy vs elevated](https://docs.openclaw.ai/gateway/sandbox-vs-tool-policy-vs-elevated)
- [Gateway: sandboxing](https://docs.openclaw.ai/gateway/sandboxing)
- [CLI: models](https://docs.openclaw.ai/cli/models)
- [Auth credential semantics](https://docs.openclaw.ai/auth-credential-semantics)
- [Gateway: troubleshooting](https://docs.openclaw.ai/gateway/troubleshooting)
- [CLI: security](https://docs.openclaw.ai/cli/security)
- [CLI: policy](https://docs.openclaw.ai/cli/policy)
