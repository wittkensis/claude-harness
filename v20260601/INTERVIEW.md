# Bootstrap Interview — question bank

The bootstrap asks **only the gaps** that investigation (Phase 1) couldn't settle, batched via
`AskUserQuestion`. Each answer maps to a field in `~/.claude/harness.config.json`
(schema: `kit/templates/harness.config.schema.json`). Don't ask what you can detect.

## 1. Projects & workspace
- **Where do your work repos live?** (one or more parent dirs) → `project_roots`
  - Used for: SessionStart surfacing each project's CLAUDE.md, and `tokens.py audit` scanning `.env*`.
- **Any immutable / do-not-edit paths?** (e.g. a `data/raw/` of sources, generated dirs) → `protected_globs`

## 2. Commit gate (quality gate on `git commit`)
- **How are your projects typechecked and tested?** Leave blank to auto-detect by marker
  (package.json→tsc+npm test, pyproject→mypy/pyright+pytest, Cargo.toml→cargo check+test, go.mod→go vet+test).
  Override only if non-standard → `commit_gate.typecheck`, `commit_gate.test`
  - These run as `sh -c "<cmd>"` from the project root. A failure blocks the commit (`[wip]` bypasses).

## 3. Format-on-edit
- **Formatter?** Blank = auto-detect (eslint/ruff/black/rustfmt/gofmt). Custom → `lint_fix.command`
  (a template; `{file}` → edited path).

## 4. Secrets & tokens (security-critical)
- **Where do secret VALUES live on this machine?** (pick all that apply) → `token_target_types`
  - `env` (`.env.local`), `ci-secret` (GH Actions / GitLab CI / Vault / AWS SM / Doppler),
    `deploy-env` (platform env vars), `console` (provider dashboard)
- **Registry location?** Default `~/.claude/token-registry.json` → `token_registry_path`
  - Reminder: the registry is **metadata only** — values never go in it.

## 5. Deploy adapter (only if you ship apps from here)
- **Deploy target?** vercel / netlify / fly / k8s / `ssh:<host>` / none → `deploy.deploy_target`
- **Secrets store for deploys?** gh-secrets / vault / aws-sm / doppler / platform-env → `deploy.secrets_store`
- **Domain/DNS provider?** cloudflare / route53 / namecheap / none → `deploy.domain_provider`
- **CI?** github-actions / gitlab-ci / none → `deploy.ci`
- **Git host?** github / gitlab / bitbucket / azure-devops → `git_host`

## 6. Skill collisions (only if Phase 1 found name clashes)
- For each kit skill whose name already exists in `~/.claude/skills/`: keep the existing one, or
  review the ported version? (install copies-if-absent and reports these; never auto-clobbers.)

---
After the interview: write `harness.config.json`, validate against the schema, then run
`install.py --config <that file>` and `port-test.py`.
