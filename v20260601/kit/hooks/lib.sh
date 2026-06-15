# Shared shell-hook library — source this at the top of every *.sh hook:
#   . "$(dirname "$0")/lib.sh"
#
# Provides:
#   TO <secs> <cmd...>   portable timeout (uses timeout/gtimeout if present, else
#                        runs unbounded — stock macOS ships NEITHER, and assuming
#                        `timeout` exists silently turns every wrapped step into a
#                        "command not found" failure. This shim is load-bearing).
#   cfg <dotted.key> [default]   read a value from ~/.claude/harness.config.json.

if command -v timeout >/dev/null 2>&1; then TO() { timeout "$@"; }
elif command -v gtimeout >/dev/null 2>&1; then TO() { gtimeout "$@"; }
else TO() { shift; "$@"; }   # drop the duration arg, run unbounded
fi

cfg() { python3 "$HOME/.claude/hooks/harness_config.py" "$1" "${2:-}" 2>/dev/null; }

# Walk up from $1 to the nearest dir containing any of the marker files in $2..$N.
# Prints the dir, or nothing. e.g. find_root "$cwd" package.json pyproject.toml
find_root() {
  local dir="$1"; shift
  while [ "$dir" != "/" ] && [ -n "$dir" ]; do
    for marker in "$@"; do
      [ -e "$dir/$marker" ] && { printf '%s' "$dir"; return 0; }
    done
    dir="$(dirname "$dir")"
  done
  return 1
}
