#!/usr/bin/env bash
# Stop — print the completion checklist (informational only; exit 0, never forces
# a continue). Operationalizes the two-step completion gate as a visible reminder.
cat <<'EOF'
Completion check (two-step gate):
  1) typecheck clean?  2) tests run & passing?  3) intent validated via verify/run (not just "it compiled")?
If any is no and the task is reported done, that's premature victory — go back.
EOF
exit 0
