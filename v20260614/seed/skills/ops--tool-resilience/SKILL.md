---
name: ops--tool-resilience
description: Doctrine for surviving auth/connectivity roadblocks in external tools (Hostinger MCP, gh, git remote, any API/MCP) without halting. Use when a tool call fails with auth/timeout/401/expired/token errors, when resuming a session that has parked auth-blocked work, or when the user says auth is fixed / "resume".
metadata:
  status: active
  modified: 2026-06-10
  source: blueprint-ew-v20260614
  refs-external:    # intentional forward-pointers; not seeded (see ref_lint.py)
    - audit--harness
    - audit--tokens
---

# Auth Resilience

## Invocation
Triggers: auth failed, token expired, 401/403, mcp timeout, hostinger timeout, resume, auth is fixed

You are an **autonomous operator who never lets one blocked external call stall the whole job.** An auth/timeout failure is a *deferred step*, not a dead session.

Example: Overnight Hostinger MCP timeouts are the canonical case. Park the DNS step, finish the build, resume the DNS at dawn.

## RULES

* **Automation First:** Never require the user to do manual work in a tool unless the credential is genuinely human-only (OAuth re-login, MFA). Everything else — retries, token refresh, reconnects, alternate paths — you handle yourself.
## STEPS

When a tool call fails, follow this response ladder (do the most automatic thing first)

1. **Classify:** Transient (timeout, 5xx, ECONNRESET, network) vs expired-credential (401/403, "token expired") vs missing-config vs rate-limit. If it's a real logic/usage error, this skill doesn't apply — fix the call.
2. **Retry with Backoff** (transient): 2–3 attempts, ~2s → 8s → 30s. Most overnight MCP timeouts clear on retry.
3. **Programmatic Refresh:** before bothering the human: refresh/rotate the token, reconnect the MCP server (`claude mcp` reconnect), re-init the client. Try this for expired credentials.
4. **Alternate Path.** Can the goal be met another way? (DNS via a different record op; deploy step reordered; a cached value reused.) Prefer a path that needs no blocked credential.
5. **Defer & Continue:** Park the blocked step and **keep going on everything that doesn't depend on it.** Halting the entire session because the *last* step (often DNS or a deploy API) is blocked is the failure mode we're eliminating. Code, tests, commits, pushes, config — all proceed.
6. **Human-Only Fallback (Last Resort):** Only if the credential truly needs the human: park ONE crisp instruction ("re-auth Hostinger MCP: `claude mcp ...`") and continue all other work. One instruction, not a blocked session.

## Parking & Resuming (durable across sessions)

- **Park:** `python3 ~/.claude/hooks/deferq.py add --service <service-name> --task "description of blocked action" --resume "skill or step to resume" --project <repo>`. (The `auth-failure` hook also auto-parks on detected failures.)
- **The queue survives** session end + compaction: `~/.claude/state/deferred-tasks.jsonl`. The SessionStart hook surfaces open items every new session.
- **Resume:** when the user says auth is fixed / "resume", or at session start with open items: `deferq.py list`, re-attempt each parked task, and `deferq.py resolve <id>` on success. Resume **without** asking the user to re-explain — the queue holds the full intent.

## Reporting

When you defer, tell the user in one line what you parked and what you completed anyway — e.g. *"Hostinger MCP timed out; parked the `meals` A-record (will auto-resume), but the app is built, tested, committed, and pushed."* Never silently drop a blocked step; never silently halt.

TERMINATION: the failed call is either (a) recovered via retry/refresh/alternate path, or (b) parked in deferq AND all non-dependent work is complete. Resume mode: every open queue item for the now-working service has been re-attempted and resolved-or-re-parked. Don't escalate to the user unless a human-only credential is the sole remaining blocker.

## Related
- `audit--tokens` — companion: tool failures trigger token rotation; token skill manages the rotation
- `ops--session-start` — feeds-into: session-start surfaces parked deferred tasks from prior failures
- `ops--swarm` — companion: swarm workers can fail with auth issues; resilience handles recovery
- `ops--laundry-list` — companion: laundry-list batch items may hit auth failures; resilience keeps work moving
- `audit--harness` — companion: retro checks the deferred queue for stale unresolved items
