# Port Manifest — what travels, what's adapted, what stays home

The home harness (`~/.claude` on the personal Mac) is split into a **portable best-practices core**
and **machine-specific bindings**. This kit carries the core, genericized; the bindings are
re-supplied on the target machine by the bootstrap interview → `harness.config.json`.

## Skills

### Ported verbatim (universal; only KW/wiki references scrubbed)
| Skill | Why it's universal |
|-------|--------------------|
| `swarm` | Parallel multi-agent build orchestration (worktrees, disjoint ownership, waves, validation gate) |
| `swarm-worker` (agent) | The worker contract the swarm drives |
| `canary-in-the-coalmine` | Treat each bug as a possible systemic canary; fix at the right altitude |
| `slop-audit` | Hunt + remove AI slop (excess docs, dead/misaligned code, vibe remnants) |
| `auth-resilience` | Defer-and-continue on auth/connectivity roadblocks; never stall overnight work |
| `diagnose` | Disciplined reproduce → minimise → hypothesise → fix loop |
| `grill-me` | Relentless plan stress-testing before committing |
| `laundry-list` | Orchestrate a multi-bug bug-bash with canary discipline |
| `think` | Research, structured reasoning, context budgeting |
| `plan` | Project planning (PRD, issues) — KW curriculum specialty dropped |
| `meta` | Author/audit skills + session handoff — project-skill genericized |

### Ported as genericized adapters (workflow kept; KW infra → config)
| Skill | Adapted how |
|-------|-------------|
| `token-rotation` | Registry path + sync-target types from `harness.config.json`; Coolify/GH-Secrets → generic targets |
| `deploy` (← kw--deploy) | Reads `deploy.{deploy_target,secrets_store,domain_provider}`; Hostinger/Coolify/VPS removed |
| `app-lifecycle` (← kw--app-lifecycle) | Generic scaffold→ship; project root + naming + host from config |
| `auth` (← kw--auth) | Framework-agnostic gate invariants; env-var names from the project |
| `build` | Engineering/TDD/stack patterns kept; KW theme + xAI specialty dropped; URLs/platform genericized |
| `design` | UX/IA + Figma kept; Kenilworth + folk-modernist specialties dropped (re-establish a work design system) |

### Dropped (stay home — irreducibly personal/KW)
| Dropped | Reason |
|---------|--------|
| `kw--ios-patterns`, `kw--ios-forms`, `kw--infra`, `kw--ops-agent` | Bound to the Kenilworth fleet / iOS web-app house style |
| `apple-hig` | iOS/iPadOS-specific; port later if the work does iOS |
| `knowledge` | Wittkepedia wiki at `~/Wittkepedia` — a personal second brain |
| `x-scout` (agent) | Personal X/Twitter growth tooling |
| design/`kenilworth.md`, `folk-modernist.md`; plan/`kenilworth-curriculum.md`; build/`ai-xai.md` | KW design system / personal aesthetic / xAI-specific |

## Agents
Ported: `evaluator`, `swarm-worker`, `deploy-verifier` (URL config-driven), `librarian`.

## Hooks (all config-driven via `harness.config.json`, fail-open/closed as appropriate)
`guard.py` (protected_globs + universal .env/rm/force-push baseline) · `commit-gate.sh`
(multi-stack auto-detect + override) · `lint-fix.sh` (multi-formatter) · `auth-failure.sh`
(defer-and-continue) · `session-context.sh` (deferred tasks + tokens + project CLAUDE.md) ·
`stop-checklist.sh` · `deferq.py` · `tokens.py` (metadata-only registry) · `harness_config.py`
(loader) · `lib.sh` (portable `TO()` timeout shim — the macOS-no-`timeout` fix).

## CLAUDE.md
Only the **universal discipline** travels (phases, context mgmt, complex-reasoning, code quality,
task discipline, secrets doctrine) — appended between sentinel markers, idempotently. Stack
defaults, paths, and the skill table are regenerated from the interview, not copied.

## Security invariants preserved
- The token registry holds **metadata only** — never values (verified: the home machine's real
  Coolify bearer token that was sitting in `meta/project-skill.md` was **excluded**, not ported).
- No secret values, IPs, or SSH identities appear anywhere in this kit.
