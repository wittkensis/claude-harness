# Patch — Orchestrator Stale Agent / Freeze Fix

**Applies to:** blueprint-ew-v20260614  
**Date:** 2026-06-14  
**Source:** Observed session failure — stale background agents + orchestrator freeze  
**Scope:** `orchestrate` skill + `orchestrator.py` state helper  
**Severity:** High — causes multi-session freezes and orphaned agent accumulation

---

## Diagnosis

### Root cause 1 — `_is_held()` does not block on `status == "approved"`

In `orchestrator.py`, the backpressure gate only blocks when `status == "awaiting_reply"`:

```python
def _is_held(s):
    if s["status"] != "awaiting_reply":
        return False   # ← "approved" passes through here
```

Once a batch is approved and agents are spawned, status transitions to `"approved"` — and `held` immediately returns `False`. If the session closes at this point and a new one opens, the kickoff sees backpressure as CLEAR and proposes a **new batch on top of in-flight agents**. Those orphaned agents accumulate across sessions.

**Evidence:** Cycle log gap of 47 hours (2026-06-11 21:50 → 2026-06-14 16:18) where batch 87/89/84 was approved but the cycle was never closed. Done-ticks all fired at once at 16:18 — manual catch-up, not real agent returns.

### Root cause 2 — No in-flight agent tracking

There is no record of which background agents are running, when they were spawned, or when to consider them stale. The SKILL.md says "≤3 active background agents at any time" but there is no enforcement mechanism or visibility into the actual count.

### Root cause 3 — No resume protocol for `status == "approved"`

The kickoff branches on `held` (awaiting_reply) but has no branch for `status == "approved"` (agents spawned, cycle not closed). A resumed session falls through to "propose a new batch" — stacking fresh agents on top of orphaned ones.

---

## Change 1 — Fix `_is_held()` to block on `status == "approved"` (orchestrator.py)

**File:** `~/.claude/state/orchestrator/orchestrator.py`

Replace:

```python
def _is_held(s):
    if s["status"] != "awaiting_reply":
        return False
    age = _age_hours(s["suggested_at"])
    return age is None or age < STALE_HOURS
```

With:

```python
def _is_held(s):
    if s["status"] == "awaiting_reply":
        age = _age_hours(s["suggested_at"])
        return age is None or age < STALE_HOURS
    if s["status"] == "approved":
        # agents are in-flight; block until explicitly cleared or stale
        age = _age_hours(s["answered_at"])
        return age is None or age < STALE_HOURS
    return False
```

Also update `cmd_status` to print a distinct message when `status == "approved"`:

```python
    print("BACKPRESSURE: " + (
        "HELD — awaiting your reply, do NOT suggest more" if held and s["status"] == "awaiting_reply"
        else "HELD — agents in flight, cycle not closed (clear to reset)"
              if held and s["status"] == "approved"
        else "CLEAR — free to suggest a new batch"
    ))
```

---

## Change 2 — Add in-flight agent tracking (orchestrator.py)

**File:** `~/.claude/state/orchestrator/orchestrator.py`

Add a new state file `inflight-agents.json` alongside `pending-batch.json`. Add three new commands:

```python
INFLIGHT = HERE / "inflight-agents.json"
AGENT_STALE_HOURS = 4  # agents older than this are considered hung

def _load_inflight():
    if INFLIGHT.exists():
        return json.loads(INFLIGHT.read_text())
    return {}

def _save_inflight(d):
    INFLIGHT.write_text(json.dumps(d, indent=2))

def cmd_track_agent(args):
    # track-agent <item_id> <description> [executor]
    # call immediately after spawning a background agent
    if len(args) < 2:
        print("usage: orchestrator.py track-agent <item_id> <description> [executor]")
        sys.exit(2)
    item_id, desc = args[0], args[1]
    executor = args[2] if len(args) > 2 else "unknown"
    d = _load_inflight()
    d[item_id] = {"description": desc, "executor": executor, "spawned_at": _now()}
    _save_inflight(d)
    _log("agent-tracked", f"#{item_id} via {executor}: {desc}")
    print(f"tracking agent for #{item_id}")

def cmd_agent_done(args):
    # agent-done <item_id>  — call alongside done-tick when an agent returns
    if not args:
        print("usage: orchestrator.py agent-done <item_id>")
        sys.exit(2)
    item_id = args[0]
    d = _load_inflight()
    if item_id in d:
        age = _age_hours(d[item_id]["spawned_at"])
        del d[item_id]
        _save_inflight(d)
        _log("agent-done", f"#{item_id} returned after {age:.1f}h")
        print(f"agent #{item_id} retired ({age:.1f}h)")
    else:
        print(f"agent #{item_id} not in inflight list (no-op)")

def cmd_inflight(args):
    # list all in-flight agents with age; exit 1 if any are stale
    d = _load_inflight()
    if not d:
        print("no agents in flight")
        sys.exit(0)
    stale = False
    for item_id, info in d.items():
        age = _age_hours(info["spawned_at"])
        flag = "⚠️ STALE" if age and age > AGENT_STALE_HOURS else "ok"
        if flag.startswith("⚠️"):
            stale = True
        print(f"  #{item_id}  [{info.get('executor','?')}]  {info.get('description','')}  "
              f"({age:.1f}h ago)  {flag}")
    sys.exit(1 if stale else 0)
```

Register in `CMDS`:
```python
CMDS = {
    ...,
    "track-agent": cmd_track_agent,
    "agent-done": cmd_agent_done,
    "inflight": cmd_inflight,
}
```

---

## Change 3 — Resume protocol + anti-pattern (SKILL.md)

**File:** `~/.claude/skills/orchestrate/SKILL.md`

### 3a — Update helper commands block

Add to the helper commands list:

```
python3 ~/.claude/state/orchestrator/orchestrator.py inflight          # list in-flight agents (exit 1 if stale)
python3 ~/.claude/state/orchestrator/orchestrator.py track-agent <id> "<desc>" [executor]
python3 ~/.claude/state/orchestrator/orchestrator.py agent-done <id>  # retire a returned agent
```

### 3b — Add agent tracking to step 3 (On reply → delegation)

After each `backlog.py start <id>` and before spawning the agent, add:

```
python3 ~/.claude/state/orchestrator/orchestrator.py track-agent <id> "<title>" <executor>
```

After each `backlog.py done <id> && orchestrator.py done-tick`, add:

```
python3 ~/.claude/state/orchestrator/orchestrator.py agent-done <id>
```

### 3c — Add branch for `status == "approved"` in KICKOFF

In the "Branch on backpressure" section, add after the `held == 1` case:

> **`status == "approved"` (agents spawned, cycle not closed):** Run `orchestrator.py inflight`. If all agents < 4h: show "batch in execution — waiting on agents; reply `clear` to force-reset." If any agents ≥ 4h: surface each as stale in 👤 block (`⚠️ stale agent → #<id> (<Xh>)`), then block those items with `backlog.py block <id> "stale agent: no return in Xh"`, call `orchestrator.py agent-done <id>` for each, then run `orchestrator.py clear` and continue to propose a fresh batch.

### 3d — Add anti-patterns

Add to the anti-patterns list:

```
- ❌ Closing a session with status == "approved" — always run `orchestrator.py clear` or 
  `ops--handoff` (which surfaces in-flight state) before the session ends.
- ❌ Spawning a background agent without `track-agent` — untracked agents are invisible 
  on resume and will accumulate across sessions.
```

---

## Applying This Patch

These are three independent changes; apply in order:

1. Edit `~/.claude/state/orchestrator/orchestrator.py` — apply Changes 1 and 2
2. Edit `~/.claude/skills/orchestrate/SKILL.md` — apply Change 3 (all four sub-sections)
3. Verify: `python3 ~/.claude/state/orchestrator/orchestrator.py status` should now show
   "HELD — agents in flight" when status is `approved`, not "CLEAR"

No seed skill updates are required (the `orchestrate` skill is personal/fleet, not seeded).
If the blueprint ever seeds an orchestrate skill, include this patch in the next version's CHANGELOG.

---

## Related

- `orchestrate` — the skill this patch targets
- `ops--handoff` — should be run before any session close that has in-flight agents
- `audit--harness` — next run should verify all three changes are in place
