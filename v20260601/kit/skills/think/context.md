# Context Sentinel

**Always active meta-layer. Shapes HOW you work, not what you work on.**

## Core Principle

Compacting = failure. Lost context means repeated work and quality drops.

---

## Context Budget

| Level | Action |
|-------|--------|
| <50% | Continue normally |
| 50-70% | Ask: can anything go to librarian subagent? |
| 70-85% | `/compact` proactively OR commit and summarize |
| >85% | Commit work, start new thread with summary |

Check with `/context`. Early warning signs: re-reading same files · explaining obvious context · long tool outputs accumulating.

---

## Session Structure

```
1. Define objective (1 sentence) — this is the validation target at the end
2. Strategy gate: is this execution or a strategy/product decision?
   → Decision: offer grill-me before committing to the approach
   → Execution: confirm it serves the project's north star (see ~/.claude/goals.md)
3. Plan approach (concise)
4. Execute in chunks → commit each chunk
5. Delegate heavy research to librarian
6. Validate intent: before reporting done, demonstrate the objective from step 1 is
   actually met — run the app, exercise the feature, confirm behavior against the
   stated goal. Not "I believe it works." Evidence it works.
7. End with summary commit
```

**Each thread = ONE clear objective.** If scope creeps, commit and start new thread.

**Strategy vs. execution balance:** Claude is most valuable when used for strategy — architecture choices, product decisions, "should I build this at all?" — not just execution. When a session is entirely execution with no strategic questions, ask once whether the work is aimed at the project's north star.

---

## Git as External Memory

The codebase is persistent. Your context window is not.

```bash
# Good commit — tells the story
git commit -m "Add user auth: login/logout working, registration pending"

# Bad commit
git commit -m "WIP"
```

### Commit-and-Continue Pattern
1. Complete logical chunk
2. Git commit with clear message
3. Context "saved" in codebase
4. Start fresh thread if needed — git log tells the story

---

## Librarian Delegation

Heavy research pollutes context. Delegate it.

```
"Research X and summarize:
- Key findings (3-5 bullets)
- Recommendation with rationale
- Confidence level"
```

Librarian returns ~500 tokens, not ~5000 tokens of raw research.

---

## Summary Handoffs

When starting new thread after context-heavy work:

```markdown
## Session Summary: [Date/Topic]

### What Was Done
- Completed X
- Made progress on Y

### Current State
- File A is in state B

### What's Next
1. Finish D
2. Test E

### Key Decisions Made
- Chose approach X because Y
```

Save to `.claude/` folder or use as commit message.

---

## Plan Mode Rules

Plans should be concise (10-20 lines max):
- List files that will be modified
- Include verification steps
- Note dependencies
- End with "Unresolved Questions" section
- Don't plan what you can just do

---

## Anti-Patterns

**NEVER:** Let auto-compact surprise you · continue with bloated context · research inline when librarian can summarize · start without clear objective · end without summary/commit
