---
name: project-skill
description: Scaffold a new project-local skill (`{proj}--{purpose}`), wire it into the project CLAUDE.md, and verify auto-loading. Use when a project needs its own deploy/domain/session/data skill that isn't a global skill.
---

# Project-local skill authoring

Creates project-local skills for a specific app. These live in the project's `.claude/skills/`
directory and are wired into the project CLAUDE.md for auto-loading. Service-specific values
(deploy IDs, URLs, env-var names) come from `~/.claude/harness.config.json` and the project's
own setup — never hardcode secret values into a skill.

## Step 1 — Identify skill type

| Type | When | Filename |
|------|------|----------|
| Deploy | Project ships somewhere | `{proj}--deploy.md` |
| Domain logic | Complex feature rules | `{proj}--{domain}.md` |
| Session | Long-running workflows | `{proj}--session.md` |
| Data | Complex schema or migration patterns | `{proj}--data.md` |

## Step 2 — Create the skill file

Path: `{project-root}/.claude/skills/{proj}--{purpose}/SKILL.md`

### Deploy skill template (fill from harness.config.json + project setup)

```markdown
---
name: {proj}--deploy
description: {Proj} deploy — target, env vars, and push-to-deploy flow. Triggers: deploy, redeploy, push, go live.
---

# {proj}--deploy

## Deploy Flow
git push origin main        # if your platform auto-deploys on push
# else: trigger via the deploy platform's API/CLI (see the `deploy` skill)

## Config (no secret VALUES here — names/locators only)
| Field | Value |
|-------|-------|
| Repo | `{org}/{repo}` |
| Branch | `main` |
| Deploy target | `{from harness.config.json deploy_target}` |
| URL | `{app}.{your-domain}` |

## Required Env Vars (set in the platform's secret store; tracked in token-rotation)
| Var | Purpose |
|-----|---------|
| `{VAR}` | {purpose} |

## Verification After Deploy
Use the `deploy-verifier` agent against the live URL.
```

### Domain skill template

```markdown
---
name: {proj}--{domain}
description: {Proj} {domain} — rules, patterns, and constraints for {feature area}.
---

# {proj}--{domain}

## Core Rules
{The non-obvious constraints that aren't obvious from the code}

## Patterns / Anti-patterns
{Recurring patterns; what to avoid and why}
```

## Step 3 — Wire into project CLAUDE.md

```markdown
## Load at session start
Open `.claude/skills/{proj}--deploy/SKILL.md` immediately at every session start.

## Skills
| Trigger | Skill | Purpose |
|---------|-------|---------|
| deploy, push, go live | `{proj}--deploy` | Deploy automation |
| {domain keywords} | `{proj}--{domain}` | {Domain purpose} |
```

**Why "Load at session start":** naming the skill in CLAUDE.md with explicit "open immediately"
language ensures Claude loads it without being asked. Project skills aren't in the global
trigger table, so they need explicit instructions.

## Step 4 — Verify auto-loading

Start a new session in the project and confirm the deploy skill is read within the first
exchange, and that the deploy locators (target ID, env-var names) are accessible without asking.

## Secrets — never in skills
Deploy IDs and env-var **names** belong in the skill; the **values** never do. Values live in
the platform secret store / `.env.local` and are tracked by the `token-rotation` skill. If you
find a secret value pasted into any skill, treat it as an incident: rotate it and scrub it.
