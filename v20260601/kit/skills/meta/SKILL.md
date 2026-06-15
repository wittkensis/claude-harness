---
name: meta
description: Work on the agent system itself — author or scaffold new skills (global and project-local skills), audit and refactor the skill library, and hand off a session to the next agent. Use when creating/writing/scaffolding a skill, auditing or optimizing skills/agents/CLAUDE.md, running a system health review, or compacting the conversation into a handoff doc.
---

# Meta

Operates on the agentic system, not on a project. Three jobs:

| File | When |
|------|------|
| [skill-authoring.md](skill-authoring.md) | Create or scaffold a skill — global (`~/.claude/skills/`) or project-local (`{proj}--{purpose}`) |
| [system-health.md](system-health.md) | Audit / refactor the library, periodic or post-project review, skill health |
| [handoff.md](handoff.md) | Compact this conversation into a handoff doc for the next session/agent |

## Quick Reference

**Skill structure** — one level deep only. `skillname/SKILL.md` is discovered; `skillname/sub/SKILL.md` is NOT (nested `SKILL.md` is an inert resource file). Specialties = plain `.md` files the router links to, read on demand.

**Discovery** — keys off `name` + `description`, not a `triggers:` array. Make the description carry the trigger keywords. First sentence = what it does; then "Use when …".

**Size** — `SKILL.md` under ~100 lines; split a specialty when it exceeds ~500–800.

**Handoff** — don't duplicate content already in PRDs, plans, commits; reference by path/URL.

**Termination** — every skill, slash-command, and template ends with a checkable done-condition (a `TERMINATION:` line or explicit "done when X"). Open-ended prompts run far longer; adding a stop condition cut one practitioner's median session 2h20m → 14min.

**Role + output** — first line assigns a specific role; specify a *structured output shape*, not free-form "summarize and synthesize". Both measurably cut mission creep.
