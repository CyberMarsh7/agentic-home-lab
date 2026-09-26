#!/usr/bin/env bash
# Fleet status check — "what's actually running where, right now."
#
# Answers the orphan-instance question from
# docs/hermes-orchestrator-rebuild-2026-09-15.md: for each known host, show
# the live gateway status, agents, and cron/automation jobs, and flag
# anything live that isn't in the REGISTRY below (orphaned) or anything in
# the REGISTRY that isn't responding (down).
#
# Run this from Virgil. Bret can ask Hermes to "run the fleet check"
# instead of typing this himself.
#
# One-time setup: fill in DANTE_HOST below with Dante's actual Tailscale
# hostname or IP (run `tailscale status` once to find it).
set -euo pipefail

DANTE_SSH_KEY="${DANTE_SSH_KEY:-$HOME/.ssh/pyramid_ed25519}"
DANTE_SSH_USER="${DANTE_SSH_USER:-marshinpyramid}"
DANTE_HOST="${DANTE_HOST:-192.168.1.227}"  # replace with Dante's tailnet hostname/IP once known
DANTE_OPENCLAW="sudo node /root/.npm-global/lib/node_modules/openclaw/dist/index.js"

# host -> space-separated list of agents that are SUPPOSED to be there
declare -A REGISTRY=(
  [dante]="oracle"
  [virgil]="samantha hermes"
)

section() { printf '\n== %s ==\n' "$1"; }

check_dante() {
  section "Dante (Pyramid, ${DANTE_HOST})"
  if ! ssh -i "$DANTE_SSH_KEY" -o ConnectTimeout=5 "${DANTE_SSH_USER}@${DANTE_HOST}" true 2>/dev/null; then
    echo "UNREACHABLE — cannot SSH to Dante. Down, or not on Tailscale right now."
    return
  fi
  ssh -i "$DANTE_SSH_KEY" "${DANTE_SSH_USER}@${DANTE_HOST}" "
    echo '--- gateway status ---'
    $DANTE_OPENCLAW gateway status
    echo '--- agents ---'
    $DANTE_OPENCLAW agents list --bindings
    echo '--- automations (cron jobs) ---'
    $DANTE_OPENCLAW automations list --all
  "
}

check_virgil() {
  section "Virgil (this machine)"
  if ! command -v openclaw >/dev/null 2>&1; then
    echo "openclaw not found in PATH on this machine."
    return
  fi
  echo '--- gateway status ---'
  openclaw gateway status
  echo '--- agents ---'
  openclaw agents list --bindings
  echo '--- automations (cron jobs) ---'
  openclaw automations list --all
}

diff_registry() {
  section "Registry check"
  for host in "${!REGISTRY[@]}"; do
    echo "$host expected: ${REGISTRY[$host]}"
  done
  echo "(compare the 'expected' lines above against the live --agents-- output"
  echo " printed for each host. Anything live but not expected = orphan."
  echo " Anything expected but missing from the live list = down/deleted.)"
}

check_dante
check_virgil
diff_registry
