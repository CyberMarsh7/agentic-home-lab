#!/usr/bin/env bash
# One-shot, READ-ONLY diagnostic sweep for everything documented as
# broken/unclear as of 2026-09-13. Changes nothing. Safe to run repeatedly.
#
# Run this from Victus (it has the SSH key for Pyramid).
# Requires: ~/.ssh/pyramid_ed25519 already set up (per docs/openclaw-setup-2026-09-03.md).
#
# Output is plain text with clear section headers — read top to bottom,
# or paste the whole thing back into a Claude Code session (local or
# cloud) and ask it to interpret the results against:
#   docs/openclaw-open-issues-diagnosis-2026-09-13.md
#   docs/voice-interface-2026-09-13.md

set -uo pipefail

PYRAMID_HOST="marshinpyramid@192.168.1.227"
PYRAMID_KEY="$HOME/.ssh/pyramid_ed25519"
OPENCLAW_BIN="/root/.npm-global/lib/node_modules/openclaw/dist/index.js"

section() { echo; echo "=================================================="; echo "== $1"; echo "=================================================="; }

section "1. PYRAMID: is the factory demo or OpenClaw actually answering the button?"
ssh -i "$PYRAMID_KEY" "$PYRAMID_HOST" '
  echo "--- factory demo process ---"
  ps aux | grep -i "pyramid_demo\|AI_Pyramid" | grep -v grep
  echo "--- openclaw process ---"
  ps aux | grep -i openclaw | grep -v grep
'

section "2. PYRAMID: OpenClaw gateway health + version"
ssh -i "$PYRAMID_KEY" "$PYRAMID_HOST" "sudo node $OPENCLAW_BIN gateway status --deep"

section "3. PYRAMID: agents configured + which channel/device binds to which"
ssh -i "$PYRAMID_KEY" "$PYRAMID_HOST" "sudo node $OPENCLAW_BIN agents list --bindings"

section "4. PYRAMID: update status (the stuck-2.0 issue)"
ssh -i "$PYRAMID_KEY" "$PYRAMID_HOST" "sudo node $OPENCLAW_BIN update status" 2>&1

section "5. PYRAMID: doctor (broad health + auth + tool-policy lint)"
ssh -i "$PYRAMID_KEY" "$PYRAMID_HOST" "sudo node $OPENCLAW_BIN doctor" 2>&1

section "6. PYRAMID: disk + .openclaw directory (the 'can't create memory' issue)"
ssh -i "$PYRAMID_KEY" "$PYRAMID_HOST" "df -h; echo; ls -la /root/.openclaw/"

section "7. VICTUS: local Claude CLI auth (the API-key-fallback issue)"
claude auth status --text 2>&1

section "8. VICTUS: OpenClaw agents + model status"
openclaw agents list --bindings 2>&1
openclaw models status --json --check 2>&1

echo
echo "=================================================="
echo "Done. Paste everything above into a Claude Code session"
echo "(this repo cloned) and ask it to compare the results against"
echo "docs/openclaw-open-issues-diagnosis-2026-09-13.md and"
echo "docs/voice-interface-2026-09-13.md, then propose exact fixes."
echo "=================================================="
