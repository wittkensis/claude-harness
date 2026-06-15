# Project Setup

## Project Structure

```
{Project Name}/
├── make.code-workspace
├── app/                   ← git root (Next.js / Tauri source)
│   ├── CLAUDE.md          ← rich project context, not a stub
│   ├── LEARNINGS.md
│   ├── Dockerfile
│   ├── .claude/
│   │   ├── CLAUDE.md      ← extended context (optional)
│   │   ├── settings.json  ← hooks
│   │   └── skills/        ← {proj}--*.md skills
│   └── plan/
│       ├── Brief.md
│       ├── CHANGELOG.md
│       ├── BLOCKERS.md
│       ├── PRDs/
│       ├── Research/
│       └── Concepts/
```

---

## Setup Workflow

### 1. Create Project Folder
```bash
mkdir -p "{project-name}" && cd "{project-name}"
```
- kebab-case name, based on brief title

### 2. Initialize Git
```bash
git init
```
`.gitignore` must include: `node_modules/ dist/ .next/ .env .env.local .DS_Store *.log`

### 3. Create VSCode Workspace

Filename: `make.code-workspace` (standard across all your design system projects)

```json
{
  "folders": [{"name": "{project-name}", "path": "."}],
  "settings": {
    "git.autofetch": true,
    "task.allowAutomaticTasks": "on"
  },
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Sync with GitHub",
        "type": "shell",
        "command": "git pull --rebase --autostash",
        "runOptions": {"runOn": "folderOpen"},
        "presentation": {"reveal": "silent", "panel": "shared", "showReuseMessage": false, "close": true},
        "problemMatcher": []
      },
      {
        "label": "typecheck",
        "type": "shell",
        "command": "npx tsc --noEmit",
        "presentation": {"reveal": "always", "panel": "shared"},
        "problemMatcher": ["$tsc"]
      }
    ]
  }
}
```

Open: `code make.code-workspace`

### 4. Create Folder Structure
```bash
mkdir -p app/plan/PRDs app/plan/Research app/plan/Concepts app/.claude/skills
```

### 5. Save Brief
Copy original brief content to `app/plan/Brief.md`.

---

### 6. Project CLAUDE.md (required — not a stub)

Write a complete, detailed CLAUDE.md at `.claude/CLAUDE.md`. This is Claude's primary reference for every future session — it must be specific enough that a cold-start agent can work without asking questions.

```markdown
# {Project Name}

## Purpose
[One paragraph — what this app does and who uses it]

## Tech Stack
- Framework: [e.g. Next.js 16 + TypeScript + Tailwind]
- Database: [e.g. Neon PostgreSQL via @neondatabase/serverless]
- Auth: [none / clerk / etc.]
- Deployment: [your deploy platform / Vercel / etc.]
- Target URL: [e.g. {app}.{your-domain}]

## Architecture
[Key decisions: folder structure, routing conventions, data flow, API patterns]

## Current Phase
[Brief / Research / Plan / Concepts / Dev]

## Key Decisions
[Track major architectural and product decisions here as the project evolves]

## Versioning & Cache Busting
- App version: see `package.json` → `version`
- Build ID injected at: [e.g. NEXT_PUBLIC_BUILD_ID env var, or next.config.ts generateBuildId]
- Static assets: content-hashed by bundler (automatic)
- API cache headers: [document the strategy — e.g. no-store on all /api routes]
- Release process: bump version in package.json → CHANGELOG.md → git tag vX.Y.Z

## Local Dev
[Commands to start, test, build — also in .claude/skills/run.md]
```

---

### 7. Claude Code Hooks — `.claude/settings.json`

**TypeScript/React projects:**
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "file=\"$(echo $TOOL_INPUT | jq -r '.file_path')\"; [[ \"$file\" == *.ts || \"$file\" == *.tsx ]] && prettier --write \"$file\" 2>/dev/null || true"
      }]
    }]
  }
}
```

**SQLite/Personal Apps — add pre-bash DB backup:**
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "if echo \"$TOOL_INPUT\" | grep -qE 'sqlite3.*(ALTER|DROP|DELETE|UPDATE|INSERT)'; then db=$(echo \"$TOOL_INPUT\" | grep -oE '[^ ]+\\.db' | head -1); [ -f \"$db\" ] && cp \"$db\" \"$db.backup-$(date +%Y%m%d-%H%M%S)\" && echo \"Backed up: $db\"; fi"
      }]
    }]
  }
}
```

---

### 8. Project-Specific Skills (required)

Create `.claude/skills/` with three files tailored to this project. These are loaded by future Claude sessions to understand how the project works without re-reading all the code.

**`.claude/skills/run.md`** — how to start and test locally:
```markdown
# Run

## Dev server
cd app && npm run dev   # http://localhost:3000

## Build
npm run build

## Type check
npx tsc --noEmit

## Test
npm test
```

**`.claude/skills/architecture.md`** — patterns and conventions:
```markdown
# Architecture

## Key Files
- `app/app/page.tsx` — main entry
- `app/lib/db.ts` — database client + schema init
- `app/lib/claude.ts` — AI client
- `app/data/` — static data (chord defs, etc.)
- `app/components/` — shared UI components

## Conventions
- All DB access goes through `lib/db.ts`
- API routes are in `app/api/` — never expose secrets to client
- Components are client-only if they use state/events ("use client")
- [Add project-specific patterns as they emerge]

## Data Flow
[Describe the main data flows: e.g. user input → API route → Claude → DB → UI]
```

**`.claude/skills/deploy.md`** — project-specific deploy steps:
```markdown
# Deploy

Target: {subdomain}.{your-domain} via your deploy platform (your host)

## Steps
1. `git push origin main` — deploy webhook triggers build
2. Monitor: [deploy-platform dashboard URL or curl health check]
3. Health check: `curl -sI https://{subdomain}.{your-domain} | head -3`

## Env Vars (set in deploy-platform dashboard)
- `ANTHROPIC_API_KEY`
- `DATABASE_URL`

## Rollback
Use deploy-platform dashboard → previous deployment → redeploy
```

---

### 9. Versioning & Cache Busting (absolute requirements)

Every project must have version tracking and cache-busting from day one. Non-negotiable.

#### Version tracking

**`package.json`** — start at `1.0.0`, bump on every release:
```json
{ "version": "1.0.0" }
```

**`CHANGELOG.md`** — created at project root, updated before every release:
```markdown
# Changelog

## [1.0.0] — YYYY-MM-DD
### Added
- Initial release
```

**Git tags** — tag every production release:
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin --tags
```

#### Cache busting

**Next.js** — inject build ID into runtime config (`next.config.ts`):
```ts
import { execSync } from 'child_process'

const buildId = execSync('git rev-parse --short HEAD').toString().trim()

const nextConfig = {
  output: 'standalone',
  generateBuildId: async () => buildId,
  env: {
    NEXT_PUBLIC_BUILD_ID: buildId,
    NEXT_PUBLIC_APP_VERSION: process.env.npm_package_version ?? '0.0.0',
  },
}
export default nextConfig
```

**API routes** — all dynamic API responses must set no-cache headers:
```ts
// In every API route handler
headers.set('Cache-Control', 'no-store')
```

**Static assets** — bundler content-hashes filenames automatically. Do not configure `immutable` caching manually unless the bundler guarantees hash changes on content change.

**Tauri/Desktop apps** — version must match `package.json` and `tauri.conf.json`:
```json
// tauri.conf.json
{ "version": "1.0.0" }
```
Use `npm version patch/minor/major` to bump both in sync.

---

### 10. Dockerfile (required for {your-domain} apps)

If deploying to `*.{your-domain}`, create `Dockerfile` in the app root before the initial commit. Your container platform is the deploy path.

**Use the Dockerfile in `engineer/code.md` → "Next.js + SQLite" section** — not a simplified version. The authoritative Dockerfile handles your platform's `NODE_ENV=production` injection (requires `npm ci --include=dev`), `better-sqlite3` native build deps, and SQLite volume setup. A simplified Dockerfile will silently break TypeScript/Tailwind builds.

---

### 11. GitHub

```bash
gh repo create {project-name} --private --source=. --remote=origin
git add .
git commit -m "Initial project setup"
git push -u origin main
```

---

## Phase Transitions

| From | To | Approval Required |
|------|----|-------------------|
| Brief | Research | Research questions list |
| Research | Plan | PRD + Architecture |
| Plan | Concepts | Design requirements |
| Concepts | Dev | Selected concept |

**Never auto-advance. Always pause.**

---

## Phase Checklists

**Research complete when:**
- [ ] Competitive landscape (3+ alternatives)
- [ ] User needs with evidence
- [ ] Technical constraints explored

**Plan complete when:**
- [ ] PRD with user stories
- [ ] Architecture decisions documented
- [ ] Tech stack confirmed
- [ ] Success metrics defined

**Concepts complete when:**
- [ ] 2-3 HTML prototypes
- [ ] Trade-offs documented
- [ ] Recommendation with rationale

---

## Setup Checklist

- [ ] Folder created (kebab-case)
- [ ] Git initialized with .gitignore
- [ ] VSCode workspace created and opened
- [ ] Folder structure created (including `.claude/skills/`)
- [ ] Brief.md saved
- [ ] CLAUDE.md written (complete — not a stub)
- [ ] Hooks configured (`.claude/settings.json`)
- [ ] Project skills created (`run.md`, `architecture.md`, `deploy.md`)
- [ ] Versioning set up (`package.json` version, `CHANGELOG.md`)
- [ ] Cache busting configured (`next.config.ts` or equivalent)
- [ ] Dockerfile created (if targeting {your-domain})
- [ ] GitHub repo created and pushed
- [ ] Tech stack confirmed
