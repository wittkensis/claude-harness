---
name: ops--laundry-list
description: Orchestrate a batch of work items — bugs, features, tasks, or any mix — across one or many apps. Triages the whole list, fans out parallel recon/planning agents per cluster, applies the right per-item discipline (canary for bugs, build for features), fixes shared roots once, parallelizes independent work, and re-validates every consumer. Use when handing off a punch list or a batch of mixed bugs/features across one or many apps.
metadata:
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
---

# Laundry List

## Invocation
Triggers: punch list, fix these, laundry list, batch of bugs or features, mix of tasks

A batch isn't N independent tickets — most items share roots, context, or affected code. Run it as a pipeline, not top-to-bottom.

**Per-item discipline:**
- Bugs → invoke `canary` (invariant → blast radius → class → altitude → codify)
- Features → invoke `build` (scope → design gate → implement → validate intent)
- Mix → classify each item first, then apply the right discipline

---

## Pipeline

### 1. Triage the whole list before touching anything

Read every item. Classify each as bug / feature / refactor / task. Group by **suspected shared root or context** — three spacing bugs may be one token; two new list features may share a component. Separate **shared-base** changes from **app-specific** ones. Flag user constraints ("don't touch X", "ship by Friday"). Surface any item that needs a judgment call or is destructive — ask up front in one `AskUserQuestion`, not mid-work.

### 2. Parallel recon/planning — before doing anything

Spawn **one read-only `Explore` agent per cluster**, `run_in_background: true`:
- **Bug clusters** → blast radius (file:line, invariant, local → app → fleet, root hypothesis)
- **Feature clusters** → dependency map (what shared code is affected, what needs to be built first, what's independent)

Wait for all agents to report, then synthesize. Recon sometimes surfaces a bug worse than reported (security leak, crash, data corruption) — triage those to the front and get the user's call if outward-facing.

### 3. Order by impact and dependency, not list order

1. Shared-base changes (token, shared component, shared lib) — ripple everywhere; do first
2. Items with dependents (a new shared component other features need)
3. Independent app-specific items (parallelizable)

After any shared fix, **re-measure** — downstream items may already be resolved or unblocked.

### 4. Execute at the right altitude

- **Shared root / shared component** → fix or build once at source, propagate to all consumers. Honor stated constraints with scoped overrides.
- **Coupled changes** (a CSS animation duration that a JS timeout depends on, an API shape that multiple callers use) → ship together, not half.
- **Independent items** → spawn **one `general-purpose` agent per app**, `run_in_background: true`, each owning its disjoint repo. Hand each a precise spec from recon, the list of files already touched (fence off collisions), "commit, don't push."

### 5. Validate — proof, not vibes

- Build/typecheck every repo touched. Shared-base changes → re-validate **all** consumers.
- Visual testing for any UI change — before/after, actually look.
- For bugs: re-run the recon search → zero remaining occurrences.
- For features: exercise the feature as specified — "it compiled" is not done.

### 6. Codify (for systemic fixes)

Per canary: turn each systemic bug fix into something un-reintroducible — token/class, tightened skill, fleet-audit dimension, or test assertion. Features don't need this step unless they establish a new shared pattern worth encoding.

### 7. Report

Per-item output (canary blocks for bugs, brief summary for features) **plus** a roll-up table:
`item → type → cluster → shared? → action → consumers affected → validated`

Call out: which items were one shared root, what was codified, anything deferred with reason.

---

## Parallelism

| Phase | Parallel? | Agent type |
|---|---|---|
| Recon / planning | Yes — one per cluster | `Explore` (read-only) |
| Shared-base fix/build | No — single owner | self |
| App-specific work | Yes — one per app | `general-purpose` |
| Validation | Yes — per app | `evaluator` / self |

---

## Guardrails

- **Triage before acting.** Top-to-bottom re-solves the same root five times or builds the same component twice.
- **One shared change, not N hand-patches.** If it's shared, fix/build it once at the source.
- **Don't blanket-apply without confirming the same root** — similar symptoms can have different causes.
- **Don't scope-creep.** Close the items on the list; use `audit--slop` separately for unrelated cleanup.
- **Watch the orchestrator's context budget.** Fan-outs keep recon and per-app work out of your context. If you're hand-editing every app inline, you're doing it wrong.

## Related
- `audit--canary` — companion: laundry-list orchestrates; canary is invoked per bug item
- `ops--swarm` — companion: swarm for a new feature build; laundry-list for a batch of mixed items
- `build--diagnose` — companion: diagnose handles individual hard reproduction loops within the batch
- `log--issues` — precedes: issues define the vertical slices that become laundry-list items
- `ops--tool-resilience` — companion: resilience handles auth failures that block individual batch items
