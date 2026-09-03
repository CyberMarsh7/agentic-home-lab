# Adding a Claude-backed agent to the Pyramid gateway (2026-09-03)

Goal: add a new OpenClaw agent, backed by Claude, on the Pyramid gateway
(`192.168.1.227`), alongside Samantha — without touching Samantha's existing
local-model setup.

## Background facts confirmed this session

- OpenClaw is real, open-source, at [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw),
  docs at [docs.openclaw.ai](https://docs.openclaw.ai/).
- Pyramid's real OpenClaw install: `/root/.npm-global/lib/node_modules/openclaw/dist/index.js`
  (do not use the stale `/usr/bin/openclaw`, v2026.6.10 — see
  `docs/hardware/pyramid-gateway-handoff-2026-08-14.md`).
- Access: `ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227`, sudo available.
- Control UI (browser, no SSH needed): `http://192.168.1.227:18789` →
  Settings → Connections → Model Providers (for API keys), or
  Agents & Tools → Agents / Models in the left sidebar.
- A cloud/remote Claude Code session has **no network path** to this LAN —
  confirmed by a direct connectivity test (curl to port 18789 timed out,
  no response). Any hands-on fix has to run from a **local** Claude Code
  session (installed directly on Victus or Pyramid) or be typed manually.

## Steps to add the "claude" agent

1. **Get an Anthropic API key** (only needed for the API-key auth path,
   not the CLI-subscription path below): console.anthropic.com/settings/keys.
   Requires a payment method on file — separate billing from any claude.ai
   subscription.

2. **Preferred path — reuse the existing Claude Code CLI login** (no API
   key needed, uses the Claude subscription instead): the Pyramid Control
   UI's Models page already showed a "Found on this Gateway" card for
   `claude-cli/claude-opus-5` with status "Credentials ready" once Claude
   Code was logged in locally.

3. **Create the new agent** (don't reuse Samantha's slot):
   ```bash
   ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227
   sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js agents add claude \
     --workspace /root/.openclaw/workspace-claude --model claude-cli/claude-opus-5
   sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway restart
   ```
   Verify: `agents list --bindings`, `models list --provider anthropic`.

4. **Pairing a phone/tablet to the gateway (companion app)** is separate
   from adding an agent — it's device-level, not per-agent:
   ```bash
   sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js qr
   ```
   Scan the printed QR (or enter the short setup code) in the OpenClaw
   companion app under Settings → Gateway. Once paired, the device can
   talk to any agent on that gateway, including the new "claude" one — no
   separate pairing per agent.

## Two open issues from this session (not yet resolved)

- **Pyramid: "can't create memory."** Likely cause: disk space or
  permissions on `/root/.openclaw/`. Diagnostic:
  ```bash
  ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 \
    "df -h; ls -la /root/.openclaw/; sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway status --deep"
  ```

- **Victus: now requires an API key** where it previously reused the CLI
  subscription login. Likely cause: expired/revoked local Claude CLI auth.
  Diagnostic:
  ```bash
  claude auth status --text
  claude /login
  ```

- **OpenClaw update to 2.0 blocked** with `handoff service not available`.
  This is a documented failure mode: OpenClaw can't find a trusted service
  identity to safely hand the update off to — common on hosts where the
  gateway was registered ad-hoc (`daemon install`) rather than through the
  proper systemd path, which matches Pyramid's history of a stale duplicate
  install. Recovery, in order:
  1. `gateway status --deep` — look for a `handoff.command` in the output
     and run that exact command if present.
  2. Otherwise: `gateway stop --force` → `update --no-restart` → `gateway start`.
  3. If that still fails, may need `gateway install` to properly register
     the service instead of the old `daemon install` path.

## Installing Claude Code locally (for real hands-on access)

A cloud/web Claude Code session can research, write docs, and prepare exact
commands, but cannot reach the home LAN. To get an assistant with real
local access on a machine (Victus, Pyramid, or the Kali Pi — same as
already set up on the Ubuntu box and Kali Pi):

```powershell
# Windows (Victus), in PowerShell
irm https://claude.ai/install.ps1 | iex
claude
```

```bash
# Linux (Pyramid, Kali Pi, Ubuntu box)
curl -fsSL https://claude.ai/install.sh | bash
claude
```

First run opens a browser login. No model selection needed at install —
change it later inside a session with `/model` if wanted. This is unrelated
to Ollama (which only runs the local models like phi4-mini/qwen2.5 used by
Samantha) — Claude Code doesn't need Ollama at all.
