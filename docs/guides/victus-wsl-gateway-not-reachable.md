# Victus: companion app can't reach the WSL gateway

**Status: diagnosed, not yet fixed. Needs to be run on Victus itself — a
cloud/remote Claude Code session has no network path to Victus, same
limitation documented in `docs/openclaw-setup-2026-09-03.md`.**

## Symptom (reported 2026-09-16)

The OpenClaw companion app on the phone won't load/connect to Victus's
gateway. Bret confirmed the gateway runs inside **WSL** on Victus (not
native Windows) — that's the key detail.

## Root cause (very likely)

WSL2 puts itself on a private virtual network by default (NAT). A service
listening inside WSL — even if it binds to `0.0.0.0` — is reachable from
Windows itself, but **not** from other devices on the home WiFi (phone,
tablet), because Windows doesn't automatically expose the WSL network to
the LAN. This matches exactly: gateway runs fine, phone gets nothing.

This is unrelated to the `gateway.trustedProxies` fix from
`docs/session-notes/2026-08-25-session-summary.md` — that fixed a
different, later-stage auth misclassification issue. This one is more
basic: the connection isn't reaching the gateway at all.

## Fix, easiest first

### Option 1 — WSL mirrored networking mode (recommended)

Makes WSL share Windows' real network directly — no NAT, no port
forwarding, phone just works like talking to any other device on the LAN.
Requires a reasonably recent Windows 11 (with WSL mirrored networking
support).

On Victus, in a `.wslconfig` file at `C:\Users\<user>\.wslconfig`:

```ini
[wsl2]
networkingMode=mirrored
```

Then fully restart WSL (from PowerShell):

```powershell
wsl --shutdown
```

Reopen WSL/the gateway. Verify from the phone's companion app again.

### Option 2 — Windows port-forward (fallback if mirrored mode unavailable)

From an elevated PowerShell on Victus, find the WSL IP first:

```powershell
wsl hostname -I
```

Then forward the gateway's port (18789, or whatever Victus's gateway uses)
from the Windows host to that WSL IP:

```powershell
netsh interface portproxy add v4tov4 listenport=18789 listenaddress=0.0.0.0 connectport=18789 connectaddress=<WSL_IP_FROM_ABOVE>
netsh advfirewall firewall add rule name="OpenClaw Gateway" dir=in action=allow protocol=TCP localport=18789
```

Downside: `<WSL_IP_FROM_ABOVE>` can change on reboot, breaking the rule
again. Mirrored mode (Option 1) doesn't have this problem, so prefer it.

### Option 3 — Run OpenClaw natively on Windows, not inside WSL

Bigger change — sidesteps WSL networking entirely by not using WSL for
the gateway. Only worth it if Options 1 and 2 both fail.

## Who should run this

Bret cannot type. The cleanest path: open a local Claude Code session on
Victus itself (already documented in `docs/openclaw-setup-2026-09-03.md`:
`irm https://claude.ai/install.ps1 | iex` then `claude`) and talk it
through this file — a local session can actually check the Windows
version, edit `.wslconfig`, and verify the fix live, none of which a
remote/cloud session can do.

## Next time this comes up

Check this file before re-diagnosing from scratch. If Option 1 was tried
and the phone still can't connect, the next step is confirming Windows'
WSL version supports mirrored mode (`wsl --version`) before falling back
to Option 2.
