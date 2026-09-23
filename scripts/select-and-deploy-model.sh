#!/usr/bin/env bash
# Startup routine: detect available compute on THIS machine, pick the
# largest model from scripts/model-manifest.json that actually fits, and
# (with --apply) point a given OpenClaw agent at it.
#
# Usage:
#   ./select-and-deploy-model.sh                                     # just report what it would pick
#   ./select-and-deploy-model.sh --agent samantha --apply             # set the model on an existing agent
#   ./select-and-deploy-model.sh --role email --agent samantha --apply
#       # also stamp out agent-presets/email/agent-template.json with
#       # the picked model + agent id, print where the trigger (cron or
#       # webhook, see that role's trigger.json) still needs wiring
#
# Detection order: NVIDIA GPU VRAM (nvidia-smi) -> Apple Silicon unified
# memory (sysctl) -> system RAM as a last-resort fallback. This is a
# planning estimate, not a guarantee - always sanity-check against the
# actual model's real memory use once it's running.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SCRIPT_DIR/model-manifest.json"
PRESETS_DIR="$SCRIPT_DIR/agent-presets"

AGENT=""
ROLE=""
APPLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --role) ROLE="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

detect_vram_gb() {
  # Prints "<method>|<GB>" - callers split on the pipe. Order matters:
  # dedicated GPU first, then Apple's unified memory, then plain Linux
  # RAM as the catch-all for everything with no GPU at all - this is the
  # path a RasPad or PineTab2 (both ARM, no discrete GPU) will always hit.
  if command -v nvidia-smi >/dev/null 2>&1; then
    local mib
    mib=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -n1)
    if [[ -n "${mib:-}" ]]; then
      echo "nvidia-gpu-vram|$(( mib / 1024 ))"
      return 0
    fi
  fi
  if command -v sysctl >/dev/null 2>&1 && sysctl -n hw.memsize >/dev/null 2>&1; then
    # Apple Silicon: unified memory, treat as VRAM-equivalent minus a
    # safety margin for the OS itself. (Linux also ships a `sysctl`
    # binary, but hw.memsize isn't a real key there, so this check
    # naturally fails and falls through - verified in this sandbox.)
    local bytes
    bytes=$(sysctl -n hw.memsize)
    echo "apple-unified-memory|$(( bytes / 1024 / 1024 / 1024 - 4 ))"
    return 0
  fi
  if [[ -r /proc/meminfo ]]; then
    local kib
    kib=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
    # No dedicated GPU detected - fall back to system RAM, minus a
    # safety margin, since a local model here would be CPU/NPU-bound.
    # This is the RasPad / PineTab2 / any other ARM-SBC path.
    echo "linux-ram-fallback|$(( kib / 1024 / 1024 - 2 ))"
    return 0
  fi
  echo "unknown|0"
}

DETECTION=$(detect_vram_gb)
DETECT_METHOD="${DETECTION%%|*}"
VRAM_GB="${DETECTION##*|}"
echo "Detection method: ${DETECT_METHOD}"
echo "Detected usable compute: ${VRAM_GB} GB"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found - needed to read $MANIFEST" >&2
  exit 1
fi

SELECTED=$(python3 - "$MANIFEST" "$VRAM_GB" <<'PYEOF'
import json, sys
manifest_path, vram_gb = sys.argv[1], int(sys.argv[2])
with open(manifest_path) as f:
    data = json.load(f)
best = None
for m in data["models"]:
    if m["min_vram_gb"] <= vram_gb:
        best = m
        break  # list is largest-to-smallest, first fit wins
if best is None:
    best = data["models"][-1]  # nothing fits cleanly - fall back to smallest
print(best["name"])
PYEOF
)

echo "Best-fitting model for this machine: $SELECTED"

if [[ "$APPLY" -eq 0 ]]; then
  echo "(dry run - pass --agent <id> --apply to actually set it)"
  exit 0
fi

if [[ -z "$AGENT" ]]; then
  echo "ERROR: --apply requires --agent <id>" >&2
  exit 1
fi

if [[ -z "$ROLE" ]]; then
  if ! command -v openclaw >/dev/null 2>&1; then
    echo "ERROR: openclaw CLI not found on this machine - can't apply" >&2
    exit 1
  fi
  echo "Setting agents.entries.${AGENT}.model = ollama/${SELECTED} ..."
  openclaw config set "agents.entries.${AGENT}.model" "ollama/${SELECTED}"
  echo "Done. Restart that agent/gateway for the change to take effect."
  exit 0
fi

PRESET_DIR="$PRESETS_DIR/$ROLE"
TEMPLATE="$PRESET_DIR/agent-template.json"
if [[ ! -f "$TEMPLATE" ]]; then
  echo "ERROR: no preset found at $TEMPLATE (known roles: $(ls "$PRESETS_DIR" 2>/dev/null | tr '\n' ' '))" >&2
  exit 1
fi

OUT_DIR="$SCRIPT_DIR/deployed"
mkdir -p "$OUT_DIR"
OUT_FILE="$OUT_DIR/${ROLE}-${AGENT}.json"
sed -e "s/__MODEL__/ollama\/${SELECTED//\//\\/}/g" -e "s/__AGENT_ID__/${AGENT}/g" "$TEMPLATE" > "$OUT_FILE"

echo "Stamped preset '$ROLE' for agent '$AGENT' with model '$SELECTED' -> $OUT_FILE"
echo "Merge this into ~/.openclaw/openclaw.json (or 'openclaw config set' each key) on the target machine."

TRIGGER="$PRESET_DIR/trigger.json"
if [[ -f "$TRIGGER" ]]; then
  echo
  echo "This role's trigger is NOT wired automatically - do this once, separately:"
  python3 -c "
import json
d = json.load(open('$TRIGGER'))
print('  Type:', d['type'])
if 'setup_command' in d:
    print('  Setup:', d['setup_command'])
if 'setup_commands' in d:
    for i, cmd in enumerate(d['setup_commands'], 1):
        print(f'  Setup {i}:', cmd)
if 'note' in d:
    print('  Note:', d['note'])
"
fi
