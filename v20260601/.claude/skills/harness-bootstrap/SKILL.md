---
name: harness-bootstrap
description: One-time installer that ports the portable Claude Code harness (skills, hooks, agents, discipline) onto THIS machine, adapted to its own services and stacks. Investigates the existing harness + connected services, interviews the user for the gaps, generates an adapted ~/.claude, then verifies it. Run once on a new machine. Triggers — harness bootstrap, port harness, set up harness, install harness.
---

# Harness Bootstrap (installer)

You are the **installer** standing up a proven harness on a new machine. The home machine's
services (its hosting, its design system, its wiki) did **not** travel — the *architecture and
discipline* did. Your job: learn what THIS machine uses, fill the gaps by asking, then generate
and verify an adapted harness. Run **full autonomy** end-to-end; only stop on a real failure or a
genuinely human-only credential.

The payload lives next to this skill in `../../kit/` (`kit/skills`, `kit/agents`, `kit/hooks`,
`kit/templates`, `kit/install.py`, `kit/port-test.py`). Find the kit root with:
`KIT="$(cd "$(dirname this-skill)/../../kit" && pwd)"` — or just locate the `HARNESS-PORT/kit` dir.

## Phase 1 — Investigate (write findings to `INVESTIGATION.md`)
Scan, don't assume. Cover:
- **Existing harness** — `~/.claude/{skills,agents,hooks,settings.json,CLAUDE.md}`. Anything here
  is **merged, never clobbered**. Note name collisions with kit skills.
- **Tooling** — `which git gh docker kubectl vercel fly aws gcloud pnpm yarn npm pytest cargo go ruff eslint`.
- **MCP servers** — `claude mcp list` (or settings). These are the auth-prone surfaces the
  auth-failure hook protects.
- **Stacks** — languages/build tools in the user's project dirs; test runners; linters; CI config.
- **Hosting & secrets** — deploy target, where secrets live, git host, domain provider (infer; confirm in interview).

## Phase 2 — Interview (produce `~/.claude/harness.config.json`)
Work through `kit/INTERVIEW.md`. **Ask only what investigation couldn't settle**, using
`AskUserQuestion`, batched. The config schema is `kit/templates/harness.config.schema.json`. Fill:
`project_roots`, `protected_globs`, `commit_gate` commands (or leave blank for auto-detect),
`token_registry_path`, `token_target_types`, and the `deploy` adapter. Write valid JSON; validate
it against the schema.

## Phase 3 — Generate (idempotent)
Run: `python3 "$KIT/install.py" --config <the harness.config.json you wrote>`
It backs up `~/.claude`, installs hooks/agents, **copies-if-absent** skills (reports collisions),
**merges** hook wiring into settings.json, appends the discipline block to CLAUDE.md between
sentinel markers, and seeds an empty (metadata-only) token registry + state dir. Re-running is safe.
For any skill it reported as "left existing," decide with the user whether to merge the ported version.

## Phase 4 — Verify + onboard secrets
- `python3 "$KIT/port-test.py"` — must pass (hooks wired + behavioral guard/commit-gate matrix +
  skill/agent integrity + config valid). Fix anything red; never hand over a red install.
- `python3 ~/.claude/hooks/tokens.py audit` — registers existing secret KEY NAMES (never values)
  as `needs-review` so the user can set cadences.
- Tell the user to **restart Claude Code (or open `/hooks` once)** so the new wiring loads — the
  settings watcher only picks up hooks present at session start.

## Guardrails
- Never write a secret VALUE anywhere (registry/skill/commit/output). Metadata only.
- Never clobber existing user skills/settings/CLAUDE.md — merge, and the install backs up first.
- If an MCP/remote auth fails mid-bootstrap, defer-and-continue per the installed `auth-resilience`
  skill; finish everything else.

TERMINATION: `port-test.py` passes, `harness.config.json` is valid and populated, existing
config/ skills were preserved (collisions reported), the token registry is seeded + audited, and
the user has been told to restart to load the wiring.
