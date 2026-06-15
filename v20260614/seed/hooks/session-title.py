#!/usr/bin/env python3
"""Emit SessionStart hookSpecificOutput JSON — wrap the context banner + set sessionTitle.

Called by session-context.sh. Reads the SessionStart event JSON on stdin (for `source` and any
existing `session_title`); takes the captured banner + cwd + phase from the environment. Sets the
title to "<project> · <phase>" so parallel sessions are legible in the picker / `claude --resume`.

`sessionTitle` is a shipped SessionStart field (code.claude.com/docs/en/hooks) — same effect as
`/rename`, ignored on source clear/compact. We additionally avoid clobbering a title that already
exists on resume. FAIL-OPEN: on any error the caller falls back to printing the plain banner.
"""
import json, os, sys, re

def project_name(cwd: str) -> str:
    home = os.path.expanduser("~")
    # Named roots — add your own project shortcuts here
    roots = {
        f"{home}/.claude": "harness",
    }
    # Load extra project roots from harness.config.json
    try:
        import json as _json
        config = _json.loads(open(f"{home}/.claude/harness.config.json").read())
        for proj in config.get("projects", []):
            if proj.get("path") and proj.get("name"):
                roots[os.path.expanduser(proj["path"])] = proj["name"]
    except Exception:
        pass
    for root, name in roots.items():
        if cwd == root or cwd.startswith(root + "/"):
            return name
    return os.path.basename(cwd.rstrip("/")) or "session"

def main() -> int:
    # The banner is built with byte-wise `head -c`, which can split a multibyte UTF-8 char and
    # leave an invalid byte (→ a lone surrogate via os.environ's surrogateescape). Scrub those to
    # U+FFFD so the emitted JSON never carries an unpaired surrogate a strict parser would reject.
    ctx = os.environ.get("CTX", "").encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    cwd = os.environ.get("CWD") or os.getcwd()
    phase = (os.environ.get("PHASE") or "").strip()
    try:
        ev = json.loads(os.environ.get("HOOK_INPUT") or "{}")
    except Exception:
        ev = {}
    source = ev.get("source", "")
    existing = (ev.get("session_title") or "").strip()

    proj = project_name(cwd)
    title = f"{proj} · {phase}" if phase else proj

    spec = {"hookEventName": "SessionStart", "additionalContext": ctx}
    # Name on a fresh start, or on resume only if nothing's set — never clobber a
    # title the user (or a prior start) already chose.
    if source == "startup" or (source == "resume" and not existing):
        spec["sessionTitle"] = title

    sys.stdout.write(json.dumps({"hookSpecificOutput": spec}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
