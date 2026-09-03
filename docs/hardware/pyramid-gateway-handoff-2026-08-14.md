# Pyramid Gateway — Status and Handoff (2026-08-13/14)

**The complaint:** Bret said "the pyramid does nothing" — screen shows nothing happening, has been broken for weeks.

## What was found

Diagnosed live via SSH from the Victus laptop:

1. The Pyramid (device at `192.168.1.227`, SSH as `marshinpyramid` with key `~/.ssh/pyramid_ed25519`, sudo available) had its OpenClaw gateway service **disabled and stopped**. Not crashed — clean exit (last exit 0). It just never got turned back on since a fix from an earlier session (2026-08-12) that registered it as enabled.

2. Because the gateway was down, port `18789` didn't respond (confirmed via curl — HTTP 000, connection refused). Meanwhile the Pyramid's kiosk Firefox had been endlessly relaunching itself against that dead backend since ~01:41 that day — many duplicate Firefox process trees piling up. That's what "does nothing" looks like on the physical screen: Firefox stuck on connection-refused pages, over and over.

3. There was also an orphaned process pair stuck since 02:30 that day: PID `716498` (openclaw) and its child PID `716506` (openclaw-doctor), pegging 123% CPU with no terminal attached (nobody watching it, 0 logged-in users). System load average was 13+ on this small ARM board as a result — likely from someone's earlier troubleshooting attempt that got stuck/wedged and was never cleaned up.

4. **Important gotcha (confirmed still true):** there are TWO openclaw installs on the Pyramid.
   - Bare `openclaw` in PATH → `/usr/bin/openclaw` → **stale**, version 2026.6.10. Don't use this.
   - The real, running one → `/root/.npm-global/lib/node_modules/openclaw/dist/index.js` → version 2026.7.1-2. **Always use this explicit path.**

## The fix (two commands, run from Victus or anywhere with the SSH key)

Step 1 — kill the stuck orphaned process pair (verify these PIDs are still current first, since they can change if anything rebooted since diagnosis):

```bash
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 "ps aux | grep openclaw"
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 "sudo kill -TERM 716506 716498"
```

Step 2 — reinstall/re-enable the gateway service (this is the exact fix that worked on 2026-08-12, just needs to be redone):

```bash
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 "sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js daemon install"
```

## Verify it worked

```bash
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 "sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js daemon status"
```

Should show "Runtime: running" (not "stopped"). Also:

```bash
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 "curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:18789/"
```

Should show HTTP 200, not HTTP 000. Firefox on the Pyramid should recover within its next retry cycle, or may need a manual page reload.

## Why a remote/cloud Claude session can't just run this

A safety classifier blocks both (a) running sudo/service commands directly on a remote machine, and (b) editing that machine's own settings to grant itself permission to run them — intentionally, so a safety tool can't edit its own permissions to unblock itself. This needs to run from a **local** Claude Code session that already has the right permissions (installed directly on Victus or Pyramid), or be run manually.

## Separate, unrelated thread (paused, not this issue)

There's also a whole separate investigation about OpenClaw being installed on both the Pyramid and the Victus laptop under one account, and a "hermes"/Samantha install on Victus that needs to stay untouched. Saved separately as `project_batcave_openclaw_victus_split.md` — do not mix the two up. The 2026-08-13/14 complaint ("pyramid does nothing") was the gateway-down issue above, not that one.
