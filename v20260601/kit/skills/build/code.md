# Code Architecture

## Core Principle

Clear over clever. Ship working code. No over-engineering.

---

## Architecture Patterns

### Code Quality
- TypeScript strict mode throughout — no `any`
- Error handling at system boundaries (user input, external APIs)
- Meaningful variable names — no abbreviations
- Comments explain WHY, never WHAT

### Component Design (React)

```typescript
interface DashboardProps {
  userId: string;
  onNavigate: (path: string) => void;
}

export function Dashboard({ userId, onNavigate }: DashboardProps) {
  // focused, typed, accessible
}
```

- Composition over inheritance
- Accessibility built-in (ARIA, semantic HTML, keyboard nav)
- Memo/lazy only where measured benefit exists

### State Management
1. `useState` / `useContext`
2. Zustand (state crosses many components)
3. React Query (server state — separate from client state)
4. Minimize re-renders with proper dependency arrays

### Testing Strategy
- Unit: business logic, utilities
- Integration: critical paths (auth, payments)
- E2E: core user flows only
- Skip: implementation details, snapshot overkill

---

## Project Structure

```
src/
├── components/   # React components
├── lib/          # Utilities, helpers
├── hooks/        # Custom React hooks
├── types/        # TypeScript definitions
├── app/          # Next.js app directory
└── api/          # API routes
```

### File Naming
- Components: `PascalCase.tsx`
- Utilities: `camelCase.ts`
- Types: `types.ts` or `{feature}.types.ts`
- Tests: `{name}.test.ts` colocated

---

## Next.js + SQLite (Web Apps)

### Required config for better-sqlite3 with standalone output

```typescript
// next.config.ts
import path from 'path';
const nextConfig: NextConfig = {
  serverExternalPackages: ['better-sqlite3'],  // required — prevents bundling native addon
  output: 'standalone',
  webpack: (config) => {
    config.resolve.alias['@'] = path.join(__dirname, 'src');  // explicit alias — tsconfig paths unreliable in Docker
    return config;
  },
};
```

### Cache busting (required — three layers)

**Layer 1 — Static assets:** Wire `generateBuildId` to git SHA so every deploy produces unique `/_next/static/[sha]/` URLs. Browsers cache these forever; new deploy = new URL = fresh fetch.

**Layer 2 — API routes:** Every route handler must return `Cache-Control: no-store`. Pattern:
```typescript
const noCache = { headers: { "Cache-Control": "no-store" } };
return NextResponse.json({ data }, noCache);
```

**Layer 3 — `headers()` config in `next.config.ts`:** Documents intent and covers any routes that forget `no-store`:
```typescript
async headers() {
  return [
    { source: "/_next/static/(.*)", headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }] },
    { source: "/api/(.*)", headers: [{ key: "Cache-Control", value: "no-store" }] },
    { source: "/((?!_next/static|api).*)", headers: [{ key: "Cache-Control", value: "no-cache, must-revalidate" }] },
  ];
},
```

See `app-lifecycle` for the full checklist.

---

### 'use server' files can only export async functions

Move all constants, types, and non-function exports to a separate `src/lib/constants.ts`
(no directive). Only async functions can be exported from files with `'use server'`.

### Dockerfile for Next.js on your deploy platform (or any NODE_ENV=production injection)

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
RUN apk add --no-cache python3 make g++  # required for better-sqlite3
COPY package*.json ./
RUN npm ci --include=dev  # --include=dev because your deploy platform injects NODE_ENV=production
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
RUN apk add --no-cache sqlite
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
RUN mkdir -p ./public  # use RUN mkdir not COPY with 2>/dev/null — BuildKit can't handle shell syntax in COPY
COPY --from=builder /app/data ./data-seed
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN mkdir -p /data && chown nextjs:nodejs /data
VOLUME ["/data"]
EXPOSE 3000
USER nextjs
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENTRYPOINT ["/entrypoint.sh"]
```

### SQLite seed files — avoid macOS-specific unistr()

When generating seed SQL on macOS with `sqlite3 .dump`, any non-ASCII chars are encoded
as `unistr('
')` etc. These don't work in better-sqlite3 or Linux SQLite.
Post-process with Python before committing:

```python
import re
def fix_unistr(m):
    inner = m.group(1)
    fixed = inner.encode('utf-8').decode('unicode_escape').replace("'", "''")
    return f"'{fixed}'"
result = re.sub(r"unistr\('((?:[^'\\]|\\.)*)'\)", fix_unistr, content)
```

---

## Desktop Apps (Tauri)

```
app/
├── src/            # React frontend
├── src-tauri/      # Rust backend
│   ├── src/main.rs
│   └── tauri.conf.json
└── package.json
```

Checklist:
- [ ] Meaningful Mac app name (not "Tauri App")
- [ ] Custom icon
- [ ] SQLite for data, Tauri Store for settings
- [ ] Menu bar integration if appropriate

---

## Component Sizing

| Guideline | Target |
|-----------|--------|
| Most components | 150-200 lines |
| Hard limit | 300 lines |
| Micro-components | Avoid < 30 lines |

**Split when:** approaching 250 lines · multiple distinct sections · multiple useState for different concerns · significant rendering branches

**Splitting process:**
1. Identify logical boundaries
2. Extract to new file
3. Run typecheck
4. Run tests
5. Verify UI unchanged

---

## Quality Checklist

- [ ] TypeScript strict mode, no `any`
- [ ] Error boundaries at appropriate levels
- [ ] Loading/error states handled
- [ ] Accessible (keyboard nav, screen reader)
- [ ] Tests for critical paths
- [ ] No console.logs left in
- [ ] Dependencies minimal and justified
- [ ] Components under 300 lines

---

## Anti-Patterns

**NEVER:** Add unnecessary dependencies · write clever code over clear · skip types · deploy without request · create backwards-compatibility shims · over-test implementation details · ignore accessibility

---

## Completion Gate

A task is done only when all three hold:
1. `npx tsc --noEmit` passes
2. Feature works as intended in the running app
3. No adjacent code was touched beyond task scope

"It compiled" is not done. See Task Discipline rules in global CLAUDE.md.

**For any UI/CSS/layout/overlay/z-index change**, step 2 requires visual verification:
- Start the dev server
- Open the affected screen in a headless browser (Playwright at 390×844 viewport)
- Screenshot the golden path — including the specific interaction (open sheet, scroll header, etc.)
- Confirm the fix with computed style or DOM inspection (`getComputedStyle`, `parentElement`, `getBoundingClientRect`)

Code reading is not sufficient. z-index, `position: fixed`, `createPortal`, and React hydration all interact in ways that only manifest at runtime.

---

## Next.js Gotchas (iCloud + Docker)

**iCloud Drive + large git repos → git hangs:** git status becomes O(n) iCloud API calls when build artifacts are tracked. Aggressively gitignore all build output directories on iCloud-hosted projects. Use `git rm -r --cached` to untrack already-committed directories.

**Large binary files block GitHub push even after gitignore:** Gitignore stops future tracking but doesn't rewrite history. If binaries are in old commits, use `git filter-repo`:
```bash
git filter-repo --path "path/to/binaries" --invert-paths --force
git remote add origin https://github.com/...  # filter-repo removes remote
git push --force origin main
```

**redirect() in page components breaks Next.js 15 SSR:** Calling `redirect()` inside a page component during static generation causes `<Html> should not be imported outside of pages/_document`. Do root-level redirects in middleware only.
**ALWAYS:** Run tests before commits · verify before marking done · explain trade-offs · ask when requirements are unclear
