# Real jobs Bret has asked agents to do — backlog (2026-09-13)

## Why this doc exists

As of today, **no agent in this lab has ever had a recurring job
(`openclaw automations`, i.e. a cron job) configured — for email, for
memory folding, for anything.** Agents got created (`agents add`) and
occasionally given a one-off task in a live chat, but nothing was ever set
up to run on its own. That's the actual, confirmed reason Bret has been
asking for the same things for two months without seeing them happen:
whoever he was talking to did the task themselves in the moment instead of
building the agent+job that would keep doing it.

Every entry below stays in this list, checked off only when there is a
**verified `openclaw automations get <jobId>` output** proving the job
exists and has actually fired at least once — not when someone believes
it's configured.

## 1. Email triage / "what needs my attention" agent — highest priority, asked for repeatedly

**What Bret wants:** an agent that reads his email and tells him what he
actually needs to know or act on — not Claude reading email for him in a
chat window once and forgetting it, an agent that keeps doing this on its
own.

**Status: not built. No agent has Gmail access configured anywhere in this
repo's record, and no automation job exists for it.**

**The real mechanism** (verified against docs.openclaw.ai on 2026-09-13,
sources below — this was never documented in this repo before today):

1. **Connect Gmail as an MCP server** in OpenClaw's config
   (`~/.openclaw/openclaw.json` on whichever device runs the gateway for
   this agent — Pyramid, per the "front door" vision):
   ```json5
   mcp: {
     servers: {
       gmail: {
         transport: "stdio", // or "sse" / "streamable-http" depending on the Gmail MCP server used
         command: "...",     // the Gmail MCP server's launch command
         args: ["..."],
         enabled: true,
         toolFilter: {
           // scope this down deliberately — an email agent probably
           // does NOT need send/delete access, only read/search
           include: ["gmail_search*", "gmail_read*", "gmail_list*"]
         }
       }
     }
   }
   ```
   Also addable via the Control UI: Settings → MCP → Add server.

2. **Give one specific agent access to it**, not every agent, via that
   agent's tool allowlist:
   ```json5
   agents: {
     entries: {
       "email-helper": {
         tools: { allow: ["gmail_*"] }
       }
     }
   }
   ```

3. **Schedule the recurring check** — this is the actual "cron job" piece
   that's been missing the whole time:
   ```bash
   openclaw automations create "0 7,12,17 * * *" \
     "Check my inbox for anything I actually need to see or act on today. Summarize it plainly, skip anything routine." \
     --name "email-triage" --agent email-helper --deliver \
     --reply-channel <whichever channel reaches Bret> --session isolated
   ```
   Three times a day (7am/noon/5pm) is a starting guess — change the cron
   expression once Bret says what cadence he actually wants.

4. **Verify it's real, not assumed:**
   ```bash
   openclaw automations list
   openclaw automations get <jobId>   # confirm lastRun actually happened
   ```

**Open decisions only Bret can make:**
- Which Gmail account(s) — his own, or also a shared family one?
- How much access: read-only search/summarize (recommended to start) vs.
  anything more (drafting replies, archiving, etc.)?
- Which agent does this — a new dedicated `email-helper`, or bolt it onto
  an existing one (claude, on Pyramid, is the obvious candidate since it's
  already Claude-backed)?
- Delivery: read aloud through whichever voice channel Bret uses, a
  companion-app notification, or something else?

**Blocker:** same as everything else physical in this repo — this has to
be configured from a local session with LAN/SSH access to wherever the
gateway runs, not from a cloud session. But the exact recipe now exists,
so it's a single sitting, not a rediscovery.

## 2. Weekly memory folding

Already documented in `docs/stackchan-mcp-and-memory-2026-09-03.md` and
`docs/openclaw-dispatching-jobs-2026-09-13.md` — same status: mechanism
known, nothing scheduled yet.

## Rule going forward

Any time Bret says "have an agent do X regularly" or "keep an eye on X for
me," the deliverable is an `openclaw automations create` command bound to
a real agent — never Claude doing X once in the current chat and calling
it handled. Add the request to this file the moment it's asked for, before
attempting to build it, so it survives even if the build gets interrupted.

## Sources (fetched live, 2026-09-13)

- [Connect MCP servers · OpenClaw](https://docs.openclaw.ai/tools/mcp)
- [Configuration — MCP, skills, and plugins · OpenClaw](https://docs.openclaw.ai/gateway/config-extensions)
- [Configuration reference · OpenClaw](https://docs.openclaw.ai/gateway/configuration-reference)
- [Manage automations · OpenClaw](https://docs.openclaw.ai/automation/cron-jobs/managing-jobs)
