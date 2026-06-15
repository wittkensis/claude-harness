---
name: plan
description: Project planning — initialization workflow, PRDs, and GitHub issues. Runs grill-me on new projects to surface needs before committing to a structure.
---

# Plan

## New Project Rule

**Always run `grill-me` before planning a new project.** Surface the full requirement tree before committing to any structure or stack. Ask questions one at a time.

## Specialties

| File | When |
|------|------|
| [setup.md](setup.md) | Full initialization workflow (Brief → Research → Plan → Concepts → Dev) |
| [stack-matrix.md](stack-matrix.md) | Tech stack decision guide when defaults don't fit |
| [prd.md](prd.md) | Synthesize context into a structured PRD |
| [issues.md](issues.md) | Break plan into independently-grabbable GitHub issues (tracer bullets) |

## Defaults (confirm against the work stack — set by the bootstrap interview)

- **Desktop:** Tauri + React + TypeScript + SQLite + Tailwind
- **Web:** Next.js + TypeScript + Tailwind
- **Prototype:** HTML + jQuery + Tailwind (single file — see build specialty)
- **API/backend:** FastAPI (Python) or Next.js API routes

## Non-negotiable requirements on every project

1. **Claude initialization** — `CLAUDE.md` must be complete and specific (not a stub). If the project deploys, scaffold a project-local deploy skill in `.claude/skills/` (see `meta` → skill-authoring). 
2. **Versioning** — version field + `CHANGELOG.md` + git tags on every release.
3. **Cache busting** — build ID injected at compile time, `no-store` on all API routes, content-hashed static assets.

**Always pause for user approval at each phase transition.**
