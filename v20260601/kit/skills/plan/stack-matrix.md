# Tech Stack Decision Matrix

## Core Principle

Always choose the most basic stack that meets requirements. Start simple.

---

## Quick Decision Tree

```
What are you building?

├─ Desktop app?
│  ├─ Need Node packages? → Electron + React + TypeScript
│  └─ Standard web tech sufficient? → Tauri + React + TypeScript + SQLite
│
├─ Full-stack web app?
│  └─> Next.js + TypeScript + Tailwind + Prisma/Drizzle + PostgreSQL
│
├─ SPA only (no backend)?
│  └─> Vite + React + TypeScript + Tailwind
│
├─ API only?
│  ├─ TypeScript/Node? → Next.js API routes or Express
│  └─ Data-heavy / ML? → FastAPI (Python)
│
├─ Prototype / Concept?
│  └─> HTML + jQuery + Tailwind (no build, single file)
│
└─ Quick script?
   └─> Python (minimal deps, no git if < 50 lines)
```

---

## Stack Profiles

### Desktop App
```
Tauri 2.x + React 19 + TypeScript 5.8 + Tailwind 3.4
+ SQLite (complex data) + Tauri Store (preferences) + Zustand (state)
```

### Full-Stack Web
```
Next.js 14 (App Router) + React 19 + TypeScript 5.8 + Tailwind 3.4
+ Prisma (ORM) + PostgreSQL (production) or SQLite (simple)
```

### SaaS Web App
```
Next.js 14 + tRPC (type-safe API) + Prisma + PostgreSQL
+ Clerk or NextAuth (auth) + Vercel (deployment)
```

### Python Backend / API
```
FastAPI + SQLAlchemy (async) + Alembic (migrations) + PostgreSQL
+ Jinja2 (if SSR templates needed)
```

### Quick Prototype
```
HTML + jQuery (CDN) + Tailwind (CDN)
```

### Cloud-hosted Python Project (cloud Python stack)
```
FastAPI + Neon (PostgreSQL) + Railway (deployment)
+ your AI provider SDK (e.g. Anthropic)
```

---

## When to Deviate from Defaults

**Electron instead of Tauri:**
- Need specific Node packages (puppeteer, etc.)
- Building IDE-like tools

**Vite instead of Next.js:**
- SPA only (no SSR, no API routes)
- Static single-page app

**PostgreSQL instead of SQLite:**
- Multi-user concurrent access
- Production web app

**pnpm** preferred over npm for all projects.

---

## Anti-Patterns

**DON'T:** Add packages without need · use frameworks for simple problems · choose tech because it's trendy · over-engineer fleeting tools
**DO:** Start simple · add complexity only when pain is real · document stack choice in project CLAUDE.md · question every dependency
