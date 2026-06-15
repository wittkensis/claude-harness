# Manifest — blueprint-ew-v20260614

Provenance registry for everything seeded by this blueprint.

---

## Seeded Skills (12)

| Skill | Family | Why portable | Source marker |
|-------|--------|-------------|---------------|
| `ops--session-start` | ops | Universal session orientation pattern; hooks-integrated | blueprint-ew-v20260614 |
| `ops--backlog` | ops | Queue discipline applies to any multi-project setup | blueprint-ew-v20260614 |
| `ops--handoff` | ops | Session continuity is a universal need | blueprint-ew-v20260614 |
| `ops--swarm` | ops | Parallel multi-agent build pattern; worktree-based | blueprint-ew-v20260614 |
| `ops--laundry-list` | ops | Batch work orchestration with per-item discipline routing | blueprint-ew-v20260614 |
| `ops--tool-resilience` | ops | Auth/timeout deferral; any tool can fail | blueprint-ew-v20260614 |
| `plan--grill-me` | plan | Design-before-build enforcement; pre-commit questioning | blueprint-ew-v20260614 |
| `build--diagnose` | build | Reproduce→minimise→fix loop applies to any stack | blueprint-ew-v20260614 |
| `build--versioning` | build | Semver + git SHA + CHANGELOG is stack-agnostic | blueprint-ew-v20260614 |
| `audit--canary` | audit | Systemic bug analysis applies to any codebase | blueprint-ew-v20260614 |
| `audit--slop` | audit | AI cruft removal applies to any AI-assisted codebase | blueprint-ew-v20260614 |
| `eval--tdd` | eval | Red-green-refactor is language-agnostic | blueprint-ew-v20260614 |

---

## Seeded Hooks (9)

| Hook | Event | What was genericized |
|------|-------|---------------------|
| `session-context.sh` | SessionStart | Removed KW fleet-app context block; generalized project-root resolution; backlog.py call is conditional on file existence; harness audit clock removed (personal) |
| `live-state.sh` | Stop | Removed `backlog.py` direct invocation; backlog block is conditional |
| `done-check.py` | Called by gates | Removed `drift-check.py` harness-specific linter call (personal tooling) |
| `commit-gate.sh` | PreToolUse(Bash) | Verbatim — already fully generic |
| `stop-checklist.sh` | Stop | Verbatim — already fully generic |
| `auth-failure.sh` | PostToolUseFailure | Verbatim — already fully generic |
| `deferq.py` | Called by auth-failure | Verbatim — already fully generic |
| `doc-reminder.py` | PreToolUse(Edit/Write) | Verbatim — already fully generic |
| `guard.py` | PreToolUse | Replaced hardcoded `~/Wittkepedia/raw/` path with `harness.config.protected_paths[]`; Coolify token pattern kept (universal API token leak protection) |

