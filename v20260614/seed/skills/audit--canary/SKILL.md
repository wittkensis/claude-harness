---
name: audit--canary
description: For any bug — single or in a batch — treat it as a possible symptom of a broader pattern before fixing. Names the invariant violated, measures blast radius (file → app → fleet), classifies root cause, fixes at the right altitude, and codifies so the class can't recur. Trigger-only: load when a fix smells systemic / shared-root, when triaging a batch of related bugs, or when explicitly asked for a canary/blast-radius pass. DO trigger on canary, blast radius, this smells systemic, fix across apps, root cause. Not for routine one-off bugs (just fix those).
metadata:
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
---

# Canary in the Coalmine Audit

## Invocation
Triggers: single bug, bug that smells systemic, canary

A bug is a **sample from a distribution**. The dead canary isn't the problem — it's the warning the air is bad everywhere. Fix the instance **and** close the class.

For batch work, `laundry-list` handles the orchestration. This skill is the per-bug loop that laundry-list invokes for each item.

---
## RULES

- **Don't stop at the symptom.** A patched instance with the class still open is an unfixed bug.
- **Don't blanket-fix without confirming the same root.** Two similar-looking bugs can have different invariants.
- **Don't scope-creep.** Close the class this canary points to; don't fold in unrelated refactors.
- **Honor altitude both ways** — don't fix a one-off as a fleet change, and don't fix a fleet problem six times by hand.

---

## LOOP

### 1. Reproduce & Locate
Find the exact instance: file:line, the offending markup/CSS/logic.
### 2. Name the broken rule
State the invariant that *should* hold (token, class, contract, convention). If you can't name it, you don't understand the bug yet.
### 3. Measure blast radius
Search for every occurrence in three scopes:
- **Local** — same file/component
- **App-wide** — everywhere in this repo (`rg`)
- **Fleet-wide** — every app under `{{harness.config.projects[0].path}}/v*` + shared base in `TEMPLATES/themes/`. Report counts + locations. "1 of 6 apps" vs "11 occurrences across 4 apps" changes the fix.
### 4. Classify
| Class                        | Meaning                                                  | Fix at                              |
| ---------------------------- | -------------------------------------------------------- | ----------------------------------- |
| **One-off**                  | Genuinely isolated; pattern holds elsewhere              | Instance                            |
| **Inconsistent application** | Correct shared pattern exists, not applied here          | All violating instances             |
| **Missing pattern**          | No shared rule — each app hand-rolls it                  | Codify first, then apply everywhere |
| **Broken pattern**           | The shared base itself is wrong → all consumers affected | Source in `TEMPLATES/themes/`       |
### 5. Fix at the right altitude
Never patch a systemic bug as a one-off.
### 6. Codify
Make the class un-reintroducible: add a test assertion that fails on regression, tighten a shared style token or component, or add a validation step to your deploy process. If only memory prevents recurrence, it's not fixed.
### 7. Validate
Re-run the search → zero remaining. For UI changes, re-run affected scenarios; for any shared style/token edit, re-validate every consumer.

### 8. Log to learning record
```bash
python3 ~/.claude/state/learning-log.py \
  --kind canary --target <app-or-fleet> \
  --outcome fixed   # or: recurred (if the class had appeared before) \
  --skill audit--canary --detail "<invariant-name>"
```

---

## OUTPUT

Format per bug:
```
BUG: <reported>
  Instance:     <file:line + offending construct>
  Invariant:    <the rule that should hold>
  Blast radius: local:N · app:N · fleet:N/6  [locations]
  Class:        one-off | inconsistent | missing-pattern | broken-pattern
  Fix:          <what changed, at what altitude>
  Prevention:   <token/class/contract/assertion added>
  Verified:     <search clean · scenarios pass on apps X,Y>
```

## Related
- `ops--laundry-list` — companion: laundry-list orchestrates batch work and calls canary per bug
- `build--diagnose` — alternative: diagnose is for hard reproduction loops; canary is for systemic class analysis
- `audit--slop` — companion: slop removes cruft after canary closes the class
- `ops--backlog` — follows: log canary findings as backlog items for systematic follow-through
- `eval--tdd` — follows: add a regression test to prevent the class recurring
