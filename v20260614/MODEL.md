# Harness Model, Versioning & Distribution

The formal model that makes a harness **reproducible, diffable, and transferable**
(issue #70). Tooling: `seed/install/harness.py`.

---

## 1. What a harness *is* (the model)

A harness is the set of components under `~/.claude` that make Claude Code
reliable. The model enumerates exactly seven component kinds plus four
singleton files — nothing else is part of the harness:

| Kind | Path | Recurse | What it is |
|------|------|:------:|------------|
| `skills` | `skills/` | yes | `family--name/SKILL.md` routing-and-playbook units |
| `agents` | `agents/` | yes | sub-agent definitions |
| `hooks` | `hooks/` | yes | event scripts (SessionStart, Stop, PreToolUse, …) |
| `state` | `state/` | yes | operational tools (`backlog.py`, `learning-log.py`) — **DBs excluded** |
| `memory` | `memory/` | yes | durable cross-session memory notes |
| `prompts` | `prompts/` | yes | reusable prompt templates |
| singletons | top-level | — | `CLAUDE.md`, `SKILLS.md`, `harness.config.json`, `.gitignore` |

**Excluded from the model** (machine-local, secret, or regenerable):
`*.db`/`*.db-wal`/`*.db-shm` (SQLite state), `__pycache__/`, `*.pyc`, `*.log`,
`.git/`, `.DS_Store`. These are never locked, never exported.

---

## 2. The lockfile (`harness.lock.json`)

The manifest is a content-addressed inventory: every component file with its
`sha256` and byte size. It is the diffable, verifiable description of a harness
at a point in time.

```bash
python3 seed/install/harness.py model            # inventory (no write)
python3 seed/install/harness.py lock             # write harness.lock.json
```

Schema:

```json
{
  "schema": 1,
  "harness_version": "1.1.0",
  "blueprint": "blueprint-ew-v20260614",
  "generated": "2026-06-14T…Z",
  "components": { "skills": [ {"path","sha256","bytes"}, … ], "hooks": […], … },
  "counts": { "skills": 12, "hooks": 9, … }
}
```

Two harnesses are identical iff their lock `components` hashes match. Diff two
locks to see exactly what changed between versions or machines.

---

## 3. Versioning

The harness carries its **own** semver (distinct from the blueprint stamp
`blueprint-ew-vYYYYMMDD`, which records *where the seed came from*). Stored in
`harness.config.json` → `harness.semver`.

```bash
python3 seed/install/harness.py version              # show (default 1.0.0)
python3 seed/install/harness.py version --bump patch # bug fix to a hook/skill
python3 seed/install/harness.py version --bump minor # new skill/hook added
python3 seed/install/harness.py version --bump major # breaking model/contract change
```

Bump policy: **major** = a component contract changes (hook event, config key,
skill interface); **minor** = additive (new skill, new command); **patch** =
fixes inside existing components.

---

## 4. Export → portable artifact

`export` bundles exactly the modeled components (with an embedded lock) into a
single `harness-<version>.tar.gz`. Secrets and DBs are excluded by the model, so
the artifact is safe to move between machines.

```bash
python3 seed/install/harness.py export --out harness-1.1.0.tar.gz
# prints the artifact sha256 for out-of-band integrity checking
```

---

## 5. Install / bootstrap on a new machine (zero manual steps)

`bootstrap` verifies the artifact against its embedded lock (sha256 of every
file), refuses a tampered/incomplete bundle, guards against path-escape, then
extracts to the target root and makes the Python tools executable.

```bash
python3 harness.py bootstrap --artifact harness-1.1.0.tar.gz --root ~/.claude
# then (printed by bootstrap):
git -C ~/.claude init
python3 ~/.claude/HARNESS/install/verify.py --claude-dir ~/.claude
```

`verify` can also be run standalone against any artifact before trusting it:

```bash
python3 harness.py verify --artifact harness-1.1.0.tar.gz
```

---

## 6. Two distribution paths

- **Blueprint (BLUEPRINT.md)** — the *adaptive* path: a Claude instance reads
  the blueprint and tailors the install to a new user (Understanding Phase,
  config interview, merge with their existing setup). Use when standing up a
  harness *for a person*.
- **Artifact (`harness.py export`/`bootstrap`)** — the *reproducible* path:
  bit-for-bit transfer of an existing harness to a new machine for the same
  user. Use when *replicating your own* harness, or pinning a known-good
  version. The lock makes it diffable and tamper-evident.

Both produce a harness that passes `verify.py` (Step 4 checks).
