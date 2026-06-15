---
name: ops--swarm
description: Orchestrate a parallel multi-agent build swarm. Decompose a new app, feature, or audit into independent workstreams and run them as concurrent background worktree workers, then integrate and validate. Use when building a new app, adding a sizeable feature, or running a cross-cutting audit — especially when the work splits into parts that can run in parallel.
metadata:
  kind: playbook
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
---

# Swarm — Parallel Build Orchestrator

## Invocation
Triggers: build new app, big feature, parallel build, agent swarm, orchestrate, fan out

The front door for **build app / add feature / run audit**. You (the main session) are the orchestrator. You decompose the job, fan out `swarm-worker` agents into isolated git worktrees, then fan in, integrate, and validate. Reliability comes from a strict worker contract, disjoint file ownership, a durable task board, and a hard validation gate — not from hope.

## Autonomy (default: max)

Run the whole tree **end-to-end without stopping**, surfacing failures loudly. This skill is the deliberate exception to the global "pause at each phase transition" rule — that rule does **not** apply here unless the user asks for gates.

**Optional pre-launch gates.** Before launching, check whether the user named gates in their request (e.g. "gate at decompose", "let me approve the plan", "stop before integrate"). If they did, pause only at those points. If they named none, run fully autonomous and only stop on failure. Never invent gates.

## Pre-flight (always run first)

Before any fan-out, verify two things:

1. **Git repo exists.** `isolation: "worktree"` requires a git repo — it will fail silently without one. Check: `ls .git` or `git rev-parse --git-dir`. If missing, either run `git init && git add . && git commit -m "init"` or surface the gap to the user. Never launch worktree workers into a non-git directory.

2. **Parallelism is worth it.** Only swarm if ≥2 genuinely independent units exist. A single-unit job → run inline or with one worker. State the decision before proceeding.

---

## The logic tree

### 0 — Triage
Classify the job and decide whether to swarm at all.

| Type | Pipeline | Parallelism |
|------|----------|-------------|
| **App** (new) | brief → research → plan → concepts → build → validate | parallelize **within** the build phase only |
| **Feature** | plan → build → validate | parallelize the build |
| **Audit** | scope → fan out (read-only) → synthesize | fully parallel, no merge step |

**Parallelize check:** only swarm if the job has ≥2 genuinely independent units. A small or linear job → run a **single** `swarm-worker` (or do it inline) — never pay N cold-starts for one unit of work. State the decision in one line and proceed.

### 1 — Decompose
Use the `Plan` agent to produce a **workstream manifest**. Each unit:

```
- id:        kebab-name
  scope:     one sentence
  owns:      [explicit file/dir paths this unit may write]
  depends:   [ids that must finish first]  (empty = wave 1)
  done:      testable completion criterion
```

**HARD CHECK before fan-out:** every `owns` set is **disjoint** — no two concurrent units write the same file. If two units need the same file, either merge them into one unit or serialize them across waves. This is what prevents merge hell. If you cannot make a wave's units disjoint, do not launch that wave in parallel.

Group units into **waves** by dependency depth (wave 1 = no deps; wave 2 = depends only on wave 1; …).

### 2 — Fan out
**Write the shared brief once.** Before fanning out, write the *invariant* context every worker needs — the overall goal, architecture, conventions, shared constraints, done-definition — to one file (e.g. `plan/swarm-brief.md`) and hand each worker its path. This kills N cold-start re-derivations of the same context. It does **not** replace per-worker scoping: the brief carries only what's common to all; each worker still gets only the *slice-specific* detail it owns (the shared brief + scoped slice, never a shared pile of everything).

Register every unit on the Task board (`TaskCreate`) so state survives compaction. Then, **wave by wave**:

- For each unit in the wave, in **one message**, spawn:
  `Agent(subagent_type: "swarm-worker", run_in_background: true, isolation: "worktree")`
- **Brief each worker like a teammate, not a chat prompt:** role + goal, scope & guardrails, numbered deliverables, output format. Hand it only the context its slice needs — *scoped memory per worker, not a shared pile.* Memory design is the single biggest predictor of swarm success, ahead of model smarts.
- **Route by skill profile.** Code unit → `swarm-worker`. Pure research/search unit → `Explore` or `researcher`. Infra/audit unit → `fleet--ops-agent`. Don't make one generalist do work a specialist agent does better.
- Mark each `TaskUpdate` → in_progress.
- Wait for the wave to finish before starting the next wave (deps require it).

### 3 — Fan in
As workers report:
- Success → record the worktree + summary; `TaskUpdate` → completed.
- Failure → **retry once** via `SendMessage` to that worker with the error context. Still failing → mark blocked, **fail loud**, and do not silently drop it. A failed dependency blocks its dependents — surface that.

### 4 — Integrate
Merge worktrees in dependency order. Disjoint ownership means conflicts should be rare; if one appears, it signals a decomposition leak — resolve and note it. Run typecheck across the merged tree.

### 5 — Validate (hard gate)
Two-step completion gate: (1) typecheck passes; (2) **exercise** the feature with the `verify`/`run` skill and confirm it does what triage said it would. "It compiled" is not done. If the app can't be run, state explicitly why and what was confirmed instead.

**Verify the risky parts first** — numbers, data, citations, auth, anything load-bearing. Retry catches *crashes*; it never catches a worker that returned confident, plausible-looking, **wrong** output. That's the failure that survives into the merge, so hunt it on purpose.

After the gate result is known, append to the learning log:
```bash
python3 ~/.claude/state/learning-log.py \
  --kind swarm-validate --target <feature-or-app> \
  --outcome pass   # or: fail \
  --skill ops--swarm --detail "<one-line cause if fail>"
```
The log is centralized (`~/.claude/state/`), so this applies in every context, not just fleet.

**Have a fleet of related apps?** Create a `myfleet--swarm` skill that adds your fleet-specific wiring (deploy, preflight, validation) on top of `ops--swarm`. Use `ops--swarm` directly for standalone apps or pure research swarms.

## Git worktrees — the critical enabler

**Worktrees are what make true parallelism viable** — the single highest-leverage primitive here. Each worker gets its **own working directory on its own branch**, so N sessions edit the same repo without colliding on file state. Without them, parallel workers on one repo corrupt each other's working tree constantly. This is non-negotiable for any multi-worker wave.

**How it works in this harness:** spawn each worker with `isolation: "worktree"` — the runtime runs `git worktree add` for you, on a fresh branch, auto-cleaned if unchanged. You do **not** hand-roll worktrees in the normal path; the flag is the contract.

**The manual equivalent** (what the flag automates; use only when driving sessions yourself outside the Agent tool):
```bash
git worktree add ../<repo>-<unit-a> -b swarm/<unit-a>    # worker A: own dir + branch
git worktree add ../<repo>-<unit-b> -b swarm/<unit-b>    # worker B
# launch a session in each; integrate by merging swarm/<unit-*> back to the branch
git worktree remove ../<repo>-<unit-a>                    # cleanup after merge
```

**Branch-per-worker is the model:** one branch per unit (`swarm/<unit-id>`), worker commits only on its branch in its own dir, orchestrator merges branches in dependency order at **Integrate**. Disjoint file ownership (step 1) + separate worktrees together guarantee no merge hell. Settings: `worktree.baseRef` ("fresh" branches off origin/default; "head" off local HEAD), `worktree.symlinkDirectories` (e.g. `node_modules`) to avoid disk bloat across many worktrees.

**fleet apps:** the repo root is `{{harness.config.projects[0].path}}/v{N}_{app}-ericwittke-com/`; worktrees branch off **that** repo. Don't create a worktree of the whole `Apps-Workspace`.

## Reliability mechanisms (why this is dependable)

- **Git worktrees** — own dir + branch per worker → genuine parallel edits, no working-tree collision. The enabler.
- **Worker contract** — predictable in, structured out. See `agents/swarm-worker.md`.
- **Disjoint ownership** — no concurrent writes to the same file → no merge hell.
- **Task board** — durable state across context compaction.
- **Dependency waves** — correct ordering, no race on unfinished deps.
- **Retry + fail-loud** — no silent drops.
- **Validation gate** — proves intent, not just compilation.

## Audit mode specifics

Audits are read-only and safe → ideal for full autonomy and recurring runs. Fan out `Explore` (search), `researcher` (research), or `fleet--ops-agent` (infra) workers, then synthesize into one report. No worktrees, no integrate step. For a recurring audit, this is a candidate for `CronCreate` / an autonomous loop.

## Quick map

| Step | Tool |
|------|------|
| Decompose | `Plan` agent |
| Track | `TaskCreate` / `TaskUpdate` |
| Fan out | `Agent(swarm-worker, run_in_background, isolation:"worktree")` |
| Retry worker | `SendMessage` |
| Code conventions inside workers | `build` skill specialties (stacks / tdd / tauri / ai) |
| Validate | `verify` / `run` |

## Where these practices come from

Field rules that shaped this skill: pick wide/independent/ends-in-files work; expect workers to fail and recover surgically; scoped memory beats a shared pile; read the plan before it runs (the cheapest intervention); verify confident-wrong output, not just crashes.

## Related
- `ops--laundry-list` — alternative: laundry-list for mixed batch items; swarm for large parallel builds
- `plan--grill-me` — precedes: stress-test the decomposition plan before launching workers
- `log--issues` — feeds-into: issues become swarm workstream units
- `ops--tool-resilience` — companion: resilience handles auth failures in individual workers
- `ops--handoff` — companion: handoffs coordinate between orchestrator sessions
