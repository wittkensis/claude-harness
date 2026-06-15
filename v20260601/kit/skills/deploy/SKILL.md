---
name: deploy
description: Ship a web app to its hosting target and verify it live. Stack-agnostic adapter — reads the deploy target, secrets store, and domain provider from harness.config.json (set during bootstrap). Use when deploying, redeploying, going live, configuring a subdomain, or syncing deploy env vars. Triggers: deploy, redeploy, push, go live, dns, subdomain, env vars.
---

# Deploy (adapter)

You ship apps to **this machine's** infrastructure, not a hardcoded one. The specifics live in
`~/.claude/harness.config.json` → `deploy.{deploy_target, secrets_store, domain_provider, ci}`.
Read them first; if a field is blank, ask the user once and offer to record it in the config.

## The flow (adapt each step to the configured target)

1. **Pre-flight** — clean tree, on `main` (or the deploy branch), build passes locally, the
   two-step completion gate is green. Never deploy a red build.
2. **Secrets present** — every required env var exists in the configured `secrets_store`
   (`gh-secrets` / `vault` / `aws-sm` / `doppler` / platform env). Cross-check against the
   `token-rotation` registry; anything `pending-wiring` must be wired before deploy.
3. **Deploy** — trigger per `deploy_target`:
   - `vercel` / `netlify` / `fly` → their CLI or a git push that auto-builds.
   - `k8s` → apply manifests / bump the image tag.
   - `ssh:<host>` → push + pull + restart the service.
   - `none` → there is no remote; stop after the local build.
4. **Domain / DNS** (only if `domain_provider` is set and a new hostname is needed) — create the
   record via that provider. This is the step most likely to hit an auth/timeout wall overnight;
   if it does, **defer-and-continue** per `auth-resilience` (the rest of the deploy still ships).
5. **Verify live** — run the `deploy-verifier` agent against the URL: reachable, auth gate fires
   (if gated), key routes 200, the **new build actually shipped** (cache-bust/SHA check). A green
   build log is not proof — confirm in production as a user would see it.

## Cache-busting (non-negotiable for web apps)
Build ID injected at compile time, `no-store` on dynamic API routes, content-hashed static
assets. The #1 "I deployed but see the old version" cause is a missing cache-bust — the
deploy-verifier's build-fresh check exists to catch exactly this.

## Project-local deploy skill
Each app should carry its own `{proj}--deploy/SKILL.md` with its concrete locators (target ID,
env-var names, URL). Scaffold it via `meta` → project-skill. **Locators yes, secret values never.**

TERMINATION: the deploy is done when the live URL serves the **new** build (verified by
deploy-verifier), the auth gate behaves as designed, and any blocked DNS/env step is either
complete or parked in the deferred queue with the rest shipped.
