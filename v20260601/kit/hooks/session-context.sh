#!/usr/bin/env bash
# SessionStart — surface (1) deferred/auth-blocked tasks, (2) tokens needing
# rotation/wiring, and (3) the active project's CLAUDE.md when cwd is under one of
# the configured project_roots. stdout is added to the session context. FAIL-OPEN.
set -uo pipefail
. "$(dirname "$0")/lib.sh"

cwd="$PWD"

# (1) Deferred (auth-blocked) tasks from prior sessions — top priority on return.
defer_n="$(python3 "$HOME/.claude/hooks/deferq.py" count 2>/dev/null || echo 0)"
if [ "${defer_n:-0}" -gt 0 ] 2>/dev/null; then
  echo "## Deferred tasks waiting ($defer_n) — auth/connectivity blocked in a prior session"
  python3 "$HOME/.claude/hooks/deferq.py" list 2>/dev/null
  echo "Load the auth-resilience skill, re-attempt each, and resolve on success (deferq.py resolve <id>). Don't ask the user to re-explain — the queue holds the intent."
  echo ""
fi

# (2) API tokens needing rotation / wiring — security custody, always-on.
tok_n="$(python3 "$HOME/.claude/hooks/tokens.py" due-count 2>/dev/null || echo 0)"
if [ "${tok_n:-0}" -gt 0 ] 2>/dev/null; then
  echo "## Tokens needing attention ($tok_n) — rotation/sync pending"
  python3 "$HOME/.claude/hooks/tokens.py" due 2>/dev/null
  echo "Load the token-rotation skill. Remind the user; keep each token in sync across every target. tokens.py rotate/wired when done."
  echo ""
fi

# (3) Active-project context: if cwd is inside any configured project root, surface
# that project's CLAUDE.md and any open blockers.
roots="$(cfg project_roots)"
[ -z "$roots" ] && exit 0
while IFS= read -r root; do
  [ -z "$root" ] && continue
  root="${root/#\~/$HOME}"
  case "$cwd" in
    "$root"/*)
      rel="${cwd#"$root"/}"
      app="${rel%%/*}"
      appdir="$root/$app"
      echo "## Active project: $app"
      if [ -f "$appdir/CLAUDE.md" ]; then
        echo ""; echo "### $app/CLAUDE.md"; head -c 4000 "$appdir/CLAUDE.md"
      fi
      if [ -f "$appdir/plan/BLOCKERS.md" ]; then
        echo ""; echo "### Open blockers (plan/BLOCKERS.md — first 1500 chars)"; head -c 1500 "$appdir/plan/BLOCKERS.md"
      fi
      break
      ;;
  esac
done <<EOF
$roots
EOF
exit 0
