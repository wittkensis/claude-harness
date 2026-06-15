#!/usr/bin/env python3
"""PreToolUse guard — fail-closed protection for the harness.

Blocks (exit 2):
  - Any Edit/Write/MultiEdit to paths listed in harness.config.protected_paths (immutable dirs)
  - Any Edit/Write/MultiEdit to a real .env file (allows .env.local / .env.example / .env.sample)
  - Live API tokens written into tracked files (the committed-token leak class)
  - Bash commands that do `rm -rf` on broad paths or `git push --force` to main

Config: ~/.claude/harness.config.json → protected_paths (list of absolute paths)
Fails OPEN on its own errors so a bug here never wedges the session.
"""
import json
import os
import re
import sys


def block(reason: str) -> None:
    print(f"BLOCKED by guard.py: {reason}", file=sys.stderr)
    sys.exit(2)


def load_protected_paths() -> list[str]:
    config_path = os.path.expanduser("~/.claude/harness.config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
        return [os.path.expanduser(p) for p in config.get("protected_paths", [])]
    except Exception:
        return []


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        return
    data = json.loads(raw)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}

    protected_paths = load_protected_paths()

    # --- file-writing tools ---
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        ap = os.path.abspath(os.path.expanduser(path)) if path else ""

        # Block writes to any protected path from config
        for prot in protected_paths:
            prot_norm = prot.rstrip("/") + os.sep
            if ap and (ap.startswith(prot_norm) or ap == prot.rstrip("/")):
                block(f"{prot} is protected (harness.config.protected_paths). "
                      "Add an exception in harness.config.json if intentional.")

        base = os.path.basename(ap)
        # Block bare .env files; allow .env.local, .env.example, .env.sample, .env.template
        if (re.fullmatch(r"\.env(\..+)?", base)
                and not base.endswith((".example", ".sample", ".template", ".local"))):
            block(f"Refusing to edit '{base}'. Real secrets belong in .env.local "
                  "(gitignored) or your secrets manager — not a possibly-tracked .env. "
                  "Use .env.local for local dev.")

        # Block live API tokens in tracked files (committed-token leak prevention)
        if not base.endswith((".local", ".example", ".sample", ".template")):
            if tool == "Write":
                blob = ti.get("content", "") or ""
            elif tool == "Edit":
                blob = ti.get("new_string", "") or ""
            elif tool == "MultiEdit":
                blob = "\n".join((e or {}).get("new_string", "") for e in (ti.get("edits") or []))
            else:
                blob = ""
            if re.search(r"\b\d+\|[A-Za-z0-9]{30,}\b", blob):
                block("Refusing to write a live API token into a tracked file. "
                      "Use an environment variable and read it from .env.local at runtime.")
        return

    # --- bash ---
    if tool == "Bash":
        cmd = ti.get("command", "") or ""
        # Block broad rm -rf at root paths
        if re.search(r"(?:^|[;&|]|&&|\|\|)\s*rm\s+-rf?\s+(?:/|~|\$HOME|\*)(?:\s|/|$)", cmd):
            block("Refusing broad `rm -rf` on /, ~, $HOME, or *. Narrow the path.")
        # Block force-push to main/master
        if re.search(r"git\s+push\s+.*--force(?!-with-lease)", cmd) and re.search(r"\bmain\b|\bmaster\b", cmd):
            block("Force-push to main/master blocked. Use --force-with-lease and confirm with the user.")
        return


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"guard.py non-fatal error (allowing): {e}", file=sys.stderr)
        sys.exit(0)
