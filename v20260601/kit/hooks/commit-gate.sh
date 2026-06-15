#!/usr/bin/env bash
# PreToolUse(Bash) — quality gate on `git commit`. Blocks (exit 2) if typecheck or
# tests fail, so steps never stack on a broken foundation.
# Stack-agnostic: auto-detects JS/TS, Python, Rust, or Go by project markers, or
# uses explicit commands from harness.config.json (commit_gate.typecheck / .test).
# Bypass: include [wip] or --no-verify in the commit command.
set -uo pipefail
. "$(dirname "$0")/lib.sh"

input="$(cat)"
cmd="$(printf '%s' "$input" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null)"

printf '%s' "$cmd" | grep -Eq 'git +commit' || exit 0
printf '%s' "$cmd" | grep -Eiq '\[wip\]|--no-verify' && exit 0

cwd="$(printf '%s' "$input" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("cwd",""))
except Exception: print("")' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"

# Explicit overrides win
cfg_tc="$(cfg commit_gate.typecheck)"
cfg_test="$(cfg commit_gate.test)"

# Find a project root by any known marker
root="$(find_root "$cwd" package.json pyproject.toml setup.py Cargo.toml go.mod)" || exit 0
cd "$root" || exit 0
fail=""

run() {  # run <label> <logfile> <cmd...>
  local label="$1" log="$2"; shift 2
  if ! TO 300 "$@" >"$log" 2>&1; then
    fail="${fail}\n— ${label} failed. See ${log}"
  fi
}

if [ -n "$cfg_tc" ] || [ -n "$cfg_test" ]; then
  # Config-driven commands (run via sh -c so the user can write a pipeline)
  [ -n "$cfg_tc" ]   && run "typecheck" /tmp/harness-gate-tc.log   sh -c "$cfg_tc"
  [ -n "$cfg_test" ] && run "tests"     /tmp/harness-gate-test.log sh -c "$cfg_test"
elif [ -f package.json ]; then
  [ -x node_modules/.bin/tsc ] && [ -f tsconfig.json ] && \
    run "typecheck" /tmp/harness-gate-tc.log ./node_modules/.bin/tsc --noEmit
  node -e 'process.exit(require("./package.json").scripts?.test?0:1)' 2>/dev/null && \
    run "tests" /tmp/harness-gate-test.log npm test --silent
elif [ -f Cargo.toml ]; then
  command -v cargo >/dev/null 2>&1 && {
    run "typecheck" /tmp/harness-gate-tc.log cargo check --quiet
    run "tests"     /tmp/harness-gate-test.log cargo test --quiet
  }
elif [ -f go.mod ]; then
  command -v go >/dev/null 2>&1 && {
    run "vet"   /tmp/harness-gate-tc.log   go vet ./...
    run "tests" /tmp/harness-gate-test.log go test ./...
  }
elif [ -f pyproject.toml ] || [ -f setup.py ]; then
  # Typecheck: prefer mypy/pyright if available; tests: pytest if available
  if command -v mypy >/dev/null 2>&1; then run "typecheck" /tmp/harness-gate-tc.log mypy .
  elif command -v pyright >/dev/null 2>&1; then run "typecheck" /tmp/harness-gate-tc.log pyright
  fi
  command -v pytest >/dev/null 2>&1 && run "tests" /tmp/harness-gate-test.log pytest -q
fi

if [ -n "$fail" ]; then
  printf 'Commit blocked — fix before committing (or add [wip] to bypass):%b\n' "$fail" >&2
  exit 2
fi
exit 0
