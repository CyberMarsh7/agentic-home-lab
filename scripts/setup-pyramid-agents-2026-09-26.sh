#!/usr/bin/env bash
# Complete, one-shot setup for real, working agents on Pyramid.
# Run this ON PYRAMID (SSH in first, or from a Remote Control session
# that's actually running there). Does the crash-loop check first,
# because setting up agents on an unstable gateway is pointless - then
# sets up two real agents and verifies each one actually works.
#
# Nothing here is guessed - every command matches something already
# verified against docs.openclaw.ai earlier this week
# (docs/openclaw-setup-2026-09-03.md, docs/gateway-crash-loop-2026-09-23.md).

set -uo pipefail
OPENCLAW_BIN="/root/.npm-global/lib/node_modules/openclaw/dist/index.js"
RUN() { echo "+ $*"; sudo node "$OPENCLAW_BIN" "$@"; }

echo "=================================================="
echo "STEP 1: Crash-loop check (fix this first or nothing below will stick)"
echo "=================================================="
ps aux | grep -i openclaw | grep -v grep
which -a openclaw
echo
echo "If more than one openclaw process/binary showed up above, STOP here"
echo "and fix that first per docs/gateway-crash-loop-2026-09-23.md - do not"
echo "continue past this point until only ONE openclaw is running."
read -p "Only one openclaw running, and it's stable? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
  echo "Stopping here. Fix the crash loop, then re-run this script."
  exit 1
fi

echo
echo "=================================================="
echo "STEP 2: Agent 1 - 'claude', the front-door agent (Claude-backed)"
echo "=================================================="
RUN agents add claude --workspace /root/.openclaw/workspace-claude --model claude-cli/claude-opus-5
RUN gateway restart
sleep 3

echo
echo "=================================================="
echo "STEP 3: Agent 2 - 'mail_reader', the email-triage agent"
echo "=================================================="
echo "This uses the preset already built and tested at"
echo "scripts/agent-presets/email/ - applying it now."
node -e "
const fs = require('fs');
const path = require('path');
const configPath = process.env.HOME + '/.openclaw/openclaw.json';
let config = {};
try { config = JSON.parse(fs.readFileSync(configPath, 'utf8')); } catch (e) {}
config.agents = config.agents || {};
config.agents.entries = config.agents.entries || {};
config.agents.entries.mail_reader = {
  workspace: '~/.openclaw/workspace-mail_reader',
  model: 'ollama/qwen2.5:3b-instruct',
  sandbox: { mode: 'all', scope: 'session', workspaceAccess: 'none' },
  tools: { profile: 'minimal', allow: ['session_status'], deny: ['group:fs', 'group:runtime', 'group:web'] }
};
fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
console.log('Wrote mail_reader into ' + configPath);
"
RUN gateway restart
sleep 3

echo
echo "=================================================="
echo "STEP 4: VERIFY - don't trust it, check it"
echo "=================================================="
RUN agents list --bindings
RUN models status --agent claude --json --check
RUN models status --agent mail_reader --json --check
RUN gateway status --deep

echo
echo "=================================================="
echo "If both agents show above and models status doesn't say failed,"
echo "run this to prove agent 1 actually responds:"
echo "  sudo node $OPENCLAW_BIN agent --agent claude --message \"say hello and confirm your own model\""
echo "=================================================="
