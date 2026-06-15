---
name: ops--backlog
description: THE canonical cross-project backlog — the single source of truth for "what is the next thing to do?" across every project Claude Code touches. Use to capture a task/idea/bug, triage and rank it, ask what's next, claim work in a swarm, or import/reconcile GitHub issues. Backed by a SQLite DB queried via backlog.py so it never inflates context. ALWAYS offer to capture a future task that surfaces but isn't being done now. Downstream: log--issues / plan--prd build a promoted item.
metadata:
  status: active
  kind: playbook
  modified: 2026-06-11
  source: blueprint-ew-v20260614
---

# ops--backlog — The Backlog

## Invocation
Triggers: backlog, what's next, what should I work on, add to the backlog, log this, capture this, triage, queue, icebox

The one durable queue for everything. Lives in SQLite at `~/.claude/state/backlog.db`, driven by
**`~/.claude/state/backlog.py`**. The DB is the source of truth; a GitHub issue is an *optional pointer*
(`github_url`) for items that need execution-level tracking — never a competing truth.

## The model
- **project** (where) — enforced enum in the `projects` table, each with a `category` (app · system · hobby · learning), a live `local_path`, and an optional `repo_url`. Growable: `backlog.py project add`.
- **type** (what kind) — `feature · improvement · bug · chore · research · design · docs · experiment`.
- **score = Impact (1–5) ÷ Effort** — Effort from t-shirt size `XS1·S2·M3·L5·XL8`. Higher score = do sooner. No priority lane, no confidence, no reach — urgency just shows up as high Impact.
- **status** — `inbox → todo → doing → blocked → done → dropped`. `inbox` = captured, not yet triaged (zero-friction dump). `todo` = ranked & ready. `doing` = atomically claimed by an agent.

## Capture doctrine
1. **Proactively offer.** Whenever a future task, idea, bug, or follow-up surfaces in conversation but isn't being done now, offer: *"Want me to drop that in the backlog?"* Don't let work evaporate.
2. **Vague → structured.** Take loose input, infer the `type`, and write the right format (below). **Make safe assumptions and state them**; ask only when a load-bearing detail is genuinely missing.
3. **Capture fast, triage later.** A one-liner to `inbox` beats a perfect entry never written. Assign Impact/size at triage.
4. **One item per idea.** Don't bundle "add search + fix layout + perf" — bundles resist ranking.

## Body formats by type (JTBD spine — no persona theater)
- **feature / improvement** → Job Story: *"When \<situation>, I want \<motivation>, so I can \<outcome>."* + acceptance criteria.
- **bug** → *What / Expected / Actual / Repro / Severity.*
- **research** → the open question + why it matters.
- **experiment** → Hypothesis: *"We believe \<change> causes \<outcome>; true when \<signal>."*
- **chore / docs** → outcome statement: *\<what> so that \<why>.*

## CLI quick reference (`python3 ~/.claude/state/backlog.py …`)
```
add <project> "<title>" [--type T --impact 1-5 --size xs|s|m|l|xl --body "…" --github URL]
triage <id> --impact N --size SZ [--type T]      # inbox → todo, computes score
top [--project P | --category C | --all] [--n 5]  # ranked open; THE renderer (cwd-aware)
list [--project P --status S --type T --limit N]
show <id>                                          # full body
claim [<id> | --project P] [--owner ID]           # atomic: todo → doing, swarm-safe
start|done|drop <id>   ·   block <id> [--note "…"]
set <id> [--impact N --size SZ --type T --github URL]
project add|set|list|verify                        # keeps local_path / repo_url live
sync [--project P] [--apply]                       # import open GH issues; reconcile closed ones
export [--out PATH]                                # human-readable BACKLOG.md snapshot
```

## Querying without inflating context
Never `cat` the DB or dump the whole backlog. Use the CLI — filtered/sorted queries return only the rows
asked for (`top --project X --n 5` = 5 lines). The session-start hook already surfaces the top items for the
current project every session, in the one canonical format.

## Swarm coordination
Parallel agents coordinate **through the DB**: `backlog.py claim` takes the write lock (`BEGIN IMMEDIATE`)
and atomically moves the top `todo` → `doing` stamped with an owner, so no two agents grab the same item.
WAL + a 5s busy-timeout mean reads never block and writers wait rather than error.

## Promote an item → GitHub issue (optional)
When an item graduates to real execution on a repo-backed project, open an issue and link it:
```bash
gh issue create --repo wittkensis/<repo> --title "<title>" --body "<the item body>" --label "<type>"
python3 ~/.claude/state/backlog.py set <id> --github <issue-url>
```
The DB row stays the source of truth; `backlog.py sync` later flags the item if its issue is closed.

## Reconciliation (this is the new source of truth)
- **Replaces the retired per-project icebox** — capture + triage + ranking now live here, DB-first across all projects (the old per-project `ICEBOX.md` / per-repo fragmentation is exactly what this replaces).
- **Downstream, unchanged:** a *ready* item hands off to `log--issues` (break into vertical-slice issues), `plan--prd` (spec a large one), `fleet--app-lifecycle` (fleet feature), `build--diagnose`/`audit--canary` (bugs).

## Related
- `log--issues` — follows: break a promoted backlog item into vertical-slice GitHub issues
- `plan--prd` — follows: spec a large backlog item before building
- `ops--session-start` — companion: surfaces the top backlog items every session
- `ops--laundry-list` — companion: a batch of promoted items becomes a laundry-list run
- `plan--grill-me` — companion: stress-test a big item before promoting it
