#!/usr/bin/env python3
"""backlog.py — the cross-project work queue (minimal seed implementation).

The single source of truth for "what's next" across every project. SQLite-backed
so it never inflates context: queries return only the rows asked for. This is the
self-contained seed copy — enough to be useful on a fresh install. Grow it in
place; the ops--backlog skill documents the intended full surface.

DB: ~/.claude/state/backlog.db (override with $BACKLOG_DB)
Model:
  project  enum row (name, category, local_path, repo_url)
  type     feature|improvement|bug|chore|research|design|docs|experiment
  status   inbox -> todo -> doing -> blocked -> done -> dropped
  score    Impact(1-5) / Effort  (effort from size xs1 s2 m3 l5 xl8); higher = sooner

Commands:
  add <project> "<title>" [--type T --impact N --size SZ --body "..." --github URL]
  triage <id> --impact N --size SZ [--type T]
  top [--project P | --category C | --all] [--n 5]
  list [--project P --status S --type T --limit N]
  show <id>
  claim [<id> | --project P] [--owner ID]
  start|done|drop <id>
  block <id> [--note "..."]
  set <id> [--impact N --size SZ --type T --github URL]
  project add|set|list <name> [--category C --path PATH --repo URL]
  export [--out PATH]
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone

DB = os.environ.get("BACKLOG_DB", os.path.expanduser("~/.claude/state/backlog.db"))
SIZES = {"xs": 1, "s": 2, "m": 3, "l": 5, "xl": 8}
TYPES = ["feature", "improvement", "bug", "chore", "research", "design", "docs", "experiment"]
CATEGORIES = ["app", "system", "hobby", "learning"]
STATUSES = ["inbox", "todo", "doing", "blocked", "done", "dropped"]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB, timeout=5.0)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY, category TEXT, local_path TEXT, repo_url TEXT
        );
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL, title TEXT NOT NULL, body TEXT DEFAULT '',
            type TEXT DEFAULT 'feature', status TEXT DEFAULT 'inbox',
            impact INTEGER, size TEXT, score REAL,
            owner TEXT, github_url TEXT, note TEXT,
            created TEXT, updated TEXT
        );
        """
    )
    con.commit()
    return con


def compute_score(impact, size):
    if impact is None or not size:
        return None
    eff = SIZES.get(size.lower())
    return round(impact / eff, 3) if eff else None


def ensure_project(con, name):
    if not con.execute("SELECT 1 FROM projects WHERE name=?", (name,)).fetchone():
        con.execute(
            "INSERT INTO projects(name,category) VALUES(?,?)", (name, "app")
        )


def fmt(row):
    s = f"#{row['id']:>3} [{row['status']:<7}] {row['type']:<11} "
    if row["score"] is not None:
        s += f"score {row['score']:<5} "
    s += f"{row['project']}: {row['title']}"
    return s


def cmd_add(con, a):
    ensure_project(con, a.project)
    score = compute_score(a.impact, a.size)
    status = "todo" if score is not None else "inbox"
    cur = con.execute(
        "INSERT INTO items(project,title,body,type,status,impact,size,score,github_url,created,updated)"
        " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (a.project, a.title, a.body or "", a.type, status, a.impact, a.size, score,
         a.github, now(), now()),
    )
    con.commit()
    print(f"added #{cur.lastrowid} ({status})")


def cmd_triage(con, a):
    score = compute_score(a.impact, a.size)
    fields = {"impact": a.impact, "size": a.size, "score": score, "status": "todo",
              "updated": now()}
    if a.type:
        fields["type"] = a.type
    _update(con, a.id, fields)
    print(f"triaged #{a.id} -> todo (score {score})")


def cmd_top(con, a):
    q = "SELECT * FROM items WHERE status IN ('todo','doing')"
    params = []
    if a.project:
        q += " AND project=?"; params.append(a.project)
    elif a.category:
        q += " AND project IN (SELECT name FROM projects WHERE category=?)"; params.append(a.category)
    q += " ORDER BY (score IS NULL), score DESC, id ASC LIMIT ?"
    params.append(a.n)
    rows = con.execute(q, params).fetchall()
    if not rows:
        print("backlog empty (nothing ranked todo/doing)"); return
    for r in rows:
        print(fmt(r))


def cmd_list(con, a):
    q = "SELECT * FROM items WHERE 1=1"
    params = []
    for col, val in (("project", a.project), ("status", a.status), ("type", a.type)):
        if val:
            q += f" AND {col}=?"; params.append(val)
    q += " ORDER BY id DESC LIMIT ?"
    params.append(a.limit)
    for r in con.execute(q, params).fetchall():
        print(fmt(r))


def cmd_show(con, a):
    r = con.execute("SELECT * FROM items WHERE id=?", (a.id,)).fetchone()
    if not r:
        print(f"no item #{a.id}", file=sys.stderr); sys.exit(1)
    for k in r.keys():
        if r[k] not in (None, ""):
            print(f"{k:>10}: {r[k]}")


def cmd_claim(con, a):
    con.execute("BEGIN IMMEDIATE")
    q = "SELECT * FROM items WHERE status='todo'"
    params = []
    if a.id:
        q += " AND id=?"; params.append(a.id)
    elif a.project:
        q += " AND project=?"; params.append(a.project)
    q += " ORDER BY (score IS NULL), score DESC, id ASC LIMIT 1"
    r = con.execute(q, params).fetchone()
    if not r:
        con.rollback(); print("nothing claimable", file=sys.stderr); sys.exit(1)
    con.execute("UPDATE items SET status='doing',owner=?,updated=? WHERE id=?",
                (a.owner or "agent", now(), r["id"]))
    con.commit()
    print(f"claimed #{r['id']}: {r['title']}")


def _update(con, item_id, fields):
    if not con.execute("SELECT 1 FROM items WHERE id=?", (item_id,)).fetchone():
        print(f"no item #{item_id}", file=sys.stderr); sys.exit(1)
    cols = ", ".join(f"{k}=?" for k in fields)
    con.execute(f"UPDATE items SET {cols} WHERE id=?", (*fields.values(), item_id))
    con.commit()


def cmd_status(con, a, status):
    _update(con, a.id, {"status": status, "updated": now()})
    print(f"#{a.id} -> {status}")


def cmd_block(con, a):
    _update(con, a.id, {"status": "blocked", "note": a.note or "", "updated": now()})
    print(f"#{a.id} -> blocked")


def cmd_set(con, a):
    fields = {"updated": now()}
    if a.impact is not None:
        fields["impact"] = a.impact
    if a.size:
        fields["size"] = a.size
    if a.type:
        fields["type"] = a.type
    if a.github:
        fields["github_url"] = a.github
    if "impact" in fields or "size" in fields:
        r = con.execute("SELECT impact,size FROM items WHERE id=?", (a.id,)).fetchone()
        imp = fields.get("impact", r["impact"] if r else None)
        sz = fields.get("size", r["size"] if r else None)
        fields["score"] = compute_score(imp, sz)
    _update(con, a.id, fields)
    print(f"updated #{a.id}")


def cmd_project(con, a):
    if a.action == "list":
        for r in con.execute("SELECT * FROM projects ORDER BY name").fetchall():
            print(f"{r['name']:<24} {r['category'] or '-':<10} {r['local_path'] or ''}")
        return
    name = a.name
    if not name:
        print("project name required", file=sys.stderr); sys.exit(1)
    if a.action == "add":
        con.execute(
            "INSERT OR IGNORE INTO projects(name,category,local_path,repo_url) VALUES(?,?,?,?)",
            (name, a.category or "app", a.path, a.repo))
    else:  # set
        for col, val in (("category", a.category), ("local_path", a.path), ("repo_url", a.repo)):
            if val is not None:
                con.execute(f"UPDATE projects SET {col}=? WHERE name=?", (val, name))
    con.commit()
    print(f"project {a.action}: {name}")


def cmd_export(con, a):
    out = a.out or os.path.expanduser("~/.claude/state/BACKLOG.md")
    rows = con.execute(
        "SELECT * FROM items WHERE status NOT IN ('done','dropped')"
        " ORDER BY (score IS NULL), score DESC, id ASC").fetchall()
    lines = [f"# Backlog — {now()}", ""]
    for r in rows:
        lines.append(f"- {fmt(r)}")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"exported {len(rows)} item(s) -> {out}")


def build_parser():
    p = argparse.ArgumentParser(prog="backlog.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add"); pa.add_argument("project"); pa.add_argument("title")
    pa.add_argument("--type", choices=TYPES, default="feature")
    pa.add_argument("--impact", type=int); pa.add_argument("--size", choices=SIZES)
    pa.add_argument("--body"); pa.add_argument("--github")

    pt = sub.add_parser("triage"); pt.add_argument("id", type=int)
    pt.add_argument("--impact", type=int, required=True)
    pt.add_argument("--size", choices=SIZES, required=True)
    pt.add_argument("--type", choices=TYPES)

    ptop = sub.add_parser("top"); g = ptop.add_mutually_exclusive_group()
    g.add_argument("--project"); g.add_argument("--category", choices=CATEGORIES)
    g.add_argument("--all", action="store_true"); ptop.add_argument("--n", type=int, default=5)

    pl = sub.add_parser("list"); pl.add_argument("--project"); pl.add_argument("--status", choices=STATUSES)
    pl.add_argument("--type", choices=TYPES); pl.add_argument("--limit", type=int, default=20)

    sub.add_parser("show").add_argument("id", type=int)

    pc = sub.add_parser("claim"); pc.add_argument("id", type=int, nargs="?")
    pc.add_argument("--project"); pc.add_argument("--owner")

    for s in ("start", "done", "drop"):
        sub.add_parser(s).add_argument("id", type=int)

    pb = sub.add_parser("block"); pb.add_argument("id", type=int); pb.add_argument("--note")

    ps = sub.add_parser("set"); ps.add_argument("id", type=int)
    ps.add_argument("--impact", type=int); ps.add_argument("--size", choices=SIZES)
    ps.add_argument("--type", choices=TYPES); ps.add_argument("--github")

    pp = sub.add_parser("project"); pp.add_argument("action", choices=["add", "set", "list"])
    pp.add_argument("name", nargs="?"); pp.add_argument("--category", choices=CATEGORIES)
    pp.add_argument("--path"); pp.add_argument("--repo")

    pe = sub.add_parser("export"); pe.add_argument("--out")
    return p


STATUS_MAP = {"start": "doing", "done": "done", "drop": "dropped"}


def main(argv):
    args = build_parser().parse_args(argv[1:])
    con = connect()
    try:
        if args.cmd == "add":
            cmd_add(con, args)
        elif args.cmd == "triage":
            cmd_triage(con, args)
        elif args.cmd == "top":
            cmd_top(con, args)
        elif args.cmd == "list":
            cmd_list(con, args)
        elif args.cmd == "show":
            cmd_show(con, args)
        elif args.cmd == "claim":
            cmd_claim(con, args)
        elif args.cmd in STATUS_MAP:
            cmd_status(con, args, STATUS_MAP[args.cmd])
        elif args.cmd == "block":
            cmd_block(con, args)
        elif args.cmd == "set":
            cmd_set(con, args)
        elif args.cmd == "project":
            cmd_project(con, args)
        elif args.cmd == "export":
            cmd_export(con, args)
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
