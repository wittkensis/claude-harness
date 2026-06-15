---
name: diagnose
description: Disciplined diagnosis loop for hard bugs and performance regressions. Reproduce → minimise → hypothesise → instrument → fix → regression-test. Use when user says "diagnose this", "debug this", reports a bug, says something is broken/throwing/failing, or describes a performance regression.
---

# Diagnose

A discipline for hard bugs. Skip phases only when explicitly justified.

## Phase 1 — Build a feedback loop

**This is the skill.** Without a fast, deterministic, agent-runnable pass/fail signal, nothing else works.

**Try in order:**
1. Failing test at the bug's seam
2. Curl/HTTP script against dev server
3. CLI invocation with fixture input, diffing stdout
4. Headless browser script (Playwright/Puppeteer)
5. Replay a captured trace
6. Throwaway harness — minimal system subset, single function call
7. Property/fuzz loop — 1000 random inputs
8. Bisection harness — `git bisect run`

**Make the loop better:** faster · sharper signal · more deterministic.

For non-deterministic bugs: loop 100×, parallelize, inject stress — raise the reproduction rate until debuggable.

**UI/overlay/z-index bugs require a visual feedback loop.** Reading CSS and JSX is not Phase 1 — it's guessing. The loop must be a headless browser (Playwright at 390×844 for iOS) that:
- Screenshots the affected state (sheet open, header after scroll, etc.)
- Inspects computed styles via `getComputedStyle`, `getBoundingClientRect`, `parentElement`
- Checks for hydration errors via `page.on('pageerror', ...)`

`z-index`, `position: fixed`, and React hydration all interact in ways that only manifest at runtime. Code reading cannot substitute for this.

**For "sheet below nav" bugs specifically:** the fix is almost never `createPortal`. It is: (1) check for an ancestor with `transform`/`filter`/`perspective` containing fixed positioning, (2) check for a `<button>` inside `<button>` causing hydration failure, (3) check that the deployed version is actually current. `createPortal` + `mounted` guard introduces timing issues that can manifest differently in prod vs dev.

Do not proceed to Phase 2 without a loop you believe in.

## Phase 2 — Reproduce

Run the loop. Confirm:
- [ ] Failure mode matches what the user described (not a nearby failure)
- [ ] Reproducible across multiple runs
- [ ] Exact symptom captured

## Phase 3 — Hypothesise

Generate 3-5 ranked hypotheses. Each must be falsifiable:

> "If X is the cause, then changing Y will make the bug disappear."

Show ranked list to user before testing. Cheap checkpoint, big time saver.

## Phase 4 — Instrument

Each probe maps to a specific prediction from Phase 3. **One variable at a time.**

- Debugger/REPL inspection preferred
- Targeted logs at boundaries distinguishing hypotheses
- Never "log everything and grep"
- Tag every debug log: `[DEBUG-a4f2]` — cleanup = single grep

**Perf:** establish baseline measurement first, then bisect. Measure before fixing.

## Phase 5 — Fix + regression test

Write regression test before the fix — only if a correct seam exists (tests real bug pattern at the call site, not a shallow imitation).

1. Turn minimised repro into failing test
2. Watch it fail
3. Apply fix
4. Watch it pass
5. Re-run Phase 1 loop against original scenario

## Phase 6 — Cleanup

- [ ] Original repro no longer reproduces
- [ ] Regression test passes (or no-seam documented)
- [ ] All `[DEBUG-...]` removed
- [ ] Throwaway prototypes deleted
- [ ] Correct hypothesis stated in commit message
