---
name: build
description: Production code — architecture, quality standards, and patterns. Routes to specialties for desktop (Tauri), AI integration, stack selection, TDD, and prototyping. For large multi-stream work that splits into independent parts run in parallel (a whole new app, a big feature, a cross-cutting audit), use the `swarm` skill instead — it orchestrates parallel worktree workers that each load these specialties for their code conventions.
---

# Build

Core patterns in [code.md](code.md).

**Parallel work?** If the job is a whole new app, a large feature, or an audit that splits into ≥2 independent units, hand off to the `swarm` skill — it decomposes, fans out concurrent worktree workers, and integrates. Each worker loads these specialties for its code conventions.

## Core Principle

Clear over clever. Ship working code. No over-engineering.

## Quick Reference

- TypeScript strict mode — no `any`
- Components: 150-300 lines, one responsibility each
- State: useState → Zustand (cross-component) → React Query (server state)
- Tests: unit (business logic), integration (critical paths), E2E (core flows only)
- Accessibility built-in — semantic HTML, ARIA, keyboard nav

> These specialties carry this Mac's stack opinions (Tauri/Next.js/React). On the work
> machine, treat them as reference patterns, not mandates — the interview sets the real
> stack defaults. Drop or replace any specialty that doesn't match your work stack.

## Specialties

| File | When |
|------|------|
| [tauri-setup.md](tauri-setup.md) | New Tauri project, tauri.conf.json, SQLite, window config |
| [tauri-titlebar.md](tauri-titlebar.md) | Custom draggable titlebar, macOS traffic lights |
| [tauri-icons.md](tauri-icons.md) | Generating all icon sizes from a source image (Tauri/desktop) |
| [web-icons.md](web-icons.md) | favicon, apple-touch-icon, PWA icons for web apps |
| [ios-web-app.md](ios-web-app.md) | iOS SPA shell, safe area, URL bar prevention, mobile panel architecture |
| [ai-anthropic.md](ai-anthropic.md) | `@anthropic-ai/sdk`, Claude API, prompt caching |
| [stacks-web.md](stacks-web.md) | Next.js, Vite, React patterns, ORM selection |
| [stacks-desktop.md](stacks-desktop.md) | Desktop app decisions (Tauri vs Electron) |
| [stacks-scripts.md](stacks-scripts.md) | Python scripts, HTML prototypes |
| [stacks-cloud.md](stacks-cloud.md) | Cloud infrastructure / hosted database decisions |
| [tdd.md](tdd.md) | Test-driven development — red-green-refactor loop |
| [prototype.md](prototype.md) | Throwaway code to answer a design question |

## AI: Common Principles

- Store API keys in environment variables (server) or the platform's secret store — never in code
- Always prompt-cache long system prompts (`cache_control: { type: "ephemeral" }`)
- Type all models — never use raw strings
- Test connections with a cheap model before the expensive one
- Default to the latest, most capable Claude models for new AI work

## Stack Defaults (reference — confirm against the work stack)

| Project Type | Stack |
|--------------|-------|
| Desktop | Tauri + React + TypeScript + SQLite |
| Web (full-stack) | Next.js + TypeScript + Tailwind + Prisma |
| Web (SPA) | Vite + React + TypeScript + Tailwind |
| Prototype | HTML + jQuery + Tailwind (CDN, no build) |
| Script | Python (minimal deps) |

**Always choose the most basic stack that meets requirements.**
