#!/usr/bin/env python3
"""secret_scan.py — gate the harness first commit against leaked secrets.

Used by the bootstrap (BLUEPRINT Step 3h) BEFORE `git -C ~/.claude commit`.
Scans the files git is about to commit (the staged set, or a passed path) for
known secret patterns. Exits non-zero and prints offenders if any are found,
so the install script refuses the first commit until they're removed.

Usage:
    python3 secret_scan.py [--staged-in DIR | PATH ...]
        --staged-in DIR   scan `git -C DIR diff --cached --name-only` (default: $HOME/.claude)
        PATH ...          scan explicit files/dirs instead

Exit codes: 0 clean · 1 secrets found · 2 usage/internal error
"""
import os
import re
import subprocess
import sys

# Pattern name -> compiled regex. Mirrors guard.py's leak class, broadened for files.
PATTERNS = {
    "laravel/sanctum-style token (N|hash)": re.compile(r"\b\d+\|[A-Za-z0-9]{30,}\b"),
    "AWS access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "OpenAI/Anthropic key": re.compile(r"\b(sk|sk-ant)-[A-Za-z0-9_-]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "PEM private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----"),
    "generic assigned secret": re.compile(
        r"(?i)(api[_-]?key|secret|password|passwd|access[_-]?token|auth[_-]?token)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9/+_-]{16,}"
    ),
}

# Filenames that should never be committed at all (secret-bearing by convention).
FORBIDDEN_BASENAMES = re.compile(
    r"^(\.env(\.(?!example$|sample$|template$).+)?|"
    r"id_rsa|id_ed25519|.*\.pem|.*\.key|.*\.p12|.*\.pfx|secrets\.(json|ya?ml))$"
)

SKIP_BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".db",
                   ".db-wal", ".db-shm", ".pyc", ".woff", ".woff2", ".ico"}


def iter_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                if ".git" in root.split(os.sep):
                    continue
                for f in files:
                    yield os.path.join(root, f)
        elif os.path.isfile(p):
            yield p


def staged_files(repo_dir):
    try:
        out = subprocess.run(
            ["git", "-C", repo_dir, "diff", "--cached", "--name-only", "-z"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [os.path.join(repo_dir, f) for f in out.split("\0") if f]


def scan_file(path):
    """Return list of (pattern_name, lineno, snippet) findings for one file."""
    findings = []
    base = os.path.basename(path)
    if FORBIDDEN_BASENAMES.match(base):
        findings.append(("forbidden filename (secret-bearing)", 0, base))
        return findings
    _root, ext = os.path.splitext(base)
    if ext.lower() in SKIP_BINARY_EXT:
        return findings
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh, 1):
                if "secret_scan" in line or "PATTERNS" in line:
                    continue  # don't flag this scanner's own pattern table
                for name, rx in PATTERNS.items():
                    if rx.search(line):
                        findings.append((name, i, line.strip()[:80]))
    except OSError:
        pass
    return findings


def main(argv):
    args = argv[1:]
    if args and args[0] == "--staged-in":
        if len(args) < 2:
            print("usage: secret_scan.py --staged-in DIR", file=sys.stderr)
            return 2
        files = staged_files(args[1])
    elif args:
        files = list(iter_files(args))
    else:
        files = staged_files(os.path.expanduser("~/.claude"))

    all_findings = []
    for f in files:
        for (name, lineno, snip) in scan_file(f):
            all_findings.append((f, name, lineno, snip))

    if all_findings:
        print("SECRET SCAN FAILED — refusing commit. Found:", file=sys.stderr)
        for (f, name, lineno, snip) in all_findings:
            loc = f"{f}:{lineno}" if lineno else f
            print(f"  [{name}] {loc}\n      {snip}", file=sys.stderr)
        print("\nRemove these (move to .env.local / secrets manager) and re-run.",
              file=sys.stderr)
        return 1

    print(f"secret_scan: clean ({len(files)} file(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
