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

## Sources (fetched live, 2026-09-23)

- [Claude Code authentication docs](https://code.claude.com/docs/en/authentication)
