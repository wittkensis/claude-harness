# Manifest — blueprint-ew-v20260614

Provenance registry for everything seeded by this blueprint. Three tables: what's included, what's adapted, what's excluded.

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

---

## Excluded Content

| Excluded | Category | Reason |
|----------|----------|--------|
| `fleet--*` (10 skills) | Fleet-specific | Bound to *.ericwittke.com infrastructure (Coolify, Hostinger, kw-system.css) |
| `consult--wittkepedia` | Personal | Queries Eric's personal wiki at ~/Wittkepedia |
| `write--brand` | Personal | Eric's X/social voice and brand |
| `write--career` | Personal | Resume and cover letter authoring |
| `teach` | Personal | Personal learning workspace |
| `audit--harness` | Personal | References Eric's specific ref-check.py, skill-lint.py, drift-check.py |
| `consult--claude-architect` | Personal | References Eric's harness architecture decisions and history |
| `audit--claude-design-principles` | Personal | Eric's 5 values + 13 principles |
| `audit--drift` | Personal | Goal-adherence audit against Eric's specific goals |
| `audit--tokens` | Fleet | Tracks Eric's Coolify + GitHub Secrets token rotation |
| `tokens.py` hook | Fleet | Monitors Eric's fleet API token rotation schedule |
| `harness-selfcheck.sh` hook | Personal | Calls Eric's specific linter scripts |
| `CLAUDE.md` goals section | Personal | Eric's long-term goals and named projects |
| `CLAUDE.md` prompt templates section | Personal | References Eric's ~/.claude/prompts/ registry |
| `consult--*` advisors | Conditionally portable | Bret Victor, Jony Ive, Ray Dalio, Elon Musk, Tufte advisors are portable but non-essential for bootstrap; add via upgrade if desired |

---

## What Stays Home

The following never travel in any blueprint version:
- Real API tokens or secrets (any value matching `\d+|[A-Za-z0-9]{30,}`)
- Personal wiki content (~/Wittkepedia)
- Fleet infrastructure config (Coolify URLs, Hostinger API keys)
- Project-specific CLAUDE.md files from ~/Apps-Workspace
- Session history (~/.claude/history.jsonl)
- Cached state (~/.claude/cache/, ~/.claude/state/)
