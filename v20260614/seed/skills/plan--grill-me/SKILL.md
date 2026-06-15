---
name: plan--grill-me
description: Interview the user relentlessly about a plan, design, or product/architecture decision until reaching shared understanding, resolving each branch of the decision tree. Use when the user wants to stress-test a plan, get grilled on a design, says "grill me", or before committing to a new project structure (see `plan`).
metadata:
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
  refs-external:    # intentional forward-pointers; not seeded (see ref_lint.py)
    - audit--improve-codebase-architecture
    - design--define-ux-architecture
    - plan--prd
    - plan--setup
---

## Invocation
`/plan-grill-me` · Triggers: grill me, stress-test plan

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Related
- `plan--prd` — follows: grill-me stress-tests the plan; PRD formalizes the result
- `design--define-ux-architecture` — companion: grill-me at the IA decision gate
- `plan--setup` — companion: grill-me before committing to a new project setup
- `ops--swarm` — precedes: grill-me stress-tests the swarm decomposition plan
- `audit--improve-codebase-architecture` — companion: grilling loop runs within architecture improvement
