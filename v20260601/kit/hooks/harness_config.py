#!/usr/bin/env python3
"""Loader for ~/.claude/harness.config.json — the single place the portable hooks
read machine-specific values (project roots, protected paths, commit-gate commands,
token registry path, deploy adapter). Importable by Python hooks; also a CLI for
shell hooks.

CLI:  harness_config.py <dotted.key> [default]
      prints the value; a list is printed one item per line; missing -> default.

Fail-soft: any error returns the default / empty so a missing or malformed config
never wedges a hook (the hooks keep their own safe baselines).
"""
import json
import os
import sys

PATH = os.path.expanduser(os.environ.get("HARNESS_CONFIG", "~/.claude/harness.config.json"))


def load():
    try:
        with open(PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def get(dotted, default=None):
    cur = load()
    for k in dotted.split("."):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else ""
    default = sys.argv[2] if len(sys.argv) > 2 else ""
    v = get(key, default)
    if isinstance(v, list):
        print("\n".join(str(x) for x in v))
    elif v is None:
        print(default)
    else:
        print(v)
