#!/usr/bin/env python3
"""verify.py — post-install verification gate (BLUEPRINT Step 4).

Runs the hard, mechanical checks an installed harness must pass. Each prints
PASS/FAIL with a reason; a single FAIL makes the whole run exit non-zero so the
installer can stop and report rather than declare a broken install "done".

Checks:
  1. backlog.py present and callable      (#98, #102) — runs `backlog.py --help`
  2. learning-log.py present and callable  (#98)       — runs `--help`
  3. no {{placeholder}} tokens remain     (#102, #103) — scans installed files
  4. no dangling skill refs               (#101, #102) — delegates to ref_lint.py
  5. .gitignore present                    (#97, #102)
  6. CLAUDE.md sentinels present (==2)     (sanity for #104)
  7. harness.config.json is valid JSON

Usage:
  verify.py [--claude-dir DIR]      (default: $HOME/.claude)
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANY_TOKEN_RX = re.compile(r"\{\{[^}]*\}\}")
SENTINEL_RX = re.compile(r"\[harness:ew\]")
SCAN_GLOBS = ["skills/*/SKILL.md", "CLAUDE.md", "SKILLS.md", "harness.config.json",
              "HARNESS/manifest.json"]


class Result:
    def __init__(self):
        self.failed = False

    def check(self, name, ok, detail=""):
        tag = "PASS" if ok else "FAIL"
        print(f"[{tag}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            self.failed = True


def callable_py(path):
    if not os.path.isfile(path):
        return False, "not present"
    try:
        r = subprocess.run([sys.executable, path, "--help"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return False, f"--help exited {r.returncode}: {r.stderr.strip()[:80]}"
        return True, "callable"
    except Exception as e:
        return False, str(e)


def main(argv):
    p = argparse.ArgumentParser(prog="verify.py")
    p.add_argument("--claude-dir", default=os.path.expanduser("~/.claude"))
    a = p.parse_args(argv[1:])
    cd = a.claude_dir
    res = Result()

    # 1 + 2: state tools callable
    ok, detail = callable_py(os.path.join(cd, "state", "backlog.py"))
    res.check("backlog.py present & callable", ok, detail)
    ok, detail = callable_py(os.path.join(cd, "state", "learning-log.py"))
    res.check("learning-log.py present & callable", ok, detail)

    # 3: no placeholder tokens in installed files
    offenders = []
    for pat in SCAN_GLOBS:
        for f in glob.glob(os.path.join(cd, pat)):
            try:
                toks = ANY_TOKEN_RX.findall(open(f, errors="ignore").read())
            except OSError:
                continue
            if toks:
                offenders.append(f"{os.path.relpath(f, cd)}: {sorted(set(toks))}")
    res.check("no {{placeholder}} tokens remain", not offenders,
              "; ".join(offenders) if offenders else "clean")

    # 4: dangling skill refs (delegate to ref_lint.py)
    skills_dir = os.path.join(cd, "skills")
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "ref_lint.py"), skills_dir],
                           capture_output=True, text=True, timeout=30)
        res.check("no dangling skill refs", r.returncode == 0,
                  (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else "")
    except Exception as e:
        res.check("no dangling skill refs", False, str(e))

    # 5: .gitignore present
    res.check(".gitignore present", os.path.isfile(os.path.join(cd, ".gitignore")))

    # 6: CLAUDE.md sentinels == 2
    cmd = os.path.join(cd, "CLAUDE.md")
    if os.path.isfile(cmd):
        n = len(SENTINEL_RX.findall(open(cmd, errors="ignore").read()))
        res.check("CLAUDE.md sentinels (BEGIN+END)", n == 2, f"found {n}, expected 2")
    else:
        res.check("CLAUDE.md sentinels (BEGIN+END)", False, "CLAUDE.md missing")

    # 7: config valid JSON
    cfg = os.path.join(cd, "harness.config.json")
    if os.path.isfile(cfg):
        try:
            json.load(open(cfg))
            res.check("harness.config.json valid", True)
        except json.JSONDecodeError as e:
            res.check("harness.config.json valid", False, str(e))
    else:
        res.check("harness.config.json valid", False, "missing")

    print()
    if res.failed:
        print("VERIFY: FAILED — fix the items above before declaring the install done.",
              file=sys.stderr)
        return 1
    print("VERIFY: all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
