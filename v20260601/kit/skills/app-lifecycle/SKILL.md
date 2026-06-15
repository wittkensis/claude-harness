---
name: app-lifecycle
description: End-to-end lifecycle for a deployable app on this machine — initiate a new app, ship a feature update, or migrate an existing app into the harness conventions. Stack-agnostic; reads naming, project root, deploy target, and secrets store from harness.config.json. Use for new project kickoff, feature updates, or onboarding an app. Triggers: new app, new project, kickoff, feature update, migrate app, app lifecycle.
---

# App Lifecycle (adapter)

The authoritative path for standing up and evolving a deployable app, consistently, every time.
Machine specifics (project root, git host, deploy target, secrets store) come from
`~/.claude/harness.config.json`. This skill orchestrates the others: `plan` → `build`/`swarm` →
`auth` → `deploy` → `token-rotation`.

## Mode A — Initiate a new app
1. **Plan** — run `grill-me`, then `plan` to lock scope, stack, and the north-star "done."
2. **Local repo** — create the project folder under the configured `project_roots[0]` using the
   agreed naming convention; `git init`; first commit. **Local, never a synced/cloud-mirrored dir**
   (file-watchers + sync race and corrupt working trees).
3. **Remote** — create the repo on the configured `git_host` (private by default); push.
4. **Scaffold** — minimal working skeleton in the chosen stack; `CLAUDE.md` (complete, not a stub);
   a project-local `{proj}--deploy` skill (see `meta` → project-skill).
5. **Secrets** — register each API key/secret in `token-rotation` (metadata only) and place values
   in `.env.local` + the configured secrets store. Never commit a value.
6. **Auth** — if the app should be gated, apply the `auth` pattern before the first deploy.
7. **Deploy** — `deploy` skill: ship + `deploy-verifier` confirms it live.
8. **Big build?** — if the initial build splits into ≥2 independent streams, hand the build phase
   to `swarm` (parallel worktree workers), then integrate + validate.

## Mode B — Feature update
`plan` the change → branch → `build` (or `swarm` if large) → two-step completion gate (typecheck +
exercise intent) → commit (the gate hook enforces this) → `deploy` → verify. Bump version +
CHANGELOG. Keep changes surgical.

## Mode C — Migrate an existing app into the harness
1. Move/clone it under a `project_roots` dir (off any synced/cloud dir).
2. Add/repair `CLAUDE.md`, a project-local deploy skill, `.env.local` + `.gitignore`.
3. `tokens.py audit` to register its secrets; wire any `needs-review`.
4. Add the cache-bust mechanism if missing; wire CI per config.
5. `deploy` + `deploy-verifier` to confirm parity.

TERMINATION: the app exists at its conventional local path + remote, builds clean, is deployed and
verified live, its secrets are registered and wired, and (if gated) the auth gate fires.
