# Changelog

## v20260614 (current)

### Install tooling + harness model (post-publish hardening)
The v2 blueprint is still the adaptive install path, but its narrated steps are
now backed by executable, testable tools in `seed/install/` so the install is
verifiable instead of vibes:
- `secret_scan.py` — gates the first commit against `.env`/keys/live API tokens (#97)
- `ref_lint.py` — fails on dangling skill refs; intentional forward-pointers are
  declared in each skill's `metadata.refs-external` (#101)
- `merge.py` — install-mode detection (fresh/migration/merge) + superset-aware
  file merge (keep-local when local ⊇ seed) + sentinel-preserving CLAUDE.md merge,
  honoring a pre-existing `# BEGIN/END HARNESS` scheme (#99, #100, #104)
- `token_replace.py` — resolves `{{harness.config.*}}` before files land (#103)
- `verify.py` — the Step-4 gate: backlog callable, no placeholders, no dangling
  refs, `.gitignore` present, sentinels, valid config (#102)
- `harness.py` + `MODEL.md` — formal component model, semver, content-addressed
  lockfile, portable `export`, and zero-step `bootstrap` from an artifact (#70)
Also seeds working `state/backlog.py` + `state/learning-log.py` (#98) and a
`seed/gitignore.template`; fixed `ericwittke`→`wittkensis` GitHub URLs (#105).

### Format: v1 → v2
Complete reformat. v1 was a Python-installer kit (install.py, port-test.py, INTERVIEW.md + kit/). v2 is a Claude-native instruction document — the blueprint is addressed directly to the adopter's Claude and is self-sufficient without any installer script.

### Key changes from v20260601

**New: Understanding Phase**
The bootstrap now opens with a structured review of the adopter's existing setup: active projects, READMEs, existing CLAUDE.md, and installed skills. The installer Claude surfaces most-used skills, flags unused candidates for cleanup, and reconciles overlaps with seed skills before writing a single file. This adapts the harness to the adopter rather than overwriting their setup.

**New: Transparency-first principle**
Every install action is narrated before it happens. The adopter sees what will change, reviews it, and confirms before anything is written. This builds trust in the installation process.

**New: harness.config.json**
A structured config file captures the adopter's name, goals, projects, stacks, and deploy targets. Hooks read from this file instead of hardcoded paths, making the entire seed portable without personal references.

**New: Provenance via frontmatter metadata**
All seeded skills carry `metadata.source: blueprint-ew-v20260614`. This marks what came from the blueprint vs. what the adopter built, without cluttering skill names or the routing table.

**New: CLAUDE.md sentinel markers**
The discipline block is wrapped in `# [harness:ew] BEGIN/END` sentinels, making upgrades non-destructive and the adopter's content completely untouched.

**Changed: Hook genericization**
Hooks previously contained hardcoded personal paths (Wittkepedia, drift-check.py). All hooks now read from `harness.config.json` or use auto-detection. The `guard.py` protected paths are config-driven.

**Changed: Skill selection**
v1 ported ~30 skills. v2 seeds exactly 12 — the discipline + universal build primitive set. Rationale: the harder-to-derive skills are the discipline ones (swarm, canary, session loop). Stack-specific skills (React, iOS, Tauri) are easy for the adopter's Claude to author using `build--skill-authoring` as a model, and they should — their stack, not ours.

**Changed: Distribution model**
v1: copy the kit folder, run install.py. v2: Claude reads BLUEPRINT.md and self-installs. No Python installer, no intermediate scripts. The blueprint IS the installer.

**Upstream: github.com/wittkensis/claude-harness**
First version published to a public GitHub repo. Future versions will be tagged releases. Adopters can `curl` the latest BLUEPRINT.md to check for upgrades.

---

## v20260601

Initial blueprint. Python-installer format. See `HARNESS/BLUEPRINTS/v20260601/` for the full kit.
