#!/usr/bin/env bash
# Stop — maintain a mechanical "live state" snapshot every turn so the next session
# never opens from zero, even if ops--handoff was never run. No model, fail-open, fast.
set -uo pipefail

input="$(cat 2>/dev/null || true)"
cwd="$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get("cwd",""))
except Exception:
    print("")' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"

out="$HOME/.claude/state/live-state.md"
mkdir -p "$(dirname "$out")"
{
  echo "# Live state — $(date '+%Y-%m-%d %H:%M')"
  echo "(mechanical snapshot, refreshed every turn by live-state.sh. Prose handoff: last-handoff.md.)"
  echo ""
  echo "- cwd: $cwd"
  if git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
    branch="$(git -C "$cwd" branch --show-current 2>/dev/null)"
    last="$(git -C "$cwd" log --oneline -1 2>/dev/null)"
    echo "- branch: ${branch:-(detached)}"
    echo "- last commit: ${last:-none}"
    dirty="$(git -C "$cwd" status --porcelain 2>/dev/null)"
    if [ -n "$dirty" ]; then
      n="$(printf '%s\n' "$dirty" | grep -c .)"
      echo "- uncommitted: $n file(s)"
      printf '%s\n' "$dirty" | head -10 | sed 's/^/    /'
    else
      echo "- working tree: clean"
    fi
  else
    echo "- git: not a repo"
  fi
  # Backlog top — conditional on backlog.py being installed
  if [ -f "$HOME/.claude/state/backlog.py" ]; then
    bl="$(python3 "$HOME/.claude/state/backlog.py" top --cwd "$cwd" --n 3 2>/dev/null || true)"
    if [ -n "$bl" ]; then
      echo ""
      echo "## Backlog top (this project)"
      echo "$bl"
    fi
  fi
} > "$out" 2>/dev/null

exit 0
