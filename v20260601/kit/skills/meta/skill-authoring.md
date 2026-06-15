---
name: skill-authoring
description: Create and scaffold agent skills — global user-level skills and project-local skills. Use when creating, writing, or scaffolding any skill.
---

# Skill Authoring

Two types of skills:

| File | When |
|------|------|
| This file | Global skill — lives in `~/.claude/skills/`, triggered system-wide |
| [project-skill.md](project-skill.md) | Project skill — `{proj}--{purpose}` in `.claude/skills/`, project-scoped |

## Global Skill Process

1. **Gather requirements** — domain, use cases, scripts needed, reference materials
2. **Draft** — SKILL.md (< 100 lines) + specialty files if content > 500 lines
3. **Review with user** — does this cover your use cases?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required, < 100 lines)
├── specialty.md       # Detailed sub-file (if needed)
└── scripts/           # Utility scripts (if needed)
```

## SKILL.md Template

```md
---
description: What it does. Use when [specific triggers].
---

# Skill Name

Route to sub-files or quick reference here.

## Quick Reference
[Minimal working example or key rules]
```

## Description Requirements

- Max 1024 chars
- First sentence: what it does
- Second sentence: "Use when [specific triggers]"

## When to Split Files

- SKILL.md exceeds 100 lines
- Content has distinct domains
- Advanced features rarely needed

## Review Checklist

- [ ] Description includes triggers
- [ ] SKILL.md under 100 lines
- [ ] No time-sensitive info
- [ ] Concrete examples included
