#!/usr/bin/env python3
"""harness.py — model, version, lock, export, and bootstrap a harness (#70).

Makes a harness reproducible, diffable, and transferable. A "harness" is the
set of components under ~/.claude that make Claude Code reliable:

    skills/   agents/   hooks/   state/   memory/   prompts/
    CLAUDE.md   SKILLS.md   harness.config.json   .gitignore

This tool gives that set a formal model (a lockfile), semantic versioning, a
portable export artifact, and a zero-manual-step bootstrap from that artifact.

Commands:
  model     [--root DIR]                 print the component inventory (JSON)
  lock      [--root DIR] [--out PATH]    write harness.lock.json (the manifest)
  version   [--root DIR] [--bump M]      show / bump semver (M = major|minor|patch)
  export    [--root DIR] [--out FILE]    bundle harness -> portable .tar.gz + lock
  verify    --artifact FILE              check an artifact against its embedded lock
  bootstrap --artifact FILE [--root DIR] install an artifact to a fresh harness

Lockfile schema (harness.lock.json):
  {
    "schema": 1,
    "harness_version": "1.0.0",          # semver of THIS harness
    "blueprint": "blueprint-ew-v20260614",
    "generated": "<iso8601>",
    "components": {
      "<kind>": [ {"path": "...", "sha256": "...", "bytes": N}, ... ]
    },
    "counts": { "skills": N, "hooks": N, ... }
  }
"""
import argparse
import hashlib
import io
import json
import os
import sys
import tarfile
from datetime import datetime, timezone

SCHEMA = 1
LOCK_NAME = "harness.lock.json"

# kind -> (relative root within the harness, recurse?)
COMPONENTS = {
    "skills": ("skills", True),
    "agents": ("agents", True),
    "hooks": ("hooks", True),
    "state": ("state", True),
    "memory": ("memory", True),
    "prompts": ("prompts", True),
}
# top-level singleton files that are part of the harness model
SINGLETONS = ["CLAUDE.md", "SKILLS.md", "harness.config.json", ".gitignore"]

# never bundle these (machine-local / secret / regenerable)
EXCLUDE_SUFFIXES = (".db", ".db-wal", ".db-shm", ".pyc", ".log")
EXCLUDE_DIRS = {"__pycache__", ".git"}
EXCLUDE_NAMES = {".DS_Store"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def included(path, name):
    if name in EXCLUDE_NAMES:
        return False
    if any(name.endswith(s) for s in EXCLUDE_SUFFIXES):
        return False
    return True


def walk_component(root, rel, recurse):
    base = os.path.join(root, rel)
    files = []
    if not os.path.isdir(base):
        return files
    if recurse:
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                if included(full, fn):
                    files.append(full)
    else:
        for fn in sorted(os.listdir(base)):
            full = os.path.join(base, fn)
            if os.path.isfile(full) and included(full, fn):
                files.append(full)
    return sorted(files)


def build_model(root):
    """Return (components_dict, all_relpaths). Paths are relative to root."""
    components = {}
    all_paths = []
    for kind, (rel, recurse) in COMPONENTS.items():
        entries = []
        for full in walk_component(root, rel, recurse):
            relp = os.path.relpath(full, root)
            entries.append({"path": relp, "sha256": sha256_file(full),
                            "bytes": os.path.getsize(full)})
            all_paths.append(relp)
        components[kind] = entries
    singles = []
    for name in SINGLETONS:
        full = os.path.join(root, name)
        if os.path.isfile(full):
            relp = os.path.relpath(full, root)
            singles.append({"path": relp, "sha256": sha256_file(full),
                            "bytes": os.path.getsize(full)})
            all_paths.append(relp)
    components["singletons"] = singles
    return components, all_paths


def read_version(root):
    """Harness semver — from harness.config.json harness.semver, default 1.0.0."""
    cfg = os.path.join(root, "harness.config.json")
    if os.path.isfile(cfg):
        try:
            data = json.load(open(cfg))
            v = data.get("harness", {}).get("semver")
            if v:
                return v
        except (OSError, json.JSONDecodeError):
            pass
    # fall back to existing lock
    lock = os.path.join(root, LOCK_NAME)
    if os.path.isfile(lock):
        try:
            return json.load(open(lock)).get("harness_version", "1.0.0")
        except (OSError, json.JSONDecodeError):
            pass
    return "1.0.0"


def read_blueprint(root):
    cfg = os.path.join(root, "harness.config.json")
    if os.path.isfile(cfg):
        try:
            return json.load(open(cfg)).get("harness", {}).get("source", "unknown")
        except (OSError, json.JSONDecodeError):
            pass
    return "unknown"


def bump_semver(v, part):
    try:
        major, minor, patch = (int(x) for x in v.split("."))
    except ValueError:
        major, minor, patch = 1, 0, 0
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def write_version(root, v):
    cfg = os.path.join(root, "harness.config.json")
    data = {}
    if os.path.isfile(cfg):
        try:
            data = json.load(open(cfg))
        except (OSError, json.JSONDecodeError):
            data = {}
    data.setdefault("harness", {})["semver"] = v
    with open(cfg, "w") as f:
        json.dump(data, f, indent=2)


def build_lock(root):
    components, _paths = build_model(root)
    counts = {k: len(v) for k, v in components.items()}
    return {
        "schema": SCHEMA,
        "harness_version": read_version(root),
        "blueprint": read_blueprint(root),
        "generated": now(),
        "components": components,
        "counts": counts,
    }


# ---------- commands ----------

def cmd_model(root):
    components, _ = build_model(root)
    print(json.dumps({"counts": {k: len(v) for k, v in components.items()},
                      "components": components}, indent=2))


def cmd_lock(root, out):
    lock = build_lock(root)
    out = out or os.path.join(root, LOCK_NAME)
    with open(out, "w") as f:
        json.dump(lock, f, indent=2)
    print(f"wrote {out}  (v{lock['harness_version']}, "
          f"{sum(lock['counts'].values())} components)")


def cmd_version(root, bump):
    cur = read_version(root)
    if not bump:
        print(cur)
        return
    new = bump_semver(cur, bump)
    write_version(root, new)
    print(f"{cur} -> {new}")


def cmd_export(root, out):
    lock = build_lock(root)
    v = lock["harness_version"]
    out = out or os.path.join(os.getcwd(), f"harness-{v}.tar.gz")
    paths = [e["path"] for entries in lock["components"].values() for e in entries]
    with tarfile.open(out, "w:gz") as tar:
        # embed the lock at the artifact root
        lock_bytes = json.dumps(lock, indent=2).encode()
        ti = tarfile.TarInfo(LOCK_NAME)
        ti.size = len(lock_bytes)
        ti.mtime = int(datetime.now(timezone.utc).timestamp())
        tar.addfile(ti, io.BytesIO(lock_bytes))
        for relp in paths:
            full = os.path.join(root, relp)
            if os.path.isfile(full):
                tar.add(full, arcname=relp)
    print(f"exported {len(paths)} components -> {out}  (v{v})")
    print(f"  sha256: {sha256_file(out)}")


def _read_member(tar, name):
    f = tar.extractfile(name)
    return f.read() if f else None


def cmd_verify(artifact):
    with tarfile.open(artifact, "r:gz") as tar:
        names = set(tar.getnames())
        if LOCK_NAME not in names:
            print(f"verify: artifact has no {LOCK_NAME}", file=sys.stderr)
            return 1
        lock = json.loads(_read_member(tar, LOCK_NAME))
        bad = []
        for entries in lock["components"].values():
            for e in entries:
                data = _read_member(tar, e["path"])
                if data is None:
                    bad.append(f"missing: {e['path']}")
                elif hashlib.sha256(data).hexdigest() != e["sha256"]:
                    bad.append(f"sha mismatch: {e['path']}")
        if bad:
            print(f"verify: FAILED ({len(bad)} issue(s)):", file=sys.stderr)
            for b in bad:
                print("  " + b, file=sys.stderr)
            return 1
    total = sum(lock["counts"].values())
    print(f"verify: OK — v{lock['harness_version']}, {total} components match the lock.")
    return 0


def cmd_bootstrap(artifact, root):
    """Zero-manual-step install of an artifact onto a fresh root."""
    if cmd_verify(artifact) != 0:
        print("bootstrap: refusing to install a tampered/incomplete artifact.",
              file=sys.stderr)
        return 1
    os.makedirs(root, exist_ok=True)
    with tarfile.open(artifact, "r:gz") as tar:
        lock = json.loads(_read_member(tar, LOCK_NAME))
        members = [m for m in tar.getmembers() if m.name != LOCK_NAME]
        # safety: no path escapes the root
        for m in members:
            dest = os.path.realpath(os.path.join(root, m.name))
            if not dest.startswith(os.path.realpath(root) + os.sep):
                print(f"bootstrap: unsafe path in artifact: {m.name}", file=sys.stderr)
                return 1
        for m in members:
            tar.extract(m, path=root)
        # land the lock too, so the installed harness is self-describing
        lock_path = os.path.join(root, LOCK_NAME)
        with open(lock_path, "w") as f:
            json.dump(lock, f, indent=2)
    # make python tools executable
    for entries in lock["components"].values():
        for e in entries:
            full = os.path.join(root, e["path"])
            if full.endswith(".py") and os.path.isfile(full):
                os.chmod(full, 0o755)
    total = sum(lock["counts"].values())
    print(f"bootstrap: installed v{lock['harness_version']} "
          f"({total} components) to {root}")
    print("Next: `git -C {0} init && python3 {0}/HARNESS/install/verify.py "
          "--claude-dir {0}`".format(root))
    return 0


def main(argv):
    p = argparse.ArgumentParser(prog="harness.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    default_root = os.path.expanduser("~/.claude")

    pm = sub.add_parser("model"); pm.add_argument("--root", default=default_root)
    pl = sub.add_parser("lock"); pl.add_argument("--root", default=default_root); pl.add_argument("--out")
    pv = sub.add_parser("version"); pv.add_argument("--root", default=default_root)
    pv.add_argument("--bump", choices=["major", "minor", "patch"])
    pe = sub.add_parser("export"); pe.add_argument("--root", default=default_root); pe.add_argument("--out")
    pver = sub.add_parser("verify"); pver.add_argument("--artifact", required=True)
    pb = sub.add_parser("bootstrap"); pb.add_argument("--artifact", required=True)
    pb.add_argument("--root", default=default_root)

    a = p.parse_args(argv[1:])
    if a.cmd == "model":
        cmd_model(a.root); return 0
    if a.cmd == "lock":
        cmd_lock(a.root, a.out); return 0
    if a.cmd == "version":
        cmd_version(a.root, a.bump); return 0
    if a.cmd == "export":
        cmd_export(a.root, a.out); return 0
    if a.cmd == "verify":
        return cmd_verify(a.artifact)
    if a.cmd == "bootstrap":
        return cmd_bootstrap(a.artifact, a.root)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
