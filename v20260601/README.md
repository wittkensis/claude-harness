# HARNESS-PORT

A self-contained kit that stands up the portable core of the home Claude Code harness — **skills
(incl. `swarm` + `canary`), agents, enforcement hooks, and discipline** — on a different machine,
adapted to that machine's own services and stacks.

## Use it (on the target / work machine)

1. **Copy** this whole `HARNESS-PORT/` folder to the work machine (drive / AirDrop / scp — no
   GitHub needed).
2. **Open Claude Code in it:**
   ```bash
   cd HARNESS-PORT
   claude
   ```
3. **Run the installer:**
   ```
   /harness-bootstrap
   ```
   It investigates the existing harness + tools, asks only what it can't detect, generates an
   adapted `~/.claude`, and verifies it. Full autonomy — it won't stall waiting on you except for a
   genuinely human-only login.
4. **Restart Claude Code** (or open `/hooks` once) so the new hook wiring loads.

That's it. The bootstrap backs up any existing `~/.claude` first and never clobbers your existing
skills/settings/CLAUDE.md — it merges.

## What's in here
```
README.md            ← you are here
PORT-MANIFEST.md     ← exactly what ports / is genericized / is dropped, and why
INTERVIEW.md         ← the question bank the bootstrap works through
.claude/skills/harness-bootstrap/   ← the installer skill (gives you /harness-bootstrap here)
kit/
  skills/  agents/  hooks/  templates/
  install.py         ← deterministic, idempotent generator (the bootstrap calls this)
  port-test.py       ← post-install verification (behavioral)
```

## Try it without touching your real ~/.claude
```bash
python3 kit/install.py --dry          # installs into a temp HOME, prints the tree
```

## Notes
- Machine-specific values live in `~/.claude/harness.config.json` (written by the interview).
  Hooks read it and fall back to safe defaults if it's missing.
- **Secrets never travel.** The token registry is metadata-only; values stay in your secret store.
- Safe to re-run `/harness-bootstrap` (or `install.py`) — it's idempotent.
