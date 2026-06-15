---
name: ops--handoff
description: Compact the current conversation into a handoff document for the next session or agent to pick up. Use when passing work to a new session, handing off to another agent, or compacting a long conversation before context runs out.
argument-hint: What will the next session focus on?
metadata:
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
  refs-external:    # intentional forward-pointers; not seeded (see ref_lint.py)
    - log--issues
    - plan--prd
---

## Invocation
`/ops-handoff` · Triggers: hand off session, handoff, compact conversation, pass to next agent

Write a handoff document summarizing the current conversation so a fresh agent can continue the work. Save it to `~/.claude/state/last-handoff.md` (overwrite each time — only one handoff doc is kept, the latest). Read the file before writing if it already exists.

Structure it with [`TEMPLATE.md`](TEMPLATE.md). It covers:
- What was accomplished
- What's in progress and its current state
- What's next (specific, actionable)
- Relevant file paths, branch names, URLs
- Skills to load in the next session

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

## Before writing — reconcile the backlog
ops--backlog is the source of truth for "what's next", so it must not carry work that's already done. Before writing the handoff:
1. List the current open items for this project: `python3 ~/.claude/state/backlog.py top --cwd "$PWD" --n 10`
2. For every item you actually completed this session, close it: `python3 ~/.claude/state/backlog.py done <id>`
3. List what you closed in the handoff's **Done** section.

Only close items genuinely finished and verified — a half-done item stays open and goes in **In progress** instead.

## Related
- `ops--session-start` — follows: session-start reads the handoff doc created by this skill
- `ops--swarm` — companion: swarm uses handoffs to coordinate between orchestrator and workers
- `plan--prd` — companion: PRD is referenced in the handoff, not duplicated
- `log--issues` — companion: open issues are referenced in the handoff
