<!-- HARNESS-PORT:BEGIN (managed by harness-bootstrap — safe to re-run; edit between markers freely, the bootstrap won't duplicate) -->

# Harness — Discipline & Operating Rules

_Ported from the home Claude Code harness. Service/stack specifics for THIS machine live in `~/.claude/harness.config.json`; the rules below are universal._

## Project Phases

```
Brief → Research → Plan → Concepts → Build → Validate
```

- Use the `plan` skill — run `grill-me` first to surface needs before committing to structure.
- **Pause for user approval at each phase transition** (the `swarm` skill is the deliberate exception — it runs the build phase autonomously by design).
- Every project uses git. Commit frequently.

## Context Management

| Level | Action |
|-------|--------|
| <50% | Continue |
| 50-70% | Consider delegating research to a sub-agent |
| 70-85% | `/compact` or commit & summarize |
| >85% | Commit, start a new thread |

## Complex Reasoning

For every complex problem: DECOMPOSE → SOLVE (with explicit confidence 0.0–1.0) → VERIFY → SYNTHESIZE → REFLECT (if confidence <0.8, find the weak link and retry). Simple questions: skip to the answer. Always output a clear answer, a confidence level, and key caveats.

## Code Quality

- Clear over clever. Type everything. Comments explain "why," not "what."
- No unused backwards-compat code. Accessibility built-in. Avoid emojis.

## Task Discipline (enforced by hooks)

- **Define success before coding** — state what "done" looks like first; that's the validation target.
- **Two-step completion gate** — (1) typecheck passes; (2) intent is validated by exercising the feature. "It compiled" is not done. "It works as intended" is done.
- **Validate intent proactively** — exercise the feature with the `verify`/`run` skill before reporting done; if it can't be run, say why and what was confirmed instead.
- **Surgical changes only** — touch only what the task requires.
- **Commit at each logical step** — never stack steps on an unverified foundation.
- **Tests verify intent, not behavior** — a test that still passes when business logic changes is worthless.
- **Fail loud** — surface uncertainty and partial failures; never swallow errors silently.
- **Read before writing** — read relevant files and callers before editing.

**Enforced by hooks** (`~/.claude/hooks/`, wired in `settings.json`): a fail-closed write guard (protected paths + `.env`), `lint --fix` on edit, a **typecheck + test gate on `git commit`** (bypass: add `[wip]`), an auth-failure defer-and-continue catcher, and SessionStart context (deferred tasks + tokens due + active-project CLAUDE.md). These make the rules above mechanical, not advisory.

## Secrets

Real secret VALUES never go in a tracked file, a skill, the token registry, or chat output. They live in `.env.local` (gitignored) / your CI/secret store / the deploy platform's env / the provider console. The `token-rotation` skill keeps each one in sync across those places. The registry holds metadata only.

<!-- HARNESS-PORT:END -->
