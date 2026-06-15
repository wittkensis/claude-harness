#!/usr/bin/env python3
"""Token rotation registry — tracks API tokens/secrets that must be rotated and
kept in sync across every place they live. METADATA ONLY — never stores VALUES.

Registry path: harness.config.json -> token_registry_path
               (default ~/.claude/token-registry.json)
Target types:  harness.config.json -> token_target_types (informational)
Audit scans:   harness.config.json -> project_roots  (each root's */.env* files)

Entry: {id, name, service, scope, cadence_days, last_rotated, status, targets[], notes}
  targets[] = {type, location, var}
  status (explicit, optional): pending-wiring | needs-review | disabled
          (otherwise derived from last_rotated + cadence_days)

Subcommands: add / list / due / due-count / rotate <id> / wired <id> /
             set-status <id> STATUS / audit / remove <id>
Fail-soft: internal errors print to stderr, exit 0 (never wedge a hook).
"""
import argparse, glob, json, os, re, sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import harness_config as hc
except Exception:
    class hc:  # type: ignore
        @staticmethod
        def get(_k, default=None):
            return default

REG = os.path.expanduser(hc.get("token_registry_path", "~/.claude/token-registry.json"))
WARN = "METADATA ONLY — never store token VALUES here. Values live in .env.local / your CI/secret store / deploy-platform env / the provider console."
DUE_WINDOW = 14  # days before next_due that a token counts as "due"
SECRETISH = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASS|CLIENT_ID|API)$", re.I)


def _roots():
    r = hc.get("project_roots", []) or []
    return [os.path.expanduser(x) for x in r] if isinstance(r, list) else []


def _load():
    if not os.path.isfile(REG):
        return {"_warning": WARN, "tokens": []}
    try:
        d = json.load(open(REG))
        d.setdefault("tokens", [])
        return d
    except Exception:
        return {"_warning": WARN, "tokens": []}


def _save(d):
    d["_warning"] = WARN
    os.makedirs(os.path.dirname(REG), exist_ok=True)
    json.dump(d, open(REG, "w"), indent=2)
    open(REG, "a").write("\n")


def _status(t):
    explicit = t.get("status")
    if explicit in ("pending-wiring", "needs-review", "disabled"):
        return explicit
    lr, cad = t.get("last_rotated"), t.get("cadence_days")
    if not lr or not cad:
        return "needs-review"
    try:
        nd = datetime.strptime(lr, "%Y-%m-%d").date() + timedelta(days=int(cad))
    except Exception:
        return "needs-review"
    today = date.today()
    if nd < today:
        return "overdue"
    if nd - today <= timedelta(days=DUE_WINDOW):
        return "due"
    return "current"


def _actionable(t):
    return _status(t) in ("overdue", "due", "pending-wiring", "needs-review")


def _next_due(t):
    lr, cad = t.get("last_rotated"), t.get("cadence_days")
    if not lr or not cad:
        return "?"
    try:
        return (datetime.strptime(lr, "%Y-%m-%d").date() + timedelta(days=int(cad))).isoformat()
    except Exception:
        return "?"


def _fmt(t):
    tg = ", ".join(f"{x.get('type')}:{x.get('location')}" + (f"[{x['var']}]" if x.get('var') else "") for x in t.get("targets", []))
    line = f"  [{t['id']}] {t['name']} ({t['service']}) — {_status(t).upper()}  next-due {_next_due(t)}"
    if tg:
        line += f"\n           sync: {tg}"
    if t.get("notes"):
        line += f"\n           note: {t['notes']}"
    return line


def _nid(d):
    import uuid
    return uuid.uuid4().hex[:8]


def cmd_add(a):
    d = _load()
    for t in d["tokens"]:
        if t["name"] == a.name and t["service"] == a.service:
            print(t["id"]); return
    targets = []
    for spec in (a.target or []):
        parts = spec.split(":")
        targets.append({"type": parts[0], "location": parts[1] if len(parts) > 1 else "", "var": parts[2] if len(parts) > 2 else a.name})
    t = {"id": _nid(d), "name": a.name, "service": a.service, "scope": a.scope or "",
         "cadence_days": a.cadence_days, "last_rotated": a.last_rotated or "",
         "status": a.status or "", "targets": targets, "notes": a.notes or ""}
    d["tokens"].append(t); _save(d); print(t["id"])


def cmd_list(a):
    d = _load()
    if a.json:
        print(json.dumps([{**t, "derived_status": _status(t), "next_due": _next_due(t)} for t in d["tokens"]], indent=2)); return
    if not d["tokens"]:
        print("Token registry empty. Run: tokens.py audit"); return
    for t in d["tokens"]:
        print(_fmt(t))


def cmd_due(a):
    d = _load()
    act = [t for t in d["tokens"] if _actionable(t)]
    if a.json:
        print(json.dumps([{**t, "derived_status": _status(t)} for t in act], indent=2)); return
    if not act:
        print("No tokens need rotation/wiring."); return
    for t in act:
        print(_fmt(t))


def cmd_due_count(a):
    print(sum(1 for t in _load()["tokens"] if _actionable(t)))


def cmd_rotate(a):
    d = _load(); on = a.on or date.today().isoformat()
    for t in d["tokens"]:
        if t["id"] == a.id:
            t["last_rotated"] = on; t["status"] = "pending-wiring"
            _save(d)
            print(f"{t['name']} rotated {on} -> status PENDING-WIRING. Sync ALL targets, then: tokens.py wired {a.id}")
            for x in t.get("targets", []):
                print(f"  - {x.get('type')}:{x.get('location')}" + (f" [{x['var']}]" if x.get('var') else ""))
            return
    print(f"no token {a.id}")


def cmd_wired(a):
    d = _load()
    for t in d["tokens"]:
        if t["id"] == a.id:
            t["status"] = ""  # derived -> current (clock just reset)
            _save(d); print(f"{t['name']} -> all targets wired, status current"); return
    print(f"no token {a.id}")


def cmd_set_status(a):
    d = _load()
    for t in d["tokens"]:
        if t["id"] == a.id:
            t["status"] = a.status if a.status != "current" else ""
            _save(d); print(f"{t['name']} -> {a.status}"); return
    print(f"no token {a.id}")


def cmd_remove(a):
    d = _load(); n = len(d["tokens"])
    d["tokens"] = [t for t in d["tokens"] if t["id"] != a.id]
    _save(d); print("removed" if len(d["tokens"]) < n else "not found")


def cmd_audit(a):
    """Scan each project root's .env* files for KEY NAMES (never values) and
    register any secret-ish token not already tracked, as needs-review."""
    d = _load()
    roots = _roots()
    if not roots:
        print("audit: no project_roots in harness.config.json — set them first."); return
    known = {(t["name"], t["service"]) for t in d["tokens"]}
    found = {}  # name -> set of env file locations
    for root in roots:
        for envf in glob.glob(os.path.join(root, "*", ".env*")):
            for line in open(envf, errors="ignore"):
                m = re.match(r"\s*([A-Z][A-Z0-9_]+)\s*=", line)
                if m and SECRETISH.search(m.group(1)):
                    found.setdefault(m.group(1), set()).add(envf)
    added = 0
    for name, files in sorted(found.items()):
        app = os.path.basename(os.path.dirname(sorted(files)[0]))
        if (name, app) in known:
            continue
        targets = [{"type": "env", "location": f, "var": name} for f in sorted(files)]
        d["tokens"].append({"id": _nid(d), "name": name, "service": app, "scope": "",
                            "cadence_days": None, "last_rotated": "", "status": "needs-review",
                            "targets": targets, "notes": "discovered by audit — set cadence + last_rotated"})
        added += 1
    _save(d)
    print(f"audit: scanned project .env files; added {added} new token(s) as needs-review. Total tracked: {len(d['tokens'])}")


def main():
    p = argparse.ArgumentParser(); s = p.add_subparsers(dest="cmd", required=True)
    pa = s.add_parser("add"); pa.add_argument("--name", required=True); pa.add_argument("--service", required=True)
    pa.add_argument("--cadence-days", type=int, default=None, dest="cadence_days"); pa.add_argument("--last-rotated", default="", dest="last_rotated")
    pa.add_argument("--target", action="append"); pa.add_argument("--scope", default=""); pa.add_argument("--status", default=""); pa.add_argument("--notes", default="")
    pl = s.add_parser("list"); pl.add_argument("--json", action="store_true")
    pd = s.add_parser("due"); pd.add_argument("--json", action="store_true")
    s.add_parser("due-count")
    pr = s.add_parser("rotate"); pr.add_argument("id"); pr.add_argument("--on", default="")
    pw = s.add_parser("wired"); pw.add_argument("id")
    ps = s.add_parser("set-status"); ps.add_argument("id"); ps.add_argument("status")
    s.add_parser("audit")
    prm = s.add_parser("remove"); prm.add_argument("id")
    a = p.parse_args()
    {"add": cmd_add, "list": cmd_list, "due": cmd_due, "due-count": cmd_due_count,
     "rotate": cmd_rotate, "wired": cmd_wired, "set-status": cmd_set_status,
     "audit": cmd_audit, "remove": cmd_remove}[a.cmd](a)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"tokens.py non-fatal error: {e}", file=sys.stderr); sys.exit(0)
