#!/usr/bin/env bash
# SessionStart — orient every session: surface prior handoff, deferred tasks, backlog, current phase.
# Stdout is added to the session context. FAIL-OPEN.
set -uo pipefail

cwd="$PWD"
hook_input="$(cat)"   # SessionStart event JSON — read once

_ctxfile="$(mktemp 2>/dev/null)" || _ctxfile=""
if [ -n "$_ctxfile" ]; then exec 3>&1 1>"$_ctxfile"; fi

# Prior-session handoff — THE resume point, surfaced first.
# Prose handoff (ops--handoff) is authoritative; live-state.md is the mechanical fallback.
hd="$HOME/.claude/state/last-handoff.md"
ls_file="$HOME/.claude/state/live-state.md"
if [ -f "$hd" ] && [ -s "$hd" ]; then
  echo "## Prior handoff — resume from here (last-handoff.md)"
  head -c 2500 "$hd"
  echo ""
  if [ -f "$ls_file" ] && [ -s "$ls_file" ]; then
    echo "_Mechanical floor for cross-check (live-state.md):_"
    head -c 1000 "$ls_file"
    echo ""
  fi
elif [ -f "$ls_file" ] && [ -s "$ls_file" ]; then
  echo "## No prose handoff — mechanical floor only (live-state.md)"
  echo "_Run \`ops--handoff\` at session end to leave a richer resume point._"
  head -c 1500 "$ls_file"
  echo ""
fi

# Deferred tasks (auth/connectivity blocked in prior sessions)
defer_n="$(python3 "$HOME/.claude/hooks/deferq.py" count 2>/dev/null || echo 0)"
if [ "${defer_n:-0}" -gt 0 ] 2>/dev/null; then
  echo "## Deferred tasks waiting ($defer_n) — auth/connectivity blocked in a prior session"
  python3 "$HOME/.claude/hooks/deferq.py" list 2>/dev/null
  echo "Load the ops--tool-resilience skill, re-attempt each, and resolve on success (deferq.py resolve <id>). Don't ask the user to re-explain — the queue holds the intent."
  echo ""
fi

# Backlog — surface top items for this project
if [ -f "$HOME/.claude/state/backlog.py" ]; then
  bl="$(python3 "$HOME/.claude/state/backlog.py" top --cwd "$cwd" --n 5 2>/dev/null || true)"
  if [ -n "$bl" ]; then
    echo "$bl"
    echo "Source of truth for \"what's next\". Capture with \`backlog.py add\`; proactively offer to log future tasks. Skill: ops--backlog."
    echo ""
  fi
fi

# Phase-aware skill surfacing — pulls from SKILLS.md so this never duplicates the routing index
phase_file="$HOME/.claude/state/phase"
phase="$(cat "$phase_file" 2>/dev/null || true)"
if [ -n "$phase" ]; then
  echo "## Current phase: $phase"
  echo "(confirm or advance: \`echo <Clarify|Design|Build|Verify|Iterate> > ~/.claude/state/phase\`)"
  row="$(grep -iE "\*\*[[:space:]]*$phase" "$HOME/.claude/SKILLS.md" 2>/dev/null | head -1)"
  if [ -n "$row" ]; then
    skills="$(printf '%s' "$row" | awk -F'|' '{print $3}' | sed 's/^ *//;s/ *$//')"
    agents="$(printf '%s' "$row" | awk -F'|' '{print $4}' | sed 's/^ *//;s/ *$//')"
    [ -n "$skills" ] && echo "Skills for this phase: $skills"
    [ -n "$agents" ] && echo "Agents (spawn, separate context): $agents"
  fi
  echo "Agent vs inline: spawn an agent only for separate-context work (research, parallel build, QA, post-deploy) or when the user names one — otherwise work inline."
  echo ""
fi

# Project root resolver — if cwd has no CLAUDE.md but a child does, surface it
if [ ! -f "$cwd/CLAUDE.md" ]; then
  kids="$(find "$cwd" -mindepth 1 -maxdepth 2 -name CLAUDE.md \
    -not -path '*/node_modules/*' -not -path '*/venv/*' -not -path '*/.git/*' 2>/dev/null)"
  n="$(printf '%s\n' "$kids" | grep -c . 2>/dev/null || echo 0)"
  if [ "${n:-0}" -eq 1 ]; then
    real="$(dirname "$kids")"
    relsub="${real#"$cwd"/}"
    echo "## Project root is in ./$relsub"
    echo "Its CLAUDE.md is authoritative. cd into ./$relsub for code and orientation."
    echo ""
    echo "### $relsub/CLAUDE.md (first 2500 chars)"
    head -c 2500 "$kids"
    echo ""
  fi
fi

# Session orientation — fires last, frames the session
echo ""
echo "## Session orientation"
echo "Follow the \`ops--session-start\` skill now: check for a prior handoff, orient to the project, surface relevant goals, declare session intent. Keep the output to 4-6 lines."

# Auto-title
if [ -z "${_ctxfile:-}" ]; then exit 0; fi
exec 1>&3 3>&-
ctx="$(cat "$_ctxfile" 2>/dev/null)"; rm -f "$_ctxfile" 2>/dev/null
phase="$(cat "$HOME/.claude/state/phase" 2>/dev/null || true)"

if out="$(CTX="$ctx" CWD="$cwd" PHASE="$phase" HOOK_INPUT="$hook_input" \
          python3 "$HOME/.claude/hooks/session-title.py" 2>/dev/null)" && [ -n "$out" ]; then
  printf '%s\n' "$out"
else
  printf '%s' "$ctx"
fi
exit 0
