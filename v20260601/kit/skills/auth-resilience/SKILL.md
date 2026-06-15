---
name: auth-resilience
description: Doctrine for surviving auth/connectivity roadblocks in external tools (any MCP server, gh, git remote, any API) without halting. Use when a tool call fails with auth/timeout/401/expired/token errors, when resuming a session that has parked auth-blocked work, or when the user says auth is fixed / "resume". Defer-and-continue: park the blocked step, keep doing everything that doesn't depend on it, auto-resume when auth returns. Goal — NEVER require manual tool-work from the user unless the credential is genuinely human-only.
---

# Auth Resilience

You are an **autonomous operator who never lets one blocked external call stall the whole job.** An auth/timeout failure is a *deferred step*, not a dead session. (Overnight MCP/API timeouts are the canonical case: park the blocked remote step, finish the build, resume it when auth returns.)

## Golden rule
**Never require the user to do manual work in a tool unless the credential is genuinely human-only** (OAuth re-login, MFA). Everything else — retries, token refresh, reconnects, alternate paths — you handle yourself.

## When a tool call fails — the response ladder (do the most automatic thing first)

1. **Classify.** Transient (timeout, 5xx, ECONNRESET, network) vs expired-credential (401/403, "token expired") vs missing-config vs rate-limit. If it's a real logic/usage error, this skill doesn't apply — fix the call.
2. **Retry with backoff** (transient): 2–3 attempts, ~2s → 8s → 30s. Most overnight MCP timeouts clear on retry.
3. **Programmatic refresh** before bothering the human: refresh/rotate the token, reconnect the MCP server (`claude mcp` reconnect), re-init the client. Try this for expired credentials.
4. **Alternate path.** Can the goal be met another way? (DNS via a different record op; deploy step reordered; a cached value reused.) Prefer a path that needs no blocked credential.
5. **Defer + continue.** Park the blocked step and **keep going on everything that doesn't depend on it.** Halting the entire session because the *last* step (often DNS) is blocked is the failure mode we're eliminating. Code, tests, commits, pushes, deploy config — all proceed.
6. **Human-only fallback (last resort).** Only if the credential truly needs the human: park ONE crisp instruction ("re-auth the blocked MCP: `claude mcp ...`") and continue all other work. One instruction, not a blocked session.

## Parking & resuming (durable across sessions)

- **Park:** `python3 ~/.claude/hooks/deferq.py add --service <remote> --task "<the blocked step>" --resume "<which skill/step to re-run>" --project <repo>`. (The `auth-failure` hook also auto-parks on detected failures.)
- **The queue survives** session end + compaction: `~/.claude/state/deferred-tasks.jsonl`. The SessionStart hook surfaces open items every new session.
- **Resume:** when the user says auth is fixed / "resume", or at session start with open items: `deferq.py list`, re-attempt each parked task, and `deferq.py resolve <id>` on success. Resume **without** asking the user to re-explain — the queue holds the full intent.

## Reporting
When you defer, tell the user in one line what you parked and what you completed anyway — e.g. *"The deploy platform's MCP timed out; parked the DNS/env step (will auto-resume), but the app is built, tested, committed, and pushed."* Never silently drop a blocked step; never silently halt.

TERMINATION: the failed call is either (a) recovered via retry/refresh/alternate path, or (b) parked in deferq AND all non-dependent work is complete. Resume mode: every open queue item for the now-working service has been re-attempted and resolved-or-re-parked. Don't escalate to the user unless a human-only credential is the sole remaining blocker.
