# Open question: "OpenClaw says mine's not verified" (2026-09-23)

Reported by Bret in passing, while heading out the door — not enough
detail to diagnose safely, and guessing here would repeat the exact
mistake this whole repo exists to prevent.

**Need the exact wording** to know which of these it actually is:
- A model auth check failing (`openclaw models status --check` showing
  an unverified/failed provider)
- Node/device pairing showing as pending or unapproved
  (`openclaw devices list`, `openclaw nodes pending`)
- The newer **Trusted Devices** beta feature (Team/Enterprise only,
  requires device enrollment) — unlikely on a personal plan, but worth
  ruling out
- Something else entirely - a channel account, a webhook, anything else
  OpenClaw might call "verification"

**Next step:** get the literal on-screen text (screenshot or exact
wording) next time this comes up, then diagnose against the real
message instead of a guess.
