---
name: token-rotation
description: Securely manage API tokens/secrets — track which need rotation and keep every token in sync across every place it lives (local env files, CI secrets, deploy-platform env vars, secret managers, provider consoles). ALWAYS use when a token is detected as expired/rotating/needs-rotation, when adding or changing any API key/secret, or when the user asks about token status. Reminds about pending tokens whenever working on apps. Registry holds metadata only — never token values. Triggers: rotate token, token expired, api key, secret, env sync, ci secret, key rotation, tokens due.
---

# Token Rotation & Sync

You are the **custodian of this machine's secrets**. The user relies on this completely: track every token that needs rotation, and keep each one **identical across every place it lives**. A token rotated in one place but stale in another is an outage waiting to happen.

## Iron rule — never store token VALUES
The registry holds **metadata only**: name, service, where it must be synced, cadence, last-rotated, status. Token **values** live ONLY in their real homes — local `.env.local` (gitignored), CI/secret managers, deploy-platform env vars, and the provider console. Never write a value into the registry, a tracked file, a commit, or chat output.

The registry path is read from `~/.claude/harness.config.json` → `token_registry_path` (default `~/.claude/token-registry.json`). The **sync target types** for this machine are defined there too (`token_target_types`) — set during the bootstrap interview to match the work stack.

## The registry (durable, always-on)
Managed via `~/.claude/hooks/tokens.py`:
- `tokens.py audit` — scan known project dirs' `.env*` for secret-ish KEY NAMES (never values) and register new ones as `needs-review`. Run when onboarding or after adding a project.
- `tokens.py list` / `due` / `due-count` — see all / actionable / count.
- `tokens.py add --name X --service S --cadence-days 90 --last-rotated 2026-06-01 --target <type>:<locator>:<KEY>` (repeat `--target` per place it lives).
- `tokens.py rotate <id>` → marks rotated, status **pending-wiring**, prints every target to sync.
- `tokens.py wired <id>` → after ALL targets updated, status **current**.

Status: `current` · `due` (≤14d to next_due) · `overdue` · `pending-wiring` (new value not yet in all targets) · `needs-review` (no cadence/last-rotated set).

## The sync contract — a token is "done" only when ALL targets match
When a token rotates, propagate the **same value** to every target before calling it wired. Target types are config-driven; common ones:

| Target type | How to sync | Notes |
|-------------|-------------|-------|
| `env:<path>` | write the new value into that `.env.local` (gitignored — the guard allows `.env.local`, blocks bare `.env`) | every project that uses the token |
| `ci-secret:<scope>:<NAME>` | set the secret in your CI/secret store (e.g. `gh secret set`, Vault, AWS Secrets Manager) — reads value from stdin/env, never a file | for CI/Actions/runtime |
| `deploy-env:<app>:<VAR>` | set the deploy platform's env var, then redeploy so it takes effect | via the `deploy` skill |
| `console:<service>` | the provider console where the value originates | the source of truth |

**Miss none.** The registry's `targets[]` is the checklist — sync every one, then `wired`. If a target is blocked (e.g. the deploy platform's auth times out), use `auth-resilience`: park that one target, finish the rest, resume later. The token stays `pending-wiring` until truly complete.

## When auth fails with "token expired / 401"
That IS a rotation signal. The `auth-failure` hook parks the blocked call; you should also check/add the token to the registry and rotate it. Expired-credential errors and this skill are two halves of the same loop.

## Always-on reminders
The SessionStart hook surfaces due/overdue/pending/needs-review tokens every session. When you see them, surface to the user in one line — e.g. *"2 tokens waiting to be wired: SERVICE_A_KEY overdue, SERVICE_B_KEY pending-wiring to CI."* Don't let them sit silently.

TERMINATION: for a rotation — every target in the token's `targets[]` holds the new value and status is `current` via `tokens.py wired`. For a status check — due/overdue/pending tokens have been surfaced to the user. Never mark `wired` with an unsynced target; never write a value anywhere it shouldn't live.
