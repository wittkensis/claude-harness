# System Optimizer

Continuously improve the agentic system — skills, agents, CLAUDE.md, design systems.

## When to Invoke

- After completing a project (capture learnings)
- When skills feel redundant or disconnected
- When new research suggests improvements
- Quarterly review

---

## Optimization Workflow

### 1. Audit Current State

```bash
ls -la ~/.claude/skills/          # Active skills
ls -la ~/.claude/agents/          # Agents
ls -la ~/.claude/design-systems/  # Design systems
wc -l ~/.claude/CLAUDE.md         # Should be < 200 lines
```

### 2. System Health Checklist

- [ ] Skills have clear, non-overlapping triggers
- [ ] Agents only used when separate context truly needed
- [ ] Design systems versioned (v1.0, v1.1)
- [ ] CLAUDE.md under 200 lines
- [ ] Skills reference each other correctly (no broken paths)
- [ ] Research insights integrated into relevant skills
- [ ] Component size limits documented

### 3. Common Optimizations

| Symptom | Fix |
|---------|-----|
| Skills overlap significantly | Merge or clarify triggers |
| Agent does what a skill could | Convert to skill (saves context) |
| Skill is too large (>500 lines) | Split by concern |
| Skills don't coordinate | Add cross-references |
| Outdated patterns | Update from research folder |

---

## Skill Lifecycle

### Creating
1. Identify recurring pattern
2. Draft with clear triggers and description
3. Keep SKILL.md minimal (< 100 lines) — move details to sub-files
4. Add cross-references
5. Update CLAUDE.md triggers

### Updating
1. Read current content
2. Make focused edit (not full rewrite unless necessary)
3. Verify cross-references still work

### Retiring
1. Document why
2. Migrate unique content to other skills
3. Update skills that reference it
4. Move to `_archive/`
5. Update CLAUDE.md

---

## Metrics

| Metric | Target |
|--------|--------|
| CLAUDE.md size | < 200 lines |
| Individual skill sizes | < 300 lines |
| Sub-file sizes | < 500 lines |

---

## Quarterly Review Template

```markdown
## Q[X] 2026 System Review

### Goal Alignment (check goals.md)
- Which projects moved toward their north star?
- Which drifted into feature-building without serving the guarding metric?
- Does the life priorities order still reflect reality?
- Any project to pause or kill?

### Strategy/Execution Balance
- Was Claude used mostly for execution (building things) or strategy (deciding what to build)?
- Were major architecture/product decisions challenged with grill-me or extended critique?

### Usage Observations
- Which skills loaded most often?
- Which were confusing or overlapping?
- What tasks lacked appropriate skills?

### Research Integrated
- [ ] [Title] → [Skills updated]

### Changes Made
- [Change 1]

### Action Items
- [ ] [Item 1]
```
