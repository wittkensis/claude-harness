---
name: build--versioning
description: Version numbering strategy — semantic versioning rules, when to bump what, git SHA build IDs for deployable apps, package.json discipline, tag strategy, conventional commits, and CHANGELOG maintenance. Load when tagging a release, deciding a version bump, or setting up versioning for a new project.
metadata:
  kind: reference
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
  refs-external:    # intentional forward-pointers; not seeded (see ref_lint.py)
    - build--caching
    - build--react
    - fleet--app-lifecycle
    - plan--setup
    - write--documentation
---

# Version Numbering

## Invocation
Triggers: versioning, semver, version bump, build id, git sha, changelog, release, tag strategy

## The two versioning contexts

These are different problems. Apply each where it fits, not both everywhere.

| Context | Tool | Purpose |
|---------|------|---------|
| **Libraries / packages** | Semantic Versioning (semver) | Signals breaking changes to consumers |
| **Deployed apps** | Git SHA build ID | Proves what code is running in production |

---

## Semantic Versioning (for libraries, CLIs, APIs)

**MAJOR.MINOR.PATCH** — e.g. `2.4.1`

| Bump | When |
|------|------|
| **MAJOR** | Breaking change: a consumer must change their code to keep working |
| **MINOR** | New capability added; all existing usage still works |
| **PATCH** | Bug fixed; behavior corrected toward documented intent |

**The only question that determines the bump:** can a consumer upgrade without changing their code? Yes → MINOR or PATCH. No → MAJOR.

### What is a breaking change?

- Removing or renaming a public function, type, or export
- Changing a function signature (different params, different return type)
- Changing observable behavior a consumer may be relying on
- Dropping support for a runtime/OS version

What is NOT a breaking change: adding optional params, adding new exports, fixing a bug.

### Pre-release identifiers

```
1.0.0-alpha.1   early API exploration, expect changes
1.0.0-beta.2    feature-complete, bugs expected
1.0.0-rc.1      release candidate, only bug fixes remain
```

Use these when you need to publish for early feedback but don't want consumers to get it automatically.

### Version 0.x

`0.x.y` means the API is unstable — MINOR bumps may break. Graduate to `1.0.0` when the public API is intentionally stable and you're committing to semver guarantees.

---

## Build IDs for deployed apps (git SHA approach)

Personal deployed apps don't have "consumers" — they have one user and a deploy pipeline. Semver adds ceremony without value. What matters: **proving the deployed code matches a commit.**

```typescript
// next.config.ts — wire this at project init, not as an afterthought
import { execSync } from 'child_process';

const buildId = (() => {
  try { return execSync('git rev-parse --short HEAD').toString().trim(); }
  catch { return 'dev'; }
})();

const nextConfig = {
  generateBuildId: async () => buildId,
  env: { NEXT_PUBLIC_BUILD_ID: buildId },
};
```

Then surface it in the app (e.g. Settings page footer: `Build: a3f2c91`). After deploy, `curl https://your-app/api/health | jq .build` confirms the live code matches what you pushed. No more "did it deploy the latest?" guessing.

**Rule:** every new fleet app wires this before first deploy. It's part of the deploy gate in `fleet--app-lifecycle`.

---

## package.json version discipline

```json
{
  "version": "1.0.0"
}
```

- Bump it intentionally, not automatically
- For deployed apps: match the version to a meaningful milestone, not every commit
- For libraries: every publish to npm must have a bumped version — the registry rejects duplicate versions
- `0.0.1` is a valid starting version for an in-development app; it signals "not stable yet"

**Never let a CI bot auto-bump versions without a human decision.** Version numbers are a communication tool. Bots generate noise.

---

## Git tag strategy

```bash
git tag v1.2.0          # annotated when you want a message
git tag -a v1.2.0 -m "Add recurring tasks feature"
git push origin v1.2.0
```

**Always prefix with `v`.** `git tag 1.2.0` looks like a branch name in some tooling. `v1.2.0` is unambiguous.

**Tag after the commit lands on main, not before.** Tags on WIP commits make rollback confusing.

**For deployed apps:** tag major milestones (`v1.0.0` = first deploy to production, `v2.0.0` = major redesign). Don't tag every deploy — that's what the SHA is for.

---

## Conventional commits (optional, high-value when used)

Format: `<type>(<scope>): <description>`

| Type | When |
|------|------|
| `feat` | New feature (MINOR bump candidate) |
| `fix` | Bug fix (PATCH bump candidate) |
| `feat!` or `BREAKING CHANGE:` | Breaking change (MAJOR bump) |
| `chore` | Housekeeping, deps, config (no version bump) |
| `docs` | Documentation only |
| `refactor` | Restructuring without behavior change |
| `perf` | Performance improvement |
| `test` | Tests only |

**Only adopt this if you use it consistently.** A repo with 30% conventional commits and 70% `"fix stuff"` is worse than no convention — it creates false signals about what changed.

---

## CHANGELOG maintenance

```markdown
# Changelog

## [Unreleased]
### Added
- Recurring task recurrence logic (Focus)

### Fixed
- Sheet close animation stuttering on iOS 17

## [1.2.0] — 2026-05-01
### Added
- LOL model switching (Grok support)
- Pipeline company search

### Fixed
- Chip overflow in horizontal scroller
```

**Rules:**
- Keep an `[Unreleased]` section at the top. Move it down at release time.
- Group by: Added, Changed, Fixed, Removed, Security
- One line per change, written for the user not the developer
- Link the version to the tag: `[1.2.0]: https://github.com/...compare/v1.1.0...v1.2.0`
- Never delete old versions — the changelog is a history, not a snapshot

**What doesn't belong in a CHANGELOG:** implementation details, refactors with no user-visible effect, dependency bumps (unless they affect behavior), "various bug fixes" (be specific or don't mention it).

---

## Common mistakes

**Version theater** — bumping `1.0.47` without any semantic reasoning. If you can't explain why it's not `1.1.0`, the number is meaningless.

**Force-pushing tags** — `git push --force origin v1.2.0` after the tag is published destroys the trust of the version number. Create a new tag instead.

**`"version": "0.0.0"` shipped to production** — signals nobody thought about it. Wire `NEXT_PUBLIC_BUILD_ID` instead and the package.json version becomes irrelevant for apps.

**Conflating app version with API version** — if you have a public API, its version is a separate concern from the app that hosts it. A `v2` API endpoint can live in a `1.x` app release.

## Related
- `build--caching` — companion: git SHA build ID is used for cache-busting layer 1
- `write--documentation` — companion: CHANGELOG format and maintenance rules are interlinked
- `plan--setup` — companion: versioning is wired during project setup
- `build--react` — companion: Next.js `generateBuildId` pattern lives in both skills
- `ops--handoff` — companion: handoff notes should reference current version/tag
