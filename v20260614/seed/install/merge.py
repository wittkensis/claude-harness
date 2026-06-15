#!/usr/bin/env python3
"""merge.py — install-mode detection and smart merge for the harness.

Backs three BLUEPRINT install behaviours so they're deterministic, not vibes:

  #99  detect-mode      Is ~/.claude already a harness? Pick fresh/migration/merge.
  #100 merge-file       When merging, keep the local file if it's a SUPERSET of the
                        seed; only write when the seed has content the local lacks.
  #104 merge-sentinel   When the local CLAUDE.md uses sentinel comments to fence a
                        harness-managed section, replace ONLY that section.

Usage:
  merge.py detect-mode [--claude-dir DIR]
        -> prints one of: fresh | migration | merge   (and a JSON report on --json)

  merge.py merge-file SEED LOCAL [--apply]
        -> decides keep-local | overwrite | merge-append; --apply performs it.

  merge.py merge-sentinel SEED_BLOCK LOCAL_CLAUDE_MD [--apply]
        -> replaces the sentinel-fenced block in LOCAL with SEED_BLOCK's content,
           preserving everything outside the sentinels; appends if no sentinels.

Sentinel grammar (default, configurable via --begin/--end):
  # [harness:ew] <anything> BEGIN ...
  ...managed content...
  # [harness:ew] END
"""
import argparse
import json
import os
import re
import sys

DEFAULT_BEGIN = r"#\s*\[harness:ew\].*BEGIN"
DEFAULT_END = r"#\s*\[harness:ew\].*END"

# Markers that say "this dir already holds harness content".
HARNESS_MARKERS = [
    "HARNESS/manifest.json",
    "harness.config.json",
    "state/backlog.py",
]
HARNESS_SENTINEL_RX = re.compile(r"\[harness:ew\]")


# ---------- #99 detect-mode ----------

def detect_mode(claude_dir):
    """Return (mode, report). mode in {fresh, migration, merge}."""
    report = {"claude_dir": claude_dir, "exists": os.path.isdir(claude_dir),
              "markers_found": [], "skills": 0, "has_sentinel_claude_md": False,
              "is_git": False}
    if not report["exists"]:
        report["reason"] = "~/.claude does not exist"
        return "fresh", report

    for m in HARNESS_MARKERS:
        if os.path.exists(os.path.join(claude_dir, m)):
            report["markers_found"].append(m)

    skills_dir = os.path.join(claude_dir, "skills")
    if os.path.isdir(skills_dir):
        report["skills"] = sum(
            1 for e in os.listdir(skills_dir)
            if os.path.isfile(os.path.join(skills_dir, e, "SKILL.md"))
        )

    cmd = os.path.join(claude_dir, "CLAUDE.md")
    if os.path.isfile(cmd):
        report["has_sentinel_claude_md"] = bool(
            HARNESS_SENTINEL_RX.search(open(cmd, errors="ignore").read()))

    report["is_git"] = os.path.isdir(os.path.join(claude_dir, ".git"))

    has_harness = bool(report["markers_found"]) or report["has_sentinel_claude_md"]
    has_any_content = report["skills"] > 0 or has_harness or report["is_git"]

    if not has_any_content:
        report["reason"] = "~/.claude exists but holds no harness/skill content"
        return "fresh", report
    if has_harness:
        # Prior harness present -> default to non-destructive merge.
        report["reason"] = "existing harness content detected; default = merge (keep local additions)"
        return "merge", report
    # Content exists but no harness markers -> old/foreign structure -> migration candidate.
    report["reason"] = ("non-harness content present (skills/git but no harness markers); "
                        "migration replaces old structure — confirm with user")
    return "migration", report


# ---------- #100 merge-file (superset rule) ----------

def _norm_lines(text):
    """Whitespace-normalized non-empty lines, for superset comparison."""
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def classify_file_merge(seed_text, local_text):
    """Return (action, detail). action in {overwrite, keep-local, merge-append}."""
    if local_text is None:
        return "overwrite", "no local file — install seed"
    if seed_text == local_text:
        return "keep-local", "identical"
    seed_lines = set(_norm_lines(seed_text))
    local_lines = set(_norm_lines(local_text))
    seed_only = seed_lines - local_lines
    if not seed_only:
        # Local contains every seed line (plus possibly more) -> local is a superset.
        return "keep-local", "local is a superset of seed (all seed content present locally)"
    if seed_lines >= local_lines:
        # Seed is a superset of local -> safe to take seed.
        return "overwrite", "seed is a superset of local"
    # Divergent: seed has new content AND local has its own. Don't clobber.
    return "merge-append", f"divergent ({len(seed_only)} seed-only line(s)); needs review/merge"


def merge_file(seed_path, local_path, apply):
    seed_text = open(seed_path, encoding="utf-8").read()
    local_text = open(local_path, encoding="utf-8").read() if os.path.exists(local_path) else None
    action, detail = classify_file_merge(seed_text, local_text)
    print(f"{action}: {local_path}  ({detail})")
    if not apply:
        return action
    if action == "overwrite":
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(seed_text)
    elif action == "merge-append":
        # Conservative: never silently merge divergent content; leave a .seed-new
        # alongside for the human/Claude to reconcile.
        with open(local_path + ".seed-new", "w", encoding="utf-8") as f:
            f.write(seed_text)
        print(f"  wrote {local_path}.seed-new for review (local left untouched)")
    # keep-local: nothing to do
    return action


# ---------- #104 merge-sentinel (CLAUDE.md) ----------

def merge_sentinel(seed_block_text, local_path, begin_rx, end_rx, apply):
    """Replace the sentinel-fenced section in local with the seed block.

    Preserves everything outside the sentinels. If the local file has no
    sentinels, append the seed block (which must itself carry sentinels).
    """
    local_text = open(local_path, encoding="utf-8").read() if os.path.exists(local_path) else ""
    bre, ere = re.compile(begin_rx), re.compile(end_rx)

    begin_m = bre.search(local_text)
    end_m = ere.search(local_text)

    if begin_m and end_m and end_m.start() > begin_m.start():
        # Replace from the BEGIN line start through the end of the END line.
        end_line_end = local_text.find("\n", end_m.end())
        if end_line_end == -1:
            end_line_end = len(local_text)
        new_text = (local_text[:begin_m.start()]
                    + seed_block_text.rstrip("\n") + "\n"
                    + local_text[end_line_end + 1:])
        action = "replaced sentinel block (content outside sentinels preserved)"
    else:
        sep = "" if local_text.endswith("\n") or not local_text else "\n"
        prefix = local_text + sep + ("\n" if local_text else "")
        new_text = prefix + seed_block_text.rstrip("\n") + "\n"
        action = "no sentinels found — appended harness block after existing content"

    print(action)
    if apply:
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(new_text)
    else:
        sys.stdout.write(new_text)
    return new_text


def main(argv):
    p = argparse.ArgumentParser(prog="merge.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    pd = sub.add_parser("detect-mode")
    pd.add_argument("--claude-dir", default=os.path.expanduser("~/.claude"))
    pd.add_argument("--json", action="store_true")

    pf = sub.add_parser("merge-file")
    pf.add_argument("seed"); pf.add_argument("local"); pf.add_argument("--apply", action="store_true")

    psnt = sub.add_parser("merge-sentinel")
    psnt.add_argument("seed_block"); psnt.add_argument("local")
    psnt.add_argument("--begin", default=DEFAULT_BEGIN); psnt.add_argument("--end", default=DEFAULT_END)
    psnt.add_argument("--apply", action="store_true")

    a = p.parse_args(argv[1:])

    if a.cmd == "detect-mode":
        mode, report = detect_mode(a.claude_dir)
        if a.json:
            print(json.dumps({"mode": mode, **report}, indent=2))
        else:
            print(mode)
            print(f"  reason: {report['reason']}", file=sys.stderr)
        return 0

    if a.cmd == "merge-file":
        merge_file(a.seed, a.local, a.apply)
        return 0

    if a.cmd == "merge-sentinel":
        seed_block = open(a.seed_block, encoding="utf-8").read()
        merge_sentinel(seed_block, a.local, a.begin, a.end, a.apply)
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
