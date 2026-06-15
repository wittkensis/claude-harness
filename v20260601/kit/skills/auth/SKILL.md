---
name: auth
description: Apply a simple, robust auth gate to a web app so unauthenticated visitors can't reach app content, plus search-engine noindex for non-public apps. Stack-agnostic pattern; env-var names and the login route come from the project. Use when adding a password/login gate, fixing an auth leak, or making an app non-indexable. Triggers: auth, password, login, password gate, authentication, robots, noindex.
---

# Auth Gate (pattern)

A pragmatic gate for "only I / my team should see this." Not a full identity system — a single
shared secret (or your org SSO if you have it) enforced at the edge, so **no app content renders
for an unauthenticated request**. The concrete framework differs per stack; the invariants don't.

## The invariants (these are what get tested)
1. **Deny by default.** A request to any protected route without a valid session **redirects to the
   login route** (or 401 for APIs). If app content ever renders unauthenticated, that's a CRITICAL
   leak — the single most important thing the `deploy-verifier` checks.
2. **The matcher covers everything.** The auth middleware/route-matcher must include *all* app
   routes and APIs, excluding only the login route, its POST handler, and truly-public assets. The
   classic leak is a matcher gap (a route the middleware never runs on).
3. **Secret in env, never in code.** The shared password / SSO client secret lives in the secrets
   store + `.env.local`, tracked by `token-rotation`. The env-var name goes in the project's deploy
   skill; the value never does.
4. **Session cookie:** httpOnly, Secure, SameSite=Lax, sane expiry. Compare the secret in constant
   time where the framework allows.

## Shape (adapt to the stack)
- **Login route** — a minimal form (or SSO redirect). POST validates the secret, sets the session
  cookie, redirects to the app.
- **Middleware / guard** — runs before protected routes; valid cookie → continue, else → redirect.
- **Logout** — clears the cookie.

## Non-public apps: keep them out of search
Add `noindex` (a `<meta name="robots" content="noindex">` and/or `X-Robots-Tag: noindex` header)
and a disallow-all `robots.txt`. A gated app still shouldn't show up in search results.

## Verify (don't trust, check)
After deploy, the `deploy-verifier` agent hits a protected route unauthenticated and expects a
redirect/401, then exercises login. Run it every deploy — auth leaks are silent until someone
finds them.

TERMINATION: an unauthenticated request to every protected route is denied (redirect/401), login
works, the secret is in env only (registered in token-rotation), and a non-public app returns
noindex.
