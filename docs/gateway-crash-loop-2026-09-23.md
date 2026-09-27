# Gateway restarting every ~10 seconds, multiple OpenClaw instances on Tailscale (2026-09-23)

## Symptom (reported by Bret)

Can't connect to devices; suspects multiple OpenClaw installs across different
machines, all reachable over Tailscale, are conflicting. Gateway (unclear
which device — check all three: Pyramid, Victus, Kali Pi) restarts roughly
every 10 seconds.

## Real mechanism (verified against docs.openclaw.ai, not guessed)

OpenClaw enforces **one gateway process per state directory** via a lock file
at `$OPENCLAW_STATE_DIR/tmp/openclaw-<uid>`, using three layers: a state
ownership lock, a config lock, and an exclusive TCP socket bind on the
gateway port. If a second process tries to start against the same state dir
or port, you get exactly this kind of symptom — a crash and restart loop, not
a clean refusal — because the supervisor (systemd, or a daemon wrapper) keeps
trying to relaunch it.

Separately, OpenClaw has a **built-in crash-loop breaker**: after 3 unclean
boots within 5 minutes, it suppresses auto-started side services (channel
plugins etc.) on the next boot so a crashing gateway can't amplify itself.
That's a symptom, not the root cause — it means something upstream is
already crash-looping badly enough to trip this.

**Most likely root cause, given this lab's specific history:**
Pyramid has two OpenClaw installs on disk (`/usr/bin/openclaw`, stale, vs.
the real `/root/.npm-global/lib/node_modules/openclaw/dist/index.js` — see
`docs/hardware/pyramid-gateway-handoff-2026-08-14.md`). If both ever got
registered as a running service (one via the old ad-hoc `daemon install`,
one via a proper `gateway install`), they'd fight over the same port/lock on
that single machine — this does not require Tailscale to cause it, Tailscale
just makes the resulting instability visible/reachable from other devices,
which likely explains "can't connect... due to multiple OpenClaw."

Being on the same tailnet does NOT normally cause cross-machine gateway
conflicts by itself — each physical device binds its own local port. The
conflict, if it's cross-machine at all, would only happen if two gateways
were misconfigured to share one `OPENCLAW_STATE_DIR` (e.g. over a synced
folder) — worth checking, but the single-machine duplicate-install
explanation is more likely per this repo's own history.

## Diagnostic path (per device, run locally — same access limitation as
everything else in this repo: this has to run from a local session)

```bash
# 1. Is more than one openclaw process running on THIS machine?
ps aux | grep -i openclaw | grep -v grep

# 2. What's actually bound to the gateway port?
lsof -i :18789   # or: ss -tlnp | grep 18789

# 3. Check the lock file itself
ls -la "${OPENCLAW_STATE_DIR:-$HOME/.openclaw/state}/tmp/"

# 4. Is the recorded lock PID actually alive?
#    (use the pid printed by step 1 or found in the lock dir)
ps -p <pid>

# 5. Full health/crash-loop status
openclaw gateway status
openclaw doctor
```

Look specifically for the two openclaw binaries on Pyramid both being
registered as services:
```bash
sudo systemctl list-units | grep -i openclaw    # Linux/systemd
which -a openclaw                                # shows every openclaw on PATH
```

## Fix, once the duplicate is confirmed

1. Stop and disable whichever service is the stale/duplicate one (the
   `/usr/bin/openclaw` one on Pyramid, per its known history).
2. `openclaw gateway install --force` to re-register the real service
   cleanly against the correct binary/state dir.
3. `openclaw gateway restart`, then re-run the diagnostic path above to
   confirm only one process holds the lock and the port stays bound.

If it turns out to genuinely be two different machines sharing one state
directory (unlikely, but checkable): give each its own
`OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` per
`docs.openclaw.ai/gateway/multiple-gateways`, already summarized in
`docs/openclaw-open-issues-diagnosis-2026-09-13.md`.

## Sources (fetched live, 2026-09-23)

- [Gateway lock](https://docs.openclaw.ai/gateway/gateway-lock)
- [Gateway restart & recovery](https://docs.openclaw.ai/gateway/restart-recovery)
- [Multiple gateways](https://docs.openclaw.ai/gateway/multiple-gateways)
