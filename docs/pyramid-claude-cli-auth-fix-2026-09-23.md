# Pyramid: Claude Code CLI asking for API credits instead of using the subscription (2026-09-23)

## Symptom

Trying to install/log into Claude Code on Pyramid, it asks for credits
that don't exist — even though the same account's subscription works
fine everywhere else (including this repo's cloud sessions).

## Real cause, verified against docs.claude.com/authentication

Two completely separate Anthropic billing systems exist:
1. **claude.ai subscription** (Pro/Max/Team/Enterprise) — what's actually
   working everywhere else.
2. **Anthropic Console API** — separate pay-per-use billing, empty unless
   funded on purpose.

If `ANTHROPIC_API_KEY` is set in the environment, Claude Code skips the
normal subscription login entirely and uses that key instead — landing
on system #2, which has no credits. This is the documented cause of
exactly this symptom.

## Fix

```bash
echo $ANTHROPIC_API_KEY      # if this prints anything, that's the cause
unset ANTHROPIC_API_KEY
claude                        # pick claude.ai login, not Console/API key
```

Pyramid has no browser (headless device), so the normal login popup
can't complete there. This is a documented, expected case — not a
separate bug:

> "If your browser shows a login code instead of redirecting back after
> you sign in, paste it into the terminal... This happens when the
> browser can't reach Claude Code's local callback server, which is
> common in WSL2, SSH sessions, and containers."

So on Pyramid: `claude` prints a URL instead of opening a browser. Open
that URL on **any other device with a browser** (phone, Victus), log in
with the real claude.ai account, and it shows a short code — type that
code into Pyramid's terminal when prompted.

**Alternative, avoids the browser dance entirely:** run
`claude setup-token` (from any machine with a browser, doesn't have to
be Pyramid itself) to mint a one-year subscription-backed token, then on
Pyramid: `export CLAUDE_CODE_OAUTH_TOKEN=<token>`.

## If `unset` doesn't stick

Check for `ANTHROPIC_API_KEY` being set somewhere persistent, not just
the current shell: `.bashrc`/`.profile`, or a `settings.json`'s `env`
block (`~/.claude/settings.json`) — the env var and settings.json paths
both count, and either one re-sets it on the next shell/session.

## Confirmed working: Pyramid's Tailscale HTTPS setup

While debugging this, Bret found a real, valid, currently-active TLS
certificate for `pyramid-openclaw-1.tail2f8a97.ts.net`, issued by Let's
Encrypt (valid 2026-09-22 through 2026-12-21). This confirms Pyramid's
OpenClaw gateway already has Tailscale's HTTPS serving configured
correctly — a real positive signal, unrelated to the login issue above.

**Important limitation, so this isn't mistaken for a way around the
cloud-session access wall:** a `.ts.net` hostname only resolves and
routes for devices that are actual authenticated members of that
specific Tailscale tailnet. It is not a public internet address, even
though it carries a normal-looking publicly-trusted certificate — no
cloud session (this one or any other) can reach it just by knowing the
hostname.

## The actual next step after login works: Remote Control

Once Claude Code is logged in on Pyramid (or Victus), running
`claude remote-control` there makes that session reachable from
claude.ai/code or the Claude phone app — with **real** access, because
it's the same physical process running on that machine, just viewable
remotely. This is the real fix for "someone has to relay commands back
and forth between Bret and a cloud session":

```bash
claude remote-control
```

It prints a URL and a QR code directly in that terminal. Scan the QR
code with the Claude phone app (or open the URL in any browser signed
into the same account), and that phone/browser is now talking to a
session with real hands on that machine — no cloud session, no relay,
no address to hand anyone.

Requirements (verified against docs.claude.com/remote-control):
- A Pro, Max, Team, or Enterprise claude.ai subscription (not an API key)
- Must be signed in via `/login` with a full-scope session, not a
  long-lived `setup-token` (those can only make model requests, not
  start Remote Control)
- Run it from inside a real project directory (a workspace-trust dialog
  has to be accepted there at least once first)

## Sources (fetched live, 2026-09-23)

- [Claude Code authentication docs](https://code.claude.com/docs/en/authentication)
- [Claude Code Remote Control docs](https://code.claude.com/docs/en/remote-control)
