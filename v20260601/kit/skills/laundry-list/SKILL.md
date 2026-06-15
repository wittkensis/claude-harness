---
name: laundry-list
description: Orchestrate a multi-bug "bug bash" — a punch list of fixes across one or many apps — end to end. Use when the user hands over a batch of bugs/issues/UI nits ("fix these", "here's a list", "punch list", "bug bash", "laundry list", "clean up these"), especially across multiple apps or with shared/design-system symptoms. Triages the whole list, fans out PARALLEL read-only recon agents to measure blast radius, AUTO-INVOKES the canary-in-the-coalmine discipline per bug, fixes shared roots once then propagates, parallelizes app-specific fixes across disjoint repos, and re-validates every consumer (build + visual testing). The orchestration layer above canary (per-bug) and slop-audit/diagnose.
---

# Laundry List

A bug bash is not N independent tickets — it's one **distribution** sampled N times. Most
"small bugs" on a real punch list are the same few systemic faults wearing different masks.
This skill runs the whole bash as a pipeline: **triage → recon (parallel) → fix at altitude →
validate**, and it **auto-invokes `canary-in-the-coalmine`** for the per-bug discipline
(invariant → blast radius → class → altitude → prevention). Use `canary` when you have ONE
suspicious bug; use `laundry-list` when you have a LIST.

> This skill is workspace-aware (every project in your workspace + any shared
> design-system/module + shared skills). For a single-repo bash, "workspace" is
> just that repo and its shared modules — the pipeline is identical.

---

## The pipeline

### 0. Load canary
Read `canary-in-the-coalmine` first (or invoke the Skill). Every bug on the list is processed
through its loop. This skill adds the orchestration *around* it: batching, parallelism, and
validation. Do not re-derive canary's classification table — reuse it.

### 1. Triage the WHOLE list before touching anything
Read every item. Do not fix top-to-bottom. Group items by **suspected shared root**, not by
where they appear:
- Cluster symptoms that smell like one cause (three "spacing" nits → one token; "bullets" +
  "wrong padding" → one row pattern; "X doesn't match the theme" → one un-tokenized value).
- Separate the clusters into **shared-base** (design system / shared component / shared lib)
  vs **app-specific** (one app's logic, data, or layout).
- Flag any **constraints** stated by the user (e.g. "don't change the LCARS theme",
  "don't touch X") and any **subjective/design** items ("make it more fun", "match iOS") that
  need a judgment call + visual validation rather than a mechanical fix.
- Surface anything that is genuinely the user's decision (architecture forks, destructive
  data fixes, anything outward-facing) and ask up front — one batched `AskUserQuestion`, not a
  drip of questions mid-fix.

### 2. Recon in PARALLEL — measure blast radius before fixing
For each cluster, you need to know how far it reaches. Fan this out: spawn **one read-only
`Explore` (or general-purpose) agent per cluster**, `run_in_background: true`, each owning a
non-overlapping set of bugs. Each agent reports, per bug: the offending construct (file:line),
the invariant that should hold, and the blast radius across three scopes (local → app →
fleet/other consumers) with counts + locations, plus a root-cause hypothesis and a one-line
fix direction. Give each agent the exact repos/paths and tell it conclusions-over-dumps.

Why parallel: recon is read-heavy and independent; running clusters concurrently keeps the
orchestrator's context clean and is dramatically faster than serial grepping. Wait for all to
report, then synthesize.

> The recon agents often surface a bug that's worse than reported (e.g. a committed secret, a
> security/data leak, a crash). Triage those to the FRONT and, if outward-facing or
> destructive, get the user's call before proceeding.

### 3. Order by blast radius, not by list order
1. **Broken/missing shared pattern** (design-system token, shared base CSS, shared component,
   shared lib) — these ripple to every consumer; fix first.
2. **Inconsistent application** (a correct shared pattern exists but some consumers drifted).
3. **True one-offs** (app-specific logic/data/layout).
Fixing a root often clears several list items at once — so fix the root, then **re-measure**
before touching anything downstream; don't re-fix cleared items as one-offs.

### 4. Fix at the right altitude
- **Shared root → fix once at the source, then propagate.** Edit the canonical source (e.g.
  your shared design-system module), then copy/propagate to every consumer and verify
  byte-identical. Add new shared tokens/classes rather than hand-patching each site. Honor
  stated constraints with scoped neutralizers (e.g. `[data-theme="lcars"] .new-thing { …reset }`)
  so protected surfaces are provably unchanged.
- **Coupled changes** (CSS whose timing/animation a JS component depends on, e.g. a sheet
  close-timeout matching an animation duration) must change **together** — don't ship the base
  change without syncing every consumer's coupled constant, or you leave a broken intermediate.
- **App-specific fixes → parallelize across DISJOINT repos.** Spawn one background
  general-purpose agent **per app**, each editing only its own directory (apps are separate
  repos → no file conflicts). Hand each a precise, file:line-level spec derived from recon, the
  list of files the orchestrator has already touched (to fence off collisions), and "commit in
  that repo, don't push." Keep the deploy target / highest-risk app for yourself.
- Don't fix a one-off as a fleet change, and don't hand-fix a fleet problem six times.

### 5. Validate every consumer — proof, not vibes
- **Build/typecheck** each app you touched (`npx tsc --noEmit` + the build). A shared-base edit
  means re-validating **every** consumer, not just the one you were looking at.
- **Visual testing for any UI change** — run the scenario screenshots (your visual test suite /
  the per-app Playwright specs), before/after, and actually look. Subjective items
  ("more fun", "match iOS") and protected surfaces (the LCARS constraint) are confirmed by eye,
  not by "it compiled". Re-shoot the protected theme to prove it's unchanged.
- Re-run the recon search → confirm the class is closed (zero remaining occurrences).

### 6. Codify so it can't recur
Per canary step 6: turn each systemic fix into something un-reintroducible — a shared
token/class/contract, a tightened shared skill, a new audit dimension, or a
a visual-test assertion that fails on regression. If the only thing stopping recurrence is
your memory, it isn't fixed.

### 7. Report — the canary report, batched
End with the per-bug blocks (canary's output format) **plus** a roll-up table:
`bug → cluster → scope → systemic? → root cause → action → siblings fixed → validated`.
Call out: which "small bugs" were actually one systemic fault, what was codified, any canary
that revealed a real fleet-wide gap, and anything deferred (with why).

---

## Parallelism cheat-sheet
| Phase | Parallel? | Agent type | Isolation |
|-------|-----------|------------|-----------|
| Recon / blast-radius | **Yes — one per bug cluster** | `Explore` (read-only) | none (read-only) |
| Shared-base fix | No — single owner | self | — |
| App-specific fixes | **Yes — one per app** | `general-purpose` | disjoint dirs (no worktree needed for separate repos) |
| Validation | Yes — per app | `evaluator` / self | — |

Always `run_in_background: true` for the fan-outs; synthesize when they report. Tell each agent
the exact paths it owns and which files are off-limits (already edited), so parallel agents
never collide.

## Guardrails
- **Triage before fixing.** A list fixed top-to-bottom re-solves the same root five times and
  misses the sixth.
- **Don't blanket-fix without confirming the same root** — two bugs that look alike can have
  different causes; verify the invariant matches before batch-applying (canary guardrail).
- **Don't scope-creep.** Close the classes the list points to; don't fold in unrelated
  refactors (use `slop-audit` separately for that).
- **Respect constraints literally.** "Don't change X" means re-validate X to prove it didn't.
- **Watch the orchestrator's context budget.** The whole point of the parallel fan-outs is to
  keep recon and per-app edits OUT of the orchestrator's context. If you find yourself
  hand-editing every app inline, you're doing it wrong — delegate and integrate.
