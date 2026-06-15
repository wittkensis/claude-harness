---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable GitHub issues using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work.
---

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

## Process

1. **Gather context** from conversation. If user passes issue reference, fetch it.
2. **Explore codebase** to understand current state. Use domain vocabulary.
3. **Draft vertical slices** — each cuts through ALL layers end-to-end (not horizontal layer-by-layer). Each slice must be demoable on its own. Prefer many thin slices.
4. **Quiz the user** — present numbered list showing: Title, Type (HITL/AFK), Blocked by, User stories covered. Iterate until approved.
5. **Publish issues** in dependency order (blockers first) so you can reference real IDs.

## Issue Template

```markdown
## What to build
[End-to-end behavior, not layer-by-layer. No specific file paths.]

## Acceptance criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by
[Blocking ticket or "None — can start immediately"]
```

**HITL** = requires human interaction (architectural decision, design review)
**AFK** = can be implemented and merged without human interaction — prefer these
