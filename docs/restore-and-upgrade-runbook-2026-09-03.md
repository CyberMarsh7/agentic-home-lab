# Restore agents + upgrade to OpenClaw 2.0 — runbook (2026-09-03)

Goal: get every agent back for the family, and upgrade Pyramid's gateway to
OpenClaw 2.0 in place. Run this from the **local** Claude Code session on
Victus (a cloud/web session has no path to this LAN — see
`docs/openclaw-setup-2026-09-03.md`).

Give the whole block below to that local session and let it work through it
in order — inventory first, so nothing gets rebuilt that isn't actually
broken.

## Phase 1 — Inventory: what's actually still alive

```bash
# Pyramid
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227 \
  "sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway status --deep; \
   sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js agents list --bindings; \
   df -h; ls -la /root/.openclaw/"

# Victus (run directly, not over SSH)
ollama list
openclaw agents list --bindings   # or the local Victus equivalent of the openclaw binary
claude auth status --text

# Kali Pi
ssh marshinpi-1 "sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway status --deep 2>&1 || openclaw gateway status --deep"
```

Report back what's actually missing vs. what's still there before rebuilding
anything — Victus wasn't reflashed, so Samantha and hermes may well still be
intact even though the Pyramid(s) were.

## Phase 2 — Fix the OpenClaw 2.0 update blocker on Pyramid

The `handoff service not available` error means OpenClaw can't find a
trusted service identity to safely hand the update to — likely because the
gateway was registered ad-hoc (`daemon install`) instead of through the
proper systemd path.

```bash
ssh -i ~/.ssh/pyramid_ed25519 marshinpyramid@192.168.1.227

# 1. Check for a handoff.command in the deep status output — run that exact
#    command if present, it's tailored to this exact host. Otherwise:

sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway stop --force
sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js update --no-restart

# 2. If it still won't take, register properly as a systemd service instead
#    of the old ad-hoc daemon install, then retry:
sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway install
sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway start

# 3. Confirm the version actually moved to 2.0:
sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js gateway status
```

Do this on Pyramid before rebuilding any agents on it — no point configuring
agents on a gateway version you're about to replace out from under them.

## Phase 3 — Rebuild whatever Phase 1 showed as actually missing

**Samantha** (Victus, local model) — should still exist since Victus wasn't
reflashed. If gone, recreate per `docs/session-notes/2026-08-25-session-summary.md`:
- Model: `qwen2.5:3b-instruct` (fits the RTX 4050's 6GB VRAM — larger models
  were tried and misfired or were too slow)
- Web/browser tools: disabled
- `exec-policy`: `cautious`
- Remove any `greet-christopher` skill if it resurfaces (it caused a
  wrong-name bug before)

**hermes** (Victus) — was intentionally stopped, not deleted, last session.
Restart it the normal way; its default model was already lightened in config.

**Oracle / Pyramid's own agent** — rebuild after Phase 2's upgrade lands, on
the new 2.0 config format (config schema may differ between versions — check
`openclaw doctor` output on 2.0 before assuming the 1.x config still applies
as-is).

**Kali Pi agent** — per Phase 1 inventory: if the Pi itself wasn't reflashed,
this one likely survived. If it was, reinstall OpenClaw fresh per the
original setup (routes inference to Victus's Ollama over Tailscale — it has
no GPU/NPU of its own).

**claude agent** (the new one from earlier today) — rebuild on Pyramid
post-upgrade using `claude-cli/claude-opus-5`, same as
`docs/openclaw-setup-2026-09-03.md` describes — the auth backend (Claude
Code CLI login) is independent of the OpenClaw gateway version.

## Phase 4 — Learning OpenClaw 2.0

Once 2.0 is running, the concrete things worth learning, roughly in order
of how often you'll actually use them day to day:

1. **Daily health check** — `gateway status --deep`, and the Control UI's
   home page at `http://192.168.1.227:18789`.
2. **Agents page** — how to see what's running, restart one agent without
   restarting the whole gateway.
3. **Models page** — swapping which model an agent uses (this is where the
   Claude Code card, Ollama models, etc. all show up).
4. **Updating safely going forward** — always `gateway status --deep`
   *before* running `update`, so a handoff problem is caught before it
   blocks mid-update rather than during.
5. **Companion app** — QR/setup-code pairing for phones/tablets, and how it
   relates to (but is separate from) individual agents.

This section is meant to grow — as we go through Phase 4 together, real
notes on what 2.0 actually looks like belong here so the next reflash can't
erase the learning either.
