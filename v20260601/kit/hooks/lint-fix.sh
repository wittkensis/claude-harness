#!/usr/bin/env bash
# PostToolUse(Edit|Write|MultiEdit) — fast, per-file style fix. FAIL-OPEN: never
# blocks work. Heavy typecheck/tests run at the commit gate, not here.
# Stack-agnostic: a config template (lint_fix.command with {file}) wins; else
# auto-detects eslint (JS/TS), ruff/black (py), rustfmt (rs), gofmt (go).
set -uo pipefail
. "$(dirname "$0")/lib.sh"

input="$(cat)"
file="$(printf '%s' "$input" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))
except Exception: print("")' 2>/dev/null)"
[ -z "$file" ] && exit 0
[ -f "$file" ] || exit 0

tmpl="$(cfg lint_fix.command)"
if [ -n "$tmpl" ]; then
  ( TO 30 sh -c "${tmpl//\{file\}/$file}" >/dev/null 2>&1 )
  exit 0
fi

case "$file" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs)
    root="$(find_root "$(dirname "$file")" package.json)" || exit 0
    [ -x "$root/node_modules/.bin/eslint" ] && \
      ( cd "$root" && TO 30 ./node_modules/.bin/eslint --fix "$file" >/dev/null 2>&1 )
    ;;
  *.py)
    if command -v ruff >/dev/null 2>&1; then ( TO 30 ruff check --fix "$file" >/dev/null 2>&1; TO 30 ruff format "$file" >/dev/null 2>&1 )
    elif command -v black >/dev/null 2>&1; then ( TO 30 black -q "$file" >/dev/null 2>&1 )
    fi
    ;;
  *.rs) command -v rustfmt >/dev/null 2>&1 && ( TO 30 rustfmt "$file" >/dev/null 2>&1 ) ;;
  *.go) command -v gofmt   >/dev/null 2>&1 && ( TO 30 gofmt -w "$file" >/dev/null 2>&1 ) ;;
esac
exit 0
