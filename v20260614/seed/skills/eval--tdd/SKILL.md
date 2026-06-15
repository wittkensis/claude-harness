---
name: eval--tdd
description: Test-driven development with red-green-refactor loop. Use when building features or fixing bugs with TDD, mentions "red-green-refactor", wants test-first development, or needs integration test strategy.
metadata:
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
  refs-external:    # intentional forward-pointers; not seeded (see ref_lint.py)
    - audit--improve-codebase-architecture
    - build--react
    - plan--prd
---

# TDD

## Invocation
Triggers: tdd, test-driven, red-green-refactor, test first, integration test

## Philosophy

Tests verify behavior through public interfaces, not implementation details. A good test reads like a specification. It survives refactors because it doesn't care about internal structure.

**Bad tests:** mock internal collaborators · test private methods · break when you refactor but behavior is unchanged.

## Anti-Pattern: Horizontal Slices

**DO NOT** write all tests first, then all code. Instead: **vertical slices**.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4
  GREEN: impl1, impl2, impl3, impl4

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  ...
```

## Workflow

### 1. Plan
- Confirm interface changes and which behaviors to test (prioritize)
- Design for testability — deep modules (small interface, deep implementation)
- List behaviors to test, not implementation steps
- Get user approval

### 2. Tracer Bullet
One test → one implementation. Proves the path works end-to-end.

### 3. Incremental Loop
For each behavior:
- RED: write test → fails
- GREEN: minimal code to pass
- Never anticipate future tests

### 4. Refactor
After all tests pass:
- Extract duplication
- Deepen modules
- Never refactor while RED

## Checklist Per Cycle

- [ ] Test describes behavior, not implementation
- [ ] Test uses public interface only
- [ ] Test would survive internal refactor
- [ ] Code is minimal for this test
- [ ] No speculative features added

## Related
- `build--diagnose` — precedes: diagnose identifies the bug; TDD writes the regression test
- `audit--canary` — companion: canary classifies the bug class; TDD codifies the fix at a seam
- `build--react` — companion: TDD applies at React component seams and API route boundaries
- `audit--improve-codebase-architecture` — companion: deep modules enable better TDD
- `plan--prd` — precedes: PRD acceptance criteria become TDD test scenarios
