#!/usr/bin/env python3
"""doc-reminder — PreToolUse(Edit|Write|MultiEdit) hook.

Whenever a documentation file is created or updated (CLAUDE.md, README, CHANGELOG, LEARNINGS,
BLOCKERS, CONTRIBUTING, ADRs, or anything under a docs/ dir), inject a reminder to apply the
`write--documentation` skill — so doc files get the right content in the right place every time,
not just when the model happens to semantically route to the skill.

Skips harness skill/agent files (those are owned by build--skill-authoring, not write--documentation).
Fail-open: any parse problem → emit nothing, exit 0. Never blocks a write.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import PurePosixPath


def is_doc(path: str) -> bool:
    if not path:
        return False
    p = path.replace("\\", "/")
    # Don't fire on skill/agent authoring surfaces — those route to build--skill-authoring.
    if "/.claude/skills/" in p or "/.claude/agents/" in p:
        return False
    name = PurePosixPath(p).name
    lname = name.lower()
    DOC_NAMES = ("claude.md", "readme", "changelog", "learnings", "blockers", "contributing")
    if lname.startswith(DOC_NAMES):
        return True
    if re.match(r"adr[-_]", lname) and lname.endswith(".md"):
        return True
    # docs/ directory markdown
    if "/docs/" in p.lower() and lname.endswith(".md"):
        return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    ti = data.get("tool_input", {}) or {}
    # Write/Edit use file_path; be liberal about the field name.
    path = ti.get("file_path") or ti.get("path") or ti.get("notebook_path") or ""
    if not is_doc(path):
        return 0

    name = PurePosixPath(path.replace("\\", "/")).name
    msg = (
        f"Editing a documentation file ({name}). Apply the **write--documentation** skill: "
        "write for the next person who needs to act; put content where it belongs "
        "(README = what/how-to-run · CLAUDE.md = how to work in THIS repo · CHANGELOG/LEARNINGS/ADR per their template); "
        "cut anything time-sensitive or redundant. Templates live in the skill's folder."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": msg,
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
