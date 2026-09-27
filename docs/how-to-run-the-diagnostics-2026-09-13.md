# How to actually run the diagnostic script (voice-only paths)

`scripts/run-diagnostics-2026-09-13.sh` checks everything documented as
broken as of today in one pass: what's answering the Pyramid button, the
stuck update, the memory failure, and Victus's auth issue. It's
read-only — it changes nothing, only reports.

The honest problem: it has to run **on Victus** (it has the SSH key for
Pyramid), and running it means getting one command onto that machine.
Here are the realistic ways that happens without typing:

## Option 1 — if a local Claude Code session already talks to you on Victus

Say (out loud, to that session): *"Pull the latest agentic-home-lab repo
and run scripts/run-diagnostics-2026-09-13.sh, then tell me what it
found."* That session has real hands on the machine — it can do this
directly and read the results back to you.

## Option 2 — Windows Voice Access (built into Windows 11, already on Victus)

This is a Windows accessibility feature, not something that needs
installing. It can open apps and dictate/execute commands by voice alone.
Settings → Accessibility → Speech → Voice Access → turn on. Once it's on,
saying something like *"open Windows Terminal"* then dictating the two
lines below (Voice Access supports command dictation into a terminal)
gets the script running:
```
cd path\to\agentic-home-lab
git pull
bash scripts/run-diagnostics-2026-09-13.sh
```
If dictation garbles the path/punctuation (a known rough edge), it's
still just this once — after this the fixes can be scripted too.

## Option 3 — anyone else in the household, once, for five minutes

Whoever it is doesn't need to understand any of this — just open a
terminal on Victus and run the three lines above. The output is
self-explanatory (it prints section headers). It can even just get pasted
back to me or to a local Claude session afterward for interpretation.

## After it runs

Paste the full output into any Claude Code session (this one included —
paste it right into this chat) with: *"here's the diagnostic output, tell
me what's actually wrong and fix it."* That's the point where real fixes
get proposed against confirmed evidence instead of guesses.
