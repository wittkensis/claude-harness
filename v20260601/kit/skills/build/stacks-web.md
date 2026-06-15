# Web Stack Patterns

## Next.js (Full-Stack Default)

**Version:** 14.x+ (App Router)

```
Next.js 14 + React 19 + TypeScript 5.8 + Tailwind 3.4
+ Prisma (ORM) or Drizzle (lighter)
+ PostgreSQL (production) or SQLite (simple)
```

When to use: full-stack apps, SSR/SSG needed, API routes needed, SEO critical

**package.json:**
```json
{
  "dependencies": {
    "next": "^14",
    "react": "^19",
    "@prisma/client": "^5"
  },
  "devDependencies": {
    "typescript": "^5.8",
    "tailwindcss": "^3.4",
    "prisma": "^5"
  }
}
```

## Vite (SPA Only)

```
Vite + React 19 + TypeScript 5.8 + Tailwind 3.4
```

When to use: SPA only, no SSR, no API routes, static single-page app

## SaaS App

```
Next.js 14 + tRPC (type-safe API) + Prisma + PostgreSQL
+ Clerk or NextAuth (auth) + Vercel (deployment)
```

## AI-Powered Web App

```
Next.js 14 + Anthropic SDK or Vercel AI SDK
+ MCP Servers (data access)
+ Tailwind + Vercel (edge functions)
```

## ORM Selection

| ORM | When |
|-----|------|
| Prisma | TypeScript apps, good DX, migrations |
| Drizzle | Lighter bundle, SQL-like syntax, more control |
| Raw SQL | Personal apps, simple queries, no migrations needed |

## Deployment

- **Vercel** — default for Next.js (zero-config)
- **Netlify** — static sites, JAMstack
- **Railway** — standalone backends, databases (see cloud.md)
