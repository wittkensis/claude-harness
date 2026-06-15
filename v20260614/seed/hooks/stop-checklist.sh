#!/usr/bin/env bash
# Stop — assert the done-gate, then print the completion checklist.
# Binds (exit 2, sends the model back) ONLY when: cwd is a JS/Python project AND it has
# uncommitted changes AND done-check.py fails — i.e. "stopping with broken work claimed done."
# Harness/no-project contexts never block (done-check returns 0). Escape: `touch ~/.claude/state/done-skip`.
set -uo pipefail

input="$(cat 2>/dev/null || true)"
cwd="$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print(d.get("cwd",""))
except Exception:
    print("")' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"

skip="$HOME/.claude/state/done-skip"

# Only assert when there is uncommitted work to be wrong about.
dirty=""
if git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
  [ -n "$(git -C "$cwd" status --porcelain 2>/dev/null)" ] && dirty=1
fi

if [ -n "$dirty" ]; then
  out="$(python3 "$HOME/.claude/hooks/done-check.py" --dir "$cwd" --quiet 2>&1)"; rc=$?
  if [ "$rc" -ne 0 ]; then
    if [ -f "$skip" ]; then
      rm -f "$skip"
      echo "⚠ done-check failed but done-skip was set — allowing stop. Reasons:" >&2
      echo "$out" >&2
    else
      {
        echo "⛔ PREMATURE DONE — done-check failed on uncommitted work:"
        echo "$out"
        echo ""
        echo "Fix it, OR if this is genuinely fine to leave: \`touch ~/.claude/state/done-skip\` then stop."
      } >&2
      exit 2
    fi
  fi
fi

cat <<'EOF'
Completion check (two-step gate):
  1) typecheck clean?  2) tests run & passing?  3) intent validated via verify/run (not just "it compiled")?
If any is no and the task is reported done, that's premature victory — go back.

If the task IS done: close with 1–3 next steps toward the goal, each naming the skill/agent that advances it (see SKILLS.md phase→skill map). Don't end on a dead stop.

Long session or mid-task with more to do? Run `ops--handoff` to capture context for the next session.
EOF
exit 0
