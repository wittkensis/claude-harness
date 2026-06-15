#!/usr/bin/env python3
"""done-check — the single, language-aware definition of "done".

One checker, called by BOTH gates so they never drift:
  - commit-gate.sh  (blocks `git commit` on failure)
  - stop-checklist.sh (asserts the gate at turn end)

Detects project context from a directory and runs the right checks:
  - js      : tsc --noEmit (if tsconfig+tsc) + npm test (if a test script exists)
  - python  : ruff check (if ruff present) + pytest (if tests + pytest present)
  - harness : ref_lint.py (dangling skill refs) — report-only; never blocks
  - none    : nothing to check

Add your own linters to check_harness() as your harness grows.

Usage:
  done-check.py [--dir DIR] [--quiet]
Exit: 0 = pass / not-applicable · 1 = a check failed (reasons on stdout).
Read-only. macOS-portable (no GNU coreutils assumptions).
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()


def run(cmd: list[str], cwd: Path, timeout: int) -> tuple[bool, str]:
    """Run cmd; return (ok, tail-of-output). Timeout => fail; missing binary => skip (ok)."""
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        out = (p.stdout + p.stderr).strip()
        return p.returncode == 0, out[-1200:]
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    except FileNotFoundError:
        return True, ""  # binary absent => check not applicable, don't fail


def find_root(start: Path, marker: str) -> Path | None:
    d = start.resolve()
    while d != d.parent:
        if (d / marker).exists():
            return d
        d = d.parent
    return None


def detect(start: Path) -> tuple[str, Path | None]:
    s = str(start.resolve())
    if s == str(HOME / ".claude") or s.startswith(str(HOME / ".claude") + os.sep):
        return "harness", HOME / ".claude"
    js_root = find_root(start, "package.json")
    py_root = find_root(start, "pyproject.toml") or find_root(start, "requirements.txt")
    if js_root and py_root:
        return ("js", js_root) if len(str(js_root)) >= len(str(py_root)) else ("python", py_root)
    if js_root:
        return "js", js_root
    if py_root:
        return "python", py_root
    return "none", None


def check_js(root: Path) -> list[str]:
    fails: list[str] = []
    tsc = root / "node_modules" / ".bin" / "tsc"
    if (root / "tsconfig.json").is_file() and tsc.is_file():
        ok, out = run([str(tsc), "--noEmit"], root, 180)
        if not ok:
            fails.append(f"typecheck failed (tsc --noEmit):\n{out}")
    pkg = root / "package.json"
    has_test = False
    if pkg.is_file():
        import json
        try:
            has_test = bool(json.loads(pkg.read_text()).get("scripts", {}).get("test"))
        except Exception:
            has_test = False
    if has_test:
        ok, out = run(["npm", "test", "--silent"], root, 300)
        if not ok:
            fails.append(f"tests failed (npm test):\n{out}")
    return fails


def check_python(root: Path) -> list[str]:
    fails: list[str] = []
    if shutil.which("ruff"):
        ok, out = run(["ruff", "check", "."], root, 120)
        if not ok:
            fails.append(f"lint failed (ruff check):\n{out}")
    has_tests = (root / "tests").is_dir() or any(root.glob("test_*.py")) or any(root.glob("*_test.py"))
    if has_tests and shutil.which("pytest"):
        ok, out = run(["pytest", "-q"], root, 300)
        if not ok:
            fails.append(f"tests failed (pytest -q):\n{out}")
    return fails


def check_harness(root: Path) -> list[str]:
    """Report-only: harness linters surface drift but never hard-block a turn.
    Add your own linters below as your harness grows."""
    notes: list[str] = []
    ref_lint = HOME / ".claude" / "HARNESS" / "install" / "ref_lint.py"
    skills_dir = HOME / ".claude" / "skills"
    for name, cmd in (
        ("ref_lint", ["python3", str(ref_lint), str(skills_dir)]),
        # Add project-specific linters here:
        # ("my-linter", ["python3", str(HOME / "myproject" / ".claude" / "my-linter.py")]),
    ):
        script = Path(cmd[1]) if len(cmd) > 1 else None
        if script and not script.exists():
            continue  # skip linters not yet installed
        ok, out = run(cmd, HOME, 60)
        if not ok:
            notes.append(f"{name}: {out.splitlines()[0] if out else 'failed'}")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.getcwd())
    ap.add_argument("--quiet", action="store_true", help="print nothing when clean")
    args = ap.parse_args()

    kind, root = detect(Path(args.dir))
    if kind == "none" or root is None:
        if not args.quiet:
            print("done-check: no JS/Python/harness context — nothing to verify.")
        return 0

    if kind == "harness":
        notes = check_harness(root)
        if notes:
            print("done-check (harness) — drift, fix before claiming done:")
            for n in notes:
                print("  -", n)
        elif not args.quiet:
            print("done-check (harness): ref_lint clean.")
        return 0  # harness is report-only, never blocks

    fails = check_js(root) if kind == "js" else check_python(root)
    if fails:
        print(f"done-check ({kind}) FAILED in {root.name} — not done:")
        for f in fails:
            print("  —", f)
        return 1
    if not args.quiet:
        print(f"done-check ({kind}): clean in {root.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
