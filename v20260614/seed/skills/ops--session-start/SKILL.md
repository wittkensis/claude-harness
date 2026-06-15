---
name: ops--session-start
description: Session orientation — runs at the start of every session. Checks for a prior handoff, orients to the working directory and project phase, surfaces active goals, and declares session intent. Wired into the SessionStart hook so it fires automatically every session.
metadata:
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
  refs-external:    # intentional forward-pointers; not seeded (see ref_lint.py)
    - audit--tokens
    - think--research
---

# Session Start

## Invocation
Triggers: session start, orient, new session, what are we working on, resume

Runs once at session open. Keeps it fast — no rabbit holes, no re-reading everything. Orient, surface continuity, declare intent.

---

## 1. Handoff from prior session

Check for a handoff doc:
```bash
cat ~/.claude/state/last-handoff.md 2>/dev/null
```

If it exists: surface the "what's next" section in one sentence. Don't recap the full doc.
If it doesn't exist: skip this step silently.

## 1.5. Surface recurring failures (every session)

The learning log is centralized (`~/.claude/state/`), so this runs in **any** context:
```bash
python3 ~/.claude/state/learning-log.py --report --since $(date -v-7d +%F 2>/dev/null || date -d '-7 days' +%F)
```
If any target shows >1 failure in the last 7 days, surface it in one line: `⚠ [target] failed N times recently`. Silent if clean or script absent.

---

## 2. Orient to the working directory

```bash
git branch --show-current 2>/dev/null
git log --oneline -3 2>/dev/null
```

Read `CLAUDE.md` if present in `$PWD`. Note: current phase (Design / Build / Verify / Iterate), active branch, last 3 commits.

Also read `~/.claude/state/phase` if present — it records the durable phase set by the last skill that advanced it. Takes precedence over inference from CLAUDE.md.

When cwd is inside `{{harness.config.projects[0].path}}`, run drift-check silently:
```bash
python3 {{harness.config.projects[0].path}}/.claude/# drift-check.py (personal; add your own linter here) 2>/dev/null
```
Surface violations if any. Silent if clean.

---

## 3. Surface relevant goals

Read `~/.claude/goals.md`. Surface only the north star(s) relevant to this project — one line each. Skip goals for unrelated projects.

---

## 4. Declare intent

State — or ask in one question if genuinely unclear:
- **Work type:** build / design / research / audit / maintain
- **Scope:** which feature, file, or question
- **Done criterion:** what does a successful session look like?

If the user's opening message already answers these, infer and confirm rather than asking.

Before acting on a build or design request, check `~/.claude/SKILLS.md` for a relevant specialist skill. If one exists, load it — don't free-style what a skill already covers.

---

## Output format


Keep the orientation summary to 4-6 lines:
```
Prior handoff: [summary of next step, or "none"]
Branch: [branch] · Phase: [phase]
Goal: [relevant north star]
Today: [work type] — [scope] — [done criterion]
```

Then stop. Don't narrate what you read. Don't ask multiple questions. Get to work.

## Related
- `ops--handoff` — precedes: session-start reads the handoff doc that ops--handoff wrote
- `audit--tokens` — companion: session-start hook surfaces due tokens; tokens skill handles rotation
- `ops--tool-resilience` — companion: session-start surfaces deferred tasks from prior auth failures
- `think--research` — companion: session start may trigger a research query to orient on unfamiliar context
- `ops--swarm` — companion: session-start orients the orchestrator before a swarm is launched
