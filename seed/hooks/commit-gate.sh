#!/usr/bin/env bash
# PreToolUse(Bash) — quality gate on `git commit`. Blocks (exit 2) the commit if
# the done-gate fails, so steps never stack on a broken foundation.
# Scope: fires on `git commit`; done-check.py decides applicability (JS or Python).
# Bypass: include [wip] or --no-verify in the commit command.
set -uo pipefail

input="$(cat)"
cmd="$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null)"

# Only gate real commits
printf '%s' "$cmd" | grep -Eq 'git +commit' || exit 0
# Explicit bypasses
printf '%s' "$cmd" | grep -Eiq '\[wip\]|--no-verify' && exit 0

cwd="$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print(d.get("cwd",""))
except Exception:
    print("")' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"

# Single source of truth for "done" — language-aware (JS: tsc+test, Python: ruff+pytest).
out="$(python3 "$HOME/.claude/hooks/done-check.py" --dir "$cwd" --quiet 2>&1)"; rc=$?
if [ "$rc" -ne 0 ]; then
  printf 'Commit blocked — done-check failed (add [wip] to bypass):\n%s\n' "$out" >&2
  exit 2
fi
exit 0
