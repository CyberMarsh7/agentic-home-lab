# Portable agent drive on Pyramid — plan (2026-09-24)

Not built yet. This is the design to execute in the next session, with
physical hardware access. Captured here so a session boundary doesn't lose it.

## The architecture

- **2TB Seagate "Zdrive" SSD** (currently plugged into Victus as `Z:`, ReFS)
  becomes the portable agent store — pre-built agent configs, memory/history,
  moved onto it.
- **Plug the SSD into Pyramid directly** (not Victus). Pyramid's OpenClaw data
  directory (`~/.openclaw` or a subset of it) points at the mounted SSD, so
  Pyramid "loads itself into itself" — the drive isn't just data alongside
  Pyramid, it becomes Pyramid's actual home.
- **Pyramid stays the hub**, running its own independent agents (as it
  already does today) — it does not become a subordinate `openclaw connect`
  node of Victus. Other things become nodes/accessories *of Pyramid*:
  ESP32-S3 boards, Stackchan units, potentially the PineTab2 and RasPad.
- **Victus stays the heavy-compute backend** — same pattern already working
  tonight: Pyramid's agents call Victus's Ollama over Tailscale for anything
  past what Pyramid's own NPU can handle. This part doesn't change.
- **Reachability**: Pyramid keeps its own Tailscale identity, so the whole
  rig (Pyramid + SSD, optionally + PineTab2) stays reachable from Victus or
  anywhere else on the tailnet even when physically disconnected from Victus.
- **MCP server for ESP32/Stackchan devices** gets built as a service
  Pyramid's dashboard exposes, once the drive is actually mounted there —
  this is the natural attachment point for it, not something to bolt onto
  Victus.

## Why this shape (not the alternatives already ruled out tonight)

- Not `openclaw connect` as a subordinate node on Pyramid's side — that would
  give up Pyramid's own agent, contradicting "Pyramid is the front door"
  from the original vision doc.
- Not "everything on the SSD, models included" — model weight *files* don't
  benefit from portability the way agent configs/memory do; USB load times
  are meaningfully slower than internal NVMe, and the thing that matters for
  "where can a model run" is which device has the compute, not which disk
  holds the file. Compute (Victus's GPU) stays where it is.

## Known blockers to solve when this work actually starts

1. **Filesystem**: the SSD is currently ReFS (Windows-only). Pyramid is
   Linux/aarch64. It needs reformatting to something both can read
   (exFAT for cross-OS, or ext4 if Windows access to it stops mattering) —
   this wipes existing contents (`empire-backup`, `claude-code-main`,
   `stackchan-system`, `ollama-models`, `active_terminal_agent.py`), so
   inventory and back up whatever's worth keeping before reformatting.
2. **Physical access**: needs the SSD physically moved from Victus to
   Pyramid, and someone at the hardware for ESP32/Stackchan bring-up.
3. **Pyramid resource limits**: only 1.9GB RAM, already tight — worth
   checking headroom before adding an MCP server + more agents there.

## Not started

Nothing above has been built. Pyramid currently still runs its agents off
its own internal disk, unrelated to the Z: drive.
