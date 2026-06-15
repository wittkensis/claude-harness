---
name: prototype
description: Build a throwaway prototype to flush out a design before committing. Routes to terminal app (logic/state questions) or UI variations (design questions). Use when user wants to prototype, sanity-check a data model, mock up a UI, or says "prototype this" / "let me play with it" / "try a few designs".
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

- **"Does this logic/state model feel right?"** → terminal app that pushes the state machine through hard cases
- **"What should this look like?"** → several radically different UI variations on one route, switchable via URL param

If ambiguous and user unreachable: default to whichever matches surrounding code (backend module → logic; page/component → UI) and state the assumption.

## Rules (both branches)

1. **Throwaway from day one** — name it clearly as a prototype, locate near what it's prototyping for
2. **One command to run** — use existing task runner (`pnpm <name>`, `python <path>`)
3. **No persistence** — state in memory unless persistence is the thing being tested
4. **Skip polish** — no tests, minimal error handling, no abstractions
5. **Surface the state** — after every action, print/render full relevant state
6. **Delete or absorb** — when the question is answered, delete it or fold it into real code

## When done

Capture the answer somewhere durable (commit message, ADR, issue, or `NOTES.md`). The answer is the only thing worth keeping.
