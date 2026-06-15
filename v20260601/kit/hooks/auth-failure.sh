#!/usr/bin/env bash
# PostToolUseFailure — best-effort catcher for AUTH/connectivity failures on
# external tools (MCP servers, gh, git remote, any API). When a tool fails because
# of auth/timeout (not a logic error), park the work in the deferred queue and tell
# the agent to DEFER-and-CONTINUE rather than abort the session.
#
# Reads hook JSON on stdin: { tool_name, tool_input, tool_response|error, cwd }.
# Emits JSON with hookSpecificOutput.additionalContext to steer the agent.
# FAIL-OPEN: any error here exits 0 silently.
set -uo pipefail

input="$(cat)"

read_json() { printf '%s' "$input" | python3 -c "import json,sys
try:
    d=json.load(sys.stdin); print(d.get('$1','') if not '$1'.startswith('tool_input.') else (d.get('tool_input',{}) or {}).get('$1'.split('.',1)[1],''))
except Exception:
    print('')" 2>/dev/null; }

tool="$(read_json tool_name)"
err="$(printf '%s' "$input" | python3 -c "import json,sys
try:
    d=json.load(sys.stdin)
    r=d.get('tool_response') or d.get('error') or d.get('tool_error') or ''
    print(json.dumps(r) if not isinstance(r,str) else r)
except Exception:
    print('')" 2>/dev/null)"

# Only act on external/auth-capable tools
case "$tool" in
  mcp__*|*Bash*|Bash) ;;
  *) exit 0 ;;
esac

# Is this an auth/connectivity failure (vs a logic/usage error)?
# Strong, specific signals only — avoid bare words like "login"/"network"/"token"
# that appear in unrelated failures (that caused a false-positive park).
AUTH_RE='unauthor(ized|ised)|not authenticated|re-?authenticate|authentication (failed|required|error)|invalid (or expired )?(token|credential|api ?key)|token (has )?expired|expired token|permission denied \(publickey|HTTP (401|403)|\b(401|403)\b|ETIMEDOUT|ECONNRESET|ECONNREFUSED|ENETUNREACH|could not connect|connection (timed out|refused)|timed out (after|while)|gateway time-?out|429 too many'
# For MCP tools, also treat a bare "timeout/timed out" as auth-ish (overnight remote
# MCP timeout is the canonical case); for plain Bash, require a strong signal above.
MCP_RE='timed? ?out|timeout'
if printf '%s' "$err" | grep -Eiq "$AUTH_RE" \
   || { case "$tool" in mcp__*) printf '%s' "$err" | grep -Eiq "$MCP_RE";; *) false;; esac; }; then
  # Derive a service label from the tool name
  svc="$tool"
  case "$tool" in
    mcp__*) svc="$(printf '%s' "$tool" | sed -E 's/mcp__([^_]+)__.*/\1-mcp/')" ;;
    *Bash*|Bash) svc="bash-remote" ;;
  esac
  cwd="$(read_json cwd)"; [ -z "$cwd" ] && cwd="$PWD"
  python3 ~/.claude/hooks/deferq.py add --service "$svc" \
    --task "auth-blocked tool call: $tool" \
    --resume "re-run the $tool call once auth is restored" \
    --project "$cwd" >/dev/null 2>&1

  python3 - "$svc" <<'PY'
import json,sys
svc=sys.argv[1]
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PostToolUseFailure",
  "additionalContext":(
    f"AUTH/connectivity failure on {svc}. This is NOT a logic error — do NOT abort the session. "
    "It has been parked in the deferred-task queue (~/.claude/hooks/deferq.py). "
    "Follow the auth-resilience skill: retry w/ backoff, try a programmatic refresh, seek an alternate path; "
    "if still blocked, CONTINUE with all work that does not depend on this call and leave the blocked step parked. "
    "Only ask the user if the credential is genuinely human-only (OAuth/MFA re-login)."
  )}}))
PY
fi
exit 0
