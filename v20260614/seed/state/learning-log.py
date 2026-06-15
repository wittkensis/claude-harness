#!/usr/bin/env python3
"""learning-log.py — durable log of non-obvious learnings (minimal seed).

When you solve something in a way you'd want to repeat, or hit a mistake you
don't want to make twice, log it here. Append-only, queryable, context-cheap.
Feeds the monthly meta-loop (audit--harness) and "don't repeat mistakes".

DB: ~/.claude/state/learning-log.db (override with $LEARNING_DB)
Model: kind (learning|mistake|decision) · project · tags · text · created

Commands:
  add "<text>" [--kind learning|mistake|decision --project P --tags a,b]
  list [--kind K --project P --tag T --limit N]
  search "<term>" [--limit N]
  export [--out PATH]
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone

DB = os.environ.get("LEARNING_DB", os.path.expanduser("~/.claude/state/learning-log.db"))
KINDS = ["learning", "mistake", "decision"]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB, timeout=5.0)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(
        "CREATE TABLE IF NOT EXISTS entries ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT DEFAULT 'learning',"
        " project TEXT, tags TEXT, text TEXT NOT NULL, created TEXT)"
    )
    con.commit()
    return con


def fmt(r):
    head = f"#{r['id']:>3} [{r['kind']:<8}]"
    if r["project"]:
        head += f" {r['project']}"
    if r["tags"]:
        head += f" ({r['tags']})"
    return f"{head}\n     {r['text']}"


def main(argv):
    p = argparse.ArgumentParser(prog="learning-log.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add"); pa.add_argument("text")
    pa.add_argument("--kind", choices=KINDS, default="learning")
    pa.add_argument("--project"); pa.add_argument("--tags")

    pl = sub.add_parser("list"); pl.add_argument("--kind", choices=KINDS)
    pl.add_argument("--project"); pl.add_argument("--tag"); pl.add_argument("--limit", type=int, default=20)

    pses = sub.add_parser("search"); pses.add_argument("term"); pses.add_argument("--limit", type=int, default=20)

    pe = sub.add_parser("export"); pe.add_argument("--out")

    a = p.parse_args(argv[1:])
    con = connect()
    try:
        if a.cmd == "add":
            cur = con.execute(
                "INSERT INTO entries(kind,project,tags,text,created) VALUES(?,?,?,?,?)",
                (a.kind, a.project, a.tags, a.text, now()))
            con.commit()
            print(f"logged #{cur.lastrowid} ({a.kind})")
        elif a.cmd == "list":
            q = "SELECT * FROM entries WHERE 1=1"; params = []
            if a.kind:
                q += " AND kind=?"; params.append(a.kind)
            if a.project:
                q += " AND project=?"; params.append(a.project)
            if a.tag:
                q += " AND tags LIKE ?"; params.append(f"%{a.tag}%")
            q += " ORDER BY id DESC LIMIT ?"; params.append(a.limit)
            for r in con.execute(q, params).fetchall():
                print(fmt(r))
        elif a.cmd == "search":
            rows = con.execute(
                "SELECT * FROM entries WHERE text LIKE ? OR tags LIKE ?"
                " ORDER BY id DESC LIMIT ?",
                (f"%{a.term}%", f"%{a.term}%", a.limit)).fetchall()
            if not rows:
                print(f"no entries matching '{a.term}'")
            for r in rows:
                print(fmt(r))
        elif a.cmd == "export":
            out = a.out or os.path.expanduser("~/.claude/state/LEARNINGS.md")
            rows = con.execute("SELECT * FROM entries ORDER BY id DESC").fetchall()
            with open(out, "w") as f:
                f.write(f"# Learnings — {now()}\n\n")
                for r in rows:
                    f.write(f"- {fmt(r)}\n")
            print(f"exported {len(rows)} entry(ies) -> {out}")
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
