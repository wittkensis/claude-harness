# Cloud Infrastructure

For full project setup with these services, see `stack-matrix.md`.

## Neon (Serverless PostgreSQL)

**Best for:** Production web apps, cloud-hosted Python backends, branching for dev/staging

```bash
# Setup
brew install neon
neon projects create --name my-project
neon connection-string
```

**Connection string format:**
```
postgresql+asyncpg://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Branching (dev/staging isolation):**
```bash
neon branches create --name dev
neon connection-string --branch dev
```

**MCP setup** (manage DB from Claude Code):
```json
{
  "mcpServers": {
    "neon": {
      "command": "npx",
      "args": ["-y", "@neondatabase/mcp-server-neon"],
      "env": { "NEON_API_KEY": "..." }
    }
  }
}
```

---

## Railway (Deployment Platform)

**Best for:** Python/FastAPI backends, any Docker-deployable service

```bash
# Setup
brew install railway
railway login
railway link
railway up
railway logs
```

**Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Auto-injects:** `DATABASE_URL` when you add a PostgreSQL service.

**Environment variables:** set in Railway Variables tab, not in code.

**MCP setup:**
```json
{
  "mcpServers": {
    "railway": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"],
      "env": { "RAILWAY_API_TOKEN": "..." }
    }
  }
}
```

---

## Vercel (Next.js / Static)

**Best for:** Next.js apps, static sites, edge functions

- Zero-config for Next.js
- Preview deploys on every PR
- Edge functions for API routes

---

## When to Use Which

| Need | Service |
|------|---------|
| Serverless Postgres with branching | Neon |
| Python/FastAPI backend | Railway |
| Next.js full-stack | Vercel |
| Static site | Vercel or Netlify |
| Postgres (simple, managed) | Railway PostgreSQL service |
