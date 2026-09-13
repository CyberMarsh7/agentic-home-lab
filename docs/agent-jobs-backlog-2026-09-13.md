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

**Correction (2026-09-13, same day): the section below this note used to
describe a generic third-party MCP setup. That was wrong — OpenClaw has a
*native*, built-in Gmail integration that's simpler and event-driven
(reacts to new mail in real time, not just on a timer). Verified against
`docs.openclaw.ai/automation/cron-jobs/gmail` directly.**

**The real mechanism:**

1. **One-command setup** — this handles Google auth, Pub/Sub
   infrastructure, and the Gmail preset mapping automatically:
   ```bash
   openclaw webhooks gmail setup --account <bret's-email>@gmail.com
   ```
   (Needs `gcloud auth login` and a GCP project set first —
   `gcloud config set project <project-id>`.)

2. **Create a dedicated, deliberately restricted agent** for reading mail
   — not one of the general-purpose agents, and NOT given filesystem/exec
   access, just enough to read and reason about a message:
   ```json5
   agents: {
     entries: {
       mail_reader: {
         workspace: "~/.openclaw/workspace-mail-reader",
         sandbox: { mode: "all", scope: "session", workspaceAccess: "none" },
         tools: {
           profile: "minimal",
           allow: ["session_status"],
           deny: ["group:fs", "group:runtime", "group:web"]
         }
       }
     }
   }
   ```

3. **Wire new mail to that agent** via a hook mapping — this is what makes
   it event-driven (fires per email) rather than a polling cron job:
   ```json5
   hooks: {
     allowedAgentIds: ["mail_reader"],
     mappings: [{
       match: { path: "gmail" },
       agentId: "mail_reader",
       forEach: "messages",
       sessionKey: "hook:gmail:{{messages[0].id}}",
       deliver: false   // set true once ready to actually notify Bret per message
     }]
   }
   ```
   Each new email gets its own isolated sandboxed run — one email can't see
   another's context.

4. **Point the agent at a model:**
   ```bash
   openclaw models auth --agent mail_reader login --provider anthropic
   openclaw models status --agent mail_reader --check --probe
   ```

5. **Verify it's real, not assumed** — send a test email and confirm a run
   actually happened:
   ```bash
   openclaw automations list
   openclaw logs --agent mail_reader
   ```

If real-time-per-email turns out to be too chatty, a scheduled digest
instead (`openclaw automations create "0 7,12,17 * * *" ... --agent
mail_reader`) is the fallback — but try the native event-driven path
first, since it's the one OpenClaw actually built for this.

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
