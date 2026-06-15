---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development.
---

# TDD

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
