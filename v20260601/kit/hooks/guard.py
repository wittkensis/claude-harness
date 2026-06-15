#!/usr/bin/env python3
"""PreToolUse guard — fail-closed protection for the harness (portable).

Universal baseline (always on, no config needed):
  - Block Edit/Write to a real .env file (allows .env.example/.sample/.template/.local).
  - Block broad `rm -rf` on /, ~, $HOME, * at a command position.
  - Block `git push --force` (without --force-with-lease) to main/master.

Config-driven (from ~/.claude/harness.config.json — empty by default):
  - protected_globs[]   : paths that are immutable; any Edit/Write or write-ish Bash
                          (>, >>, rm/mv/cp/tee/truncate, sed -i) targeting them is blocked.
  - secret_file_globs[] : extra filename globs to treat like a real secret file.

Reads hook JSON on stdin: { tool_name, tool_input, cwd, ... }.
Exit 0 = allow, exit 2 = block (stderr shown to Claude). Fails OPEN on its own errors.
"""
import fnmatch
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import harness_config as hc
except Exception:  # never let a missing helper wedge the guard
    class hc:  # type: ignore
        @staticmethod
        def get(_k, default=None):
            return default


def block(reason: str) -> None:
    print(f"BLOCKED by guard.py: {reason}", file=sys.stderr)
    sys.exit(2)


def _globs(key):
    v = hc.get(key, []) or []
    return [os.path.expanduser(g) for g in v] if isinstance(v, list) else []


def _matches(path, globs):
    return any(fnmatch.fnmatch(path, g) or fnmatch.fnmatch(path, g.rstrip("/") + "/*") for g in globs)


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        return
    data = json.loads(raw)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}

    protected = _globs("protected_globs")
    secret_globs = _globs("secret_file_globs")

    # --- file-writing tools ---
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        ap = os.path.abspath(os.path.expanduser(path)) if path else ""
        if ap and protected and _matches(ap, protected):
            block(f"'{path}' is in a protected/immutable path (harness.config.json "
                  "protected_globs). Refusing to modify it.")
        base = os.path.basename(ap)
        # Universal: block a real .env; allow committed templates + gitignored *.local
        is_env = re.fullmatch(r"\.env(\..+)?", base) and not base.endswith(
            (".example", ".sample", ".template", ".local"))
        if is_env or (secret_globs and _matches(ap, secret_globs)):
            block(f"Refusing to edit '{base}'. Real secrets belong in .env.local "
                  "(gitignored) / your secret store — not a possibly-tracked file. "
                  "Use .env.local and the token-rotation skill.")
        return

    # --- bash ---
    if tool == "Bash":
        cmd = ti.get("command", "") or ""
        # write-ish bash targeting a protected path
        for g in protected:
            name = os.path.basename(g.rstrip("/*")) or g
            if g in cmd or name in cmd:
                if re.search(
                    r"(?:>>?\s*\S*%s|\b(?:rm|mv|cp|tee|truncate)\b[^|]*%s|sed\s+-i[^|]*%s)"
                    % (re.escape(name), re.escape(name), re.escape(name)), cmd):
                    block(f"Bash command writes to a protected path ({g}).")
        # broad rm -rf only at a command position (not inside an echo/string)
        if re.search(r"(?:^|[;&|]|&&|\|\|)\s*rm\s+-rf?\s+(?:/|~|\$HOME|\*)(?:\s|/|$)", cmd):
            block("Refusing broad `rm -rf` on /, ~, $HOME, or *. Narrow the path.")
        if re.search(r"git\s+push\s+.*--force(?!-with-lease)", cmd) and re.search(r"\bmain\b|\bmaster\b", cmd):
            block("Force-push to main/master blocked. Use --force-with-lease and confirm with the user.")
        return


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail open — never wedge the session on a guard bug
        print(f"guard.py non-fatal error (allowing): {e}", file=sys.stderr)
        sys.exit(0)
