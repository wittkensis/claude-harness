#!/usr/bin/env python3
"""token_replace.py — substitute {{harness.config.*}} tokens before writing files.

Seed files carry placeholders like `{{harness.config.projects[0].path}}` and
`{{harness.config.user.name}}`. This pass resolves each token against the live
harness.config.json and rewrites the file with real values. Run it on every
seed file as it's written to its destination (BLUEPRINT Step 3).

Token grammar:  {{ harness.config.<dotted.path[with][0].indices> }}
  - dotted keys descend objects: user.name
  - [N] indexes arrays:          projects[0].path
  - whitespace inside {{ }} is tolerated

Usage:
  token_replace.py --config CONFIG FILE ...          rewrites FILEs in place
  token_replace.py --config CONFIG --check FILE ...   report unresolved, no write
  token_replace.py --config CONFIG --stdin            filter stdin -> stdout

Exit: 0 ok · 1 unresolved tokens remain (in --check) · 2 usage/error
"""
import argparse
import json
import os
import re
import sys

TOKEN_RX = re.compile(r"\{\{\s*harness\.config\.([A-Za-z0-9_.\[\]]+)\s*\}\}")
# also tolerate the bare {{harness.config}} root and other {{...}} for the checker
ANY_TOKEN_RX = re.compile(r"\{\{[^}]*\}\}")
SEGMENT_RX = re.compile(r"([A-Za-z0-9_]+)|\[(\d+)\]")


def resolve(config, path):
    """Resolve a dotted/indexed path against config['harness']['config']-style root.

    The token namespace is `harness.config.X`, where the config file's top level
    IS that namespace. So `user.name` -> config['user']['name'].
    Returns (found, value).
    """
    cur = config
    for m in SEGMENT_RX.finditer(path):
        key, idx = m.group(1), m.group(2)
        try:
            if key is not None:
                cur = cur[key]
            else:
                cur = cur[int(idx)]
        except (KeyError, IndexError, TypeError):
            return False, None
    return True, cur


def stringify(val):
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    if val is None:
        return ""
    return str(val)


def substitute(text, config):
    """Return (new_text, unresolved_list)."""
    unresolved = []

    def repl(m):
        found, val = resolve(config, m.group(1))
        if not found or val in (None, "", [], {}):
            unresolved.append(m.group(0))
            return m.group(0)  # leave token in place so --check can catch it
        return stringify(val)

    new_text = TOKEN_RX.sub(repl, text)
    return new_text, unresolved


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    # Drop comment keys so they don't shadow real lookups
    return {k: v for k, v in cfg.items() if not k.startswith("_")}


def main(argv):
    p = argparse.ArgumentParser(prog="token_replace.py")
    p.add_argument("--config", required=True)
    p.add_argument("--check", action="store_true", help="report unresolved, do not write")
    p.add_argument("--stdin", action="store_true", help="filter stdin -> stdout")
    p.add_argument("files", nargs="*")
    a = p.parse_args(argv[1:])

    try:
        config = load_config(a.config)
    except (OSError, json.JSONDecodeError) as e:
        print(f"token_replace: cannot read config {a.config}: {e}", file=sys.stderr)
        return 2

    if a.stdin:
        text = sys.stdin.read()
        new_text, unresolved = substitute(text, config)
        sys.stdout.write(new_text)
        return 1 if unresolved else 0

    if not a.files:
        print("token_replace: no files given", file=sys.stderr)
        return 2

    any_unresolved = False
    for path in a.files:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"  skip {path}: {e}", file=sys.stderr)
            continue
        new_text, unresolved = substitute(text, config)
        # surface ALL remaining {{...}} tokens, not just harness.config ones
        leftover = ANY_TOKEN_RX.findall(new_text)
        if a.check:
            if leftover:
                any_unresolved = True
                print(f"UNRESOLVED in {path}: {sorted(set(leftover))}", file=sys.stderr)
            continue
        if new_text != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
            print(f"substituted: {path}")
        if leftover:
            any_unresolved = True
            print(f"  WARNING unresolved tokens remain in {path}: {sorted(set(leftover))}",
                  file=sys.stderr)

    return 1 if any_unresolved else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
