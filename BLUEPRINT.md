# Claude Code Harness Blueprint
**Version:** v20260614
**Upstream:** https://github.com/wittkensis/claude-harness
**Source:** Eric Wittke <eric.wittke@gmail.com>
**Format:** v2 (Claude-native instruction document)

---

> **This document is addressed to you — the Claude Code instance doing the installing.**
> Read it top-to-bottom once during bootstrap. Return to Part 2 whenever you need to extend or upgrade the harness.

---

## What This Is

A harness is the system *around* the agent loop that makes Claude Code reliable, goal-directed, and capable of autonomous orchestration. The model is the easy part; the harness is where 98% of the value lives.

This blueprint gives your user:
- **Goal-centricity** — every session and task is anchored to declared goals
- **Phase discipline** — a five-phase task cycle (Clarify → Design → Build → Verify → Iterate) that prevents premature building and silent failures
- **Autonomous orchestration** — parallel multi-agent builds via `ops--swarm`; resilient to auth/connectivity failures
- **A work queue** — `ops--backlog`, the single cross-project source of truth for what's next
- **Session continuity** — handoff + live-state so no session opens from zero
- **Validation discipline** — done-gates, commit guards, and canary analysis

What this blueprint does *not* give your user: your installer's personal goals, projects, stacks, or opinions. You will derive those during the Understanding Phase and build a harness that fits this specific human.

---

# PART 1: BOOTSTRAP
*Execute top-to-bottom, once. Each step ends with a confirmation gate — do not proceed until the user acknowledges.*

---

## Step 1 — Pre-flight

Run these checks and report the findings to the user **before touching anything**:

```bash
# Claude Code version
claude --version 2>/dev/null || echo "version unknown"

# Existing ~/.claude structure
ls ~/.claude/ 2>/dev/null || echo "~/.claude does not exist"

# Is ~/.claude already a git repo?
git -C ~/.claude rev-parse --git-dir 2>/dev/null && echo "git: YES" || echo "git: NO"

# Existing skills count
ls ~/.claude/skills/ 2>/dev/null | wc -l || echo "0"

# Existing hooks count  
ls ~/.claude/hooks/ 2>/dev/null | wc -l || echo "0"

# Existing CLAUDE.md?
[ -f ~/.claude/CLAUDE.md ] && echo "CLAUDE.md: EXISTS" || echo "CLAUDE.md: NONE"
```

Present the summary to the user in plain language:
> "Here's what I found on this machine: [findings]. I'm going to install a Claude Code harness that will add [N] skills, [N] hooks, extend your CLAUDE.md, and initialize a git repo in `~/.claude`. Nothing will be overwritten without showing you a diff first. Ready to continue?"

**Gate: Wait for user acknowledgment before proceeding.**

---

## Step 2 — Understanding Phase

This phase has three parts. Complete all three before writing any files.

### 2a. Read existing setup

Read these files if they exist — do not skip even if they look minimal:

1. `~/.claude/CLAUDE.md` — their existing rules and goals
2. Any `CLAUDE.md` files in their active project directories (ask: "What projects are you actively working on?")
3. `README.md` or `CLAUDE.md` in each active project root
4. `~/.claude/SKILLS.md` — their existing skill routing table (if any)
5. `.claude/CLAUDE.md` inside each active project (project-local overrides)

As you read, note:
- What goals or values does this person already have written down?
- What stacks and frameworks appear in their projects?
- What workflow patterns do they already follow (or resist)?
- What does their existing CLAUDE.md already cover that the harness discipline block would duplicate?

### 2b. Skills inventory

List all skills currently in `~/.claude/skills/`. Cross-reference against the 12 seed skills in this blueprint's `seed/skills/` directory.

Then do two things:

**Surface most-used skills:** Count how often each skill name appears in their existing `CLAUDE.md`, `SKILLS.md`, and any project CLAUDE.md files. Present the top 5 by reference frequency — these are high-signal, keep them prominent in the new routing table.

**Surface unused candidates:** Find skills installed but not referenced anywhere in their `~/.claude/` or active project dirs. Present the list:
> "I found these N skills with no references in your routing table or CLAUDE.md files: [list]. Would you like to review them for cleanup before we install? Removing unused skills reduces context noise every session."

**Surface overlaps:** For each seed skill that matches an existing skill by name or purpose, show the overlap:
> "You already have [existing-skill] which overlaps with the seed [seed-skill]. Here's how I'd reconcile them: [recommendation — keep yours / merge / replace]. Proceed with this recommendation?"

### 2c. Config interview

Ask these questions to generate `harness.config.json`. Do not write the file until you have all answers:

```
1. Your name (for commit authorship and session context):
2. Your email:
3. Your top 1–3 long-term goals (e.g., "ship a profitable SaaS", "publish a novel"):
4. Active projects — for each: name, path on disk, primary stack/language:
5. Where do you deploy? (e.g., Vercel, Fly.io, self-hosted VPS, nowhere yet):
6. Where do you store secrets? (e.g., .env.local only, Doppler, AWS Secrets Manager):
7. Preferred git remote provider (GitHub / GitLab / Bitbucket / none):
8. Do you want the harness skills to auto-load system-wide, or only per-project?
   [system-wide is the default and recommended — your ~/.claude/skills/ applies everywhere]
```

Show the user the generated `harness.config.json` before writing it:
> "Here's the config I'll write to `~/.claude/harness.config.json`: [JSON]. Looks right?"

**Gate: Wait for user confirmation of the config before proceeding.**

---

## Step 3 — Install Phase

Narrate every action before executing it. Use this exact pattern:
> "Next I'll [description of action]. This will [what changes]. Proceed?"

Install in this order:

### 3a. Initialize git in ~/.claude

```bash
# Only if not already a git repo
git -C ~/.claude rev-parse --git-dir 2>/dev/null || git init ~/.claude
```

Tell the user: "I'll initialize git in `~/.claude` so the harness has a local history. You can see what changed and when with `git log ~/.claude`. This stays local — nothing is pushed without your say-so."

### 3b. Write harness.config.json

Write the confirmed config from Step 2c to `~/.claude/harness.config.json`.

### 3c. Install seed skills

Copy the 12 skills from `seed/skills/` into `~/.claude/skills/`.

**Merge rule:** For each skill, check if a file already exists at that path.
- If no conflict: copy directly.
- If conflict: show a diff and ask: "This skill already exists. Replace / merge / skip?"

Each copied skill already has `metadata.source: blueprint-ew-v20260614` in its frontmatter — do not remove this line. It's the provenance marker.

Tell the user:
> "I'll add these 12 skills to `~/.claude/skills/`. Each one serves a specific harness process — I'll explain what each does as I install it: [list each with one-line description]. Proceed?"

The 12 skills and what they give your user:

| Skill | What it unlocks |
|-------|----------------|
| `ops--session-start` | Session orientation — resume from prior handoff, surface goals and backlog |
| `ops--backlog` | Cross-project work queue — the single source of truth for "what's next" |
| `ops--handoff` | Session compaction — leave a resume point so the next session opens oriented |
| `ops--swarm` | Parallel multi-agent builds — decompose → fan out concurrent workers → integrate |
| `ops--laundry-list` | Batch work orchestration — triage a list, apply the right discipline per item |
| `ops--tool-resilience` | Auth/connectivity failure handling — park, continue unblocked work, auto-resume |
| `plan--grill-me` | Plan stress-testing — relentless questioning before committing to a direction |
| `build--diagnose` | Disciplined debug loop — reproduce → minimise → hypothesise → fix |
| `build--versioning` | Semantic versioning, git SHA build IDs, CHANGELOG discipline |
| `audit--canary` | Systemic bug analysis — treat each bug as a possible symptom of a broader pattern |
| `audit--slop` | AI cruft removal — hunt dead code, placeholder data, vague comments |
| `eval--tdd` | Test-first discipline — red → green → refactor loop |

### 3d. Install hooks

Copy the 9 hooks from `seed/hooks/` into `~/.claude/hooks/`.

**Merge rule:** Same as skills — show diff, ask before overwriting.

Tell the user what each hook does before installing:
> "I'll install 9 hooks into `~/.claude/hooks/`. Hooks run automatically on specific events — here's what each one does: [explain each]. Proceed?"

The hooks and what they enforce:

| Hook | Event | What it does |
|------|-------|-------------|
| `session-context.sh` | SessionStart | Surfaces prior handoff, deferred tasks, backlog, current phase — orients every session |
| `live-state.sh` | Stop (every turn) | Writes a mechanical snapshot so sessions never open from zero |
| `commit-gate.sh` | Pre-commit | Blocks `git commit` if typecheck/tests fail; bypass with `[wip]` in message |
| `stop-checklist.sh` | Session end | Asserts the done-gate before stopping; prevents leaving broken work |
| `done-check.py` | Called by both gates | Language-aware checker: JS (tsc + npm test), Python (ruff + pytest), harness (ref-check) |
| `auth-failure.sh` | Tool failure | Defers auth/timeout failures to a queue; continues unblocked work |
| `deferq.py` | Called by auth-failure | Manages the deferred-work queue |
| `doc-reminder.py` | Pre-edit (doc files) | Auto-surfaces the documentation skill when editing CLAUDE.md, README, CHANGELOG |
| `guard.py` | Pre-tool (write/bash) | Blocks writes to real .env files, broad `rm -rf`, force-push to main |

Wire the hooks in `~/.claude/settings.json`. Show the user the diff to settings.json before applying.

### 3e. Extend CLAUDE.md

Read `seed/claude-discipline.md` from this blueprint. It contains the harness discipline block, wrapped in sentinel markers:

```
# [harness:ew] v20260614 BEGIN — managed by ops--blueprint-version; do not edit manually
...discipline content...
# [harness:ew] END
```

**Merge rule:**
- If `~/.claude/CLAUDE.md` already has `[harness:ew]` sentinels: replace the block between them with the new version.
- If not: append the discipline block to the end of their existing CLAUDE.md. Never insert before their existing content.
- If they have no CLAUDE.md: create one with just the discipline block, then invite them to add their goals above the sentinel.

Tell the user:
> "I'll extend your CLAUDE.md with the harness discipline block (approach principles, task cycle, naming conventions, agents table). Your existing content is completely untouched — the new content is appended after it and wrapped in sentinel markers so future upgrades can find and replace it cleanly. Proceed?"

### 3f. Generate SKILLS.md

Create `~/.claude/SKILLS.md` with:
1. The Phase→Skill routing table (seeded with the 12 installed skills)
2. A trigger→skill table for each installed skill
3. A note pointing to `build--skill-authoring` for extending it

If a SKILLS.md already exists, show a diff and ask: "Replace / merge / keep yours?"

### 3g. Write harness manifest

Write `~/.claude/HARNESS/manifest.json`:
```json
{
  "blueprint": "blueprint-ew-v20260614",
  "upstream": "https://github.com/wittkensis/claude-harness",
  "installed": "{{ISO_DATE}}",
  "skills_seeded": [list of installed skill names],
  "hooks_seeded": [list of installed hook names]
}
```

### 3h. First git commit

```bash
git -C ~/.claude add -A
git -C ~/.claude commit -m "harness: bootstrap from blueprint-ew-v20260614"
```

---

## Step 4 — Verification

Run each check and report pass/fail to the user.

**Check 1 — Skills discoverable**
Ask yourself: list the 5 task cycle phases and name one installed skill for each. If you can't, the routing table needs work.

**Check 2 — Hooks wired**
```bash
cat ~/.claude/settings.json | python3 -c "import json,sys; s=json.load(sys.stdin); print(list(s.get('hooks',{}).keys()))"
```
Should show at least: `SessionStart`, `Stop`, `PreToolUse`, `PostToolUseFailure`.

**Check 3 — Config readable**
```bash
python3 -c "import json; c=open('$HOME/.claude/harness.config.json').read(); json.loads(c); print('OK')"
```

**Check 4 — Git initialized**
```bash
git -C ~/.claude log --oneline -1
```
Should show the bootstrap commit.

**Check 5 — CLAUDE.md sentinels**
```bash
grep -c '\[harness:ew\]' ~/.claude/CLAUDE.md
```
Should return `2` (BEGIN and END).

Present a summary:
> "Bootstrap complete. ✓ N skills installed ✓ N hooks wired ✓ CLAUDE.md extended ✓ git initialized at [short hash]. Your harness is live. Start your next session normally — `ops--session-start` will orient you."

---

# PART 2: REFERENCE
*Return here when extending, upgrading, or troubleshooting the harness.*

---

## 2.1 — The Harness Model

Three ideas underpin everything:

**Goal-centricity.** Every session, task, and skill invocation should trace back to a declared goal. Goals live in your CLAUDE.md (you'll add them above the sentinel block). When work can't be traced to a goal, question whether it should be done at all.

**Phase discipline.** The five-phase task cycle prevents the most common failure modes:
- *Clarify* before designing — don't assume you understand the problem
- *Design* before building — have something to show for the direction before writing code
- *Verify* against the design intent, not just compilation — don't claim success prematurely
- *Iterate* with findings fed back — no silent failures

**Autonomous orchestration.** The harness enables Claude to handle complex, multi-step work without constant supervision: `ops--swarm` fans work out to parallel agents in isolated git worktrees, `ops--tool-resilience` handles auth failures without blocking, and the session loop (start → work → handoff) keeps continuity across sessions.

**The queue:** `ops--backlog` (`~/.claude/state/backlog.py`) is the single source of truth for what's next across all your projects. Every task, idea, bug, and follow-up that surfaces but isn't being done now goes there. Never let work evaporate into the transcript.

**The session loop:**
```
ops--session-start → [oriented, goals surfaced, backlog top shown]
  → work (Clarify → Design → Build → Verify → Iterate)
  → ops--handoff → [resume point written for next session]
```

**The meta loop (monthly):**
```
audit--harness → [snapshot of skill usage, drift, uncodified learnings]
  → ranked proposals for harness improvements
  → implement highest-signal improvements
  → advance harness-audit-due by ~1 month
```

---

## 2.2 — Namespace Reference

**Skill naming:** `family--name` (double-dash separator). The family prefix is the namespace.

Standard families from this blueprint:
| Family | Domain |
|--------|--------|
| `ops--` | Orchestration, session, queue, resilience |
| `build--` | Engineering, debugging, stack patterns |
| `audit--` | Quality, analysis, self-improvement |
| `plan--` | Design, clarification, PRD |
| `eval--` | Testing, validation |
| `think--` | Reasoning, research, first principles |
| `design--` | UX, IA, visual design |

Create your own families for domain-specific clusters (e.g., `myapp--` for app-specific skills, `myfleet--` for a set of related apps).

**Provenance marker:** Skills seeded from this blueprint have `metadata.source: blueprint-ew-v20260614` in their YAML frontmatter. This is how you know what came from upstream vs. what you built yourself.

**CLAUDE.md sentinels:**
```
# [harness:ew] v20260614 BEGIN — managed by ops--blueprint-version; do not edit manually
# [harness:ew] END
```
Never edit the content between these manually. Use `ops--blueprint-version` to upgrade.

**Config source of truth:** `~/.claude/harness.config.json` — hooks and skills read from here. Edit it directly when your setup changes (new project, new deploy target, etc.).

---

## 2.3 — Extending the Harness

**Adding a skill:**
1. Create `~/.claude/skills/family--name/skill.md`
2. Write YAML frontmatter: `name`, `description` (this drives routing — be specific about triggers and exclusions), `metadata.status: active`, `metadata.modified: YYYY-MM-DD`
3. Add a trigger→skill row to `~/.claude/SKILLS.md`
4. Commit: `git -C ~/.claude commit -am "skill: add family--name"`

**Adding a hook:**
1. Create the hook file in `~/.claude/hooks/`
2. Make it executable: `chmod +x ~/.claude/hooks/your-hook.sh`
3. Wire it in `~/.claude/settings.json` under the appropriate event key
4. Hooks are the cheapest extension mechanism — prefer a hook over a skill for guaranteed-activation behavior

**Adding a project to the backlog:**
```bash
python3 ~/.claude/state/backlog.py add --type feat --project "your-project" "description of work"
```

**Creating a fleet namespace:** If you have multiple related apps/services, create a `myfleet--` skill family. Use `metadata.tier: fleet` in frontmatter to fence those skills to fleet context only (they won't fire on unrelated work).

---

## 2.4 — Upgrading

When you want to check for a newer blueprint version:

```bash
# Fetch the latest BLUEPRINT.md from upstream
curl -s https://raw.githubusercontent.com/ericwittke/claude-harness/main/BLUEPRINT.md | head -5
```

The version header tells you if a newer version exists. Compare against your installed version in `~/.claude/HARNESS/manifest.json`.

To apply an upgrade, use the `ops--blueprint-version` skill installed on the upstream machine. Or manually:
1. Download the new `seed/` directory
2. For each changed file, diff against your installed version
3. Selectively apply changes that make sense for your setup
4. Update `metadata.source` values to the new version stamp
5. Commit: `git -C ~/.claude commit -am "harness: upgrade to blueprint-ew-vYYYYMMDD"`

Upgrade philosophy: **selective, intentional.** Not every change to the upstream harness belongs in your harness. The diff is a menu, not a mandate.

---

## 2.5 — Evolving Your Own Harness

The harness should improve over time, driven by what you actually learn in sessions.

**Codify learnings as skills:** When you solve a problem in a non-obvious way that you'd want to repeat, write a skill. When you notice you keep loading the same context before a type of task, write a skill for that task type.

**Retire unused skills:** Skills inject their description into the context every session. Unused skills are pure noise. Run a usage check monthly:
```bash
# Find skills not referenced in your routing table or any CLAUDE.md
for d in ~/.claude/skills/*/; do
  name=$(basename "$d")
  grep -r "$name" ~/.claude/SKILLS.md ~/.claude/CLAUDE.md 2>/dev/null | grep -q . || echo "UNUSED: $name"
done
```

**The monthly meta-loop:**
1. Run `audit--harness` (or equivalent review) — look at what skills you actually used, what hooks fired, what learnings accumulated
2. Identify the 2–3 highest-signal improvements
3. Implement them (new skill, updated hook, refined routing)
4. Advance `~/.claude/state/harness-audit-due` by ~1 month

**Keep SKILLS.md as the routing source of truth.** The description field in each skill's frontmatter determines when Claude loads it — but SKILLS.md is where you see the full picture and tune it. If routing feels off, that's the first place to look.

---

## Appendix: Seed Kit Inventory

### Skills seeded (12)
See `seed/skills/` — each is a complete skill directory with `skill.md`.

### Hooks seeded (9)
See `seed/hooks/` — each is a standalone script, genericized for any setup.

### Config template
See `seed/harness.config.template.json` — fill in during Step 2c.

### CLAUDE.md discipline block
See `seed/claude-discipline.md` — the exact content inserted between sentinels.

### Provenance
All seeded content carries `metadata.source: blueprint-ew-v20260614`. This is the lineage marker — it tells you and your Claude what came from this blueprint vs. what you built yourself. Do not remove it from seeded files; update it when you apply an upgrade.
