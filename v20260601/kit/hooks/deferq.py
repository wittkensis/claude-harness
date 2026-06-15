#!/usr/bin/env python3
"""Deferred-task queue — park work blocked by an external roadblock (usually auth),
so it survives the session and a returning agent can auto-resume it.

Store: ~/.claude/state/deferred-tasks.jsonl  (one JSON object per line)
Record: {id, ts, service, task, resume_hint, project, status}

Subcommands:
  add  --service S --task "..." [--resume "..."] [--project PATH]   -> prints id
  list [--json]        open items (human or machine readable)
  count                number of OPEN items (stdout int; exit 0)
  resolve <id...>      mark items resolved
  resolve --all
Fail-soft: any internal error prints to stderr and exits 0 so this never wedges a hook.
"""
import argparse, json, os, sys, time, uuid

STATE = os.path.expanduser("~/.claude/state")
QUEUE = os.path.join(STATE, "deferred-tasks.jsonl")


def _load():
    if not os.path.isfile(QUEUE):
        return []
    out = []
    for line in open(QUEUE):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _save(items):
    os.makedirs(STATE, exist_ok=True)
    with open(QUEUE, "w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")


def cmd_add(a):
    items = _load()
    # de-dupe: same service+task already open -> don't pile up overnight retries
    for it in items:
        if it.get("status") == "open" and it.get("service") == a.service and it.get("task") == a.task:
            print(it["id"])
            return
    rec = {
        "id": uuid.uuid4().hex[:8],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "service": a.service,
        "task": a.task,
        "resume_hint": a.resume or "",
        "project": a.project or os.getcwd(),
        "status": "open",
    }
    items.append(rec)
    _save(items)
    print(rec["id"])


def cmd_list(a):
    items = [it for it in _load() if it.get("status") == "open"]
    if a.json:
        print(json.dumps(items, indent=2))
        return
    if not items:
        print("No deferred tasks.")
        return
    for it in items:
        print(f"  [{it['id']}] {it['service']}: {it['task']}")
        if it.get("resume_hint"):
            print(f"           resume: {it['resume_hint']}")
        if it.get("project"):
            print(f"           project: {it['project']}")


def cmd_count(a):
    print(sum(1 for it in _load() if it.get("status") == "open"))


def cmd_resolve(a):
    items = _load()
    ids = set(a.ids)
    n = 0
    for it in items:
        if it.get("status") == "open" and (a.all or it.get("id") in ids):
            it["status"] = "resolved"
            it["resolved_ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            n += 1
    _save(items)
    print(f"resolved {n}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("add"); pa.add_argument("--service", required=True); pa.add_argument("--task", required=True); pa.add_argument("--resume", default=""); pa.add_argument("--project", default="")
    pl = sub.add_parser("list"); pl.add_argument("--json", action="store_true")
    sub.add_parser("count")
    pr = sub.add_parser("resolve"); pr.add_argument("ids", nargs="*"); pr.add_argument("--all", action="store_true")
    a = p.parse_args()
    {"add": cmd_add, "list": cmd_list, "count": cmd_count, "resolve": cmd_resolve}[a.cmd](a)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"deferq.py non-fatal error: {e}", file=sys.stderr)
        sys.exit(0)
