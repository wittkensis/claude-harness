#!/usr/bin/env python3
"""Deterministic generator for the portable harness. The harness-bootstrap skill
runs the judgment steps (investigate + interview, producing harness.config.json),
then calls this to do the mechanical, idempotent install. Safe to re-run.

Steps (in order):
  1. Back up the existing ~/.claude  ->  ~/.claude/.backups/<ts>.tgz
  2. Install hooks      (kit/hooks/*      -> ~/.claude/hooks/, overwrite, +x)
  3. Install agents     (the 4 managed agents -> ~/.claude/agents/, overwrite)
  4. Install skills     (kit/skills/*     -> ~/.claude/skills/, copy-if-absent;
                         existing same-name skills are LEFT ALONE and reported)
  5. Merge hook wiring  into ~/.claude/settings.json  (append-if-absent, never clobber)
  6. Append discipline  to ~/.claude/CLAUDE.md  (idempotent, between sentinel markers)
  7. Install config     (harness.config.json, if given and absent / or --force)
  8. Seed state         (empty token-registry + state/ dir)

Usage:
  install.py [--kit DIR] [--home DIR] [--config FILE] [--force] [--dry]
  --dry : install into a fresh temp HOME and print the tree (no touch to real ~).
"""
import argparse, json, os, shutil, stat, sys, tarfile, tempfile, time

MANAGED_AGENTS = {"evaluator.md", "swarm-worker.md", "deploy-verifier.md", "librarian.md"}
BEGIN = "<!-- HARNESS-PORT:BEGIN"
END = "<!-- HARNESS-PORT:END -->"


def log(msg): print(f"  {msg}")


def backup(claude_dir):
    if not os.path.isdir(claude_dir):
        log("no existing ~/.claude — nothing to back up"); return
    bdir = os.path.join(claude_dir, ".backups")
    os.makedirs(bdir, exist_ok=True)
    dest = os.path.join(bdir, time.strftime("%Y%m%d-%H%M%S") + ".tgz")
    with tarfile.open(dest, "w:gz") as tar:
        for entry in os.listdir(claude_dir):
            if entry == ".backups":
                continue
            tar.add(os.path.join(claude_dir, entry), arcname=entry)
    log(f"backup -> {dest}")


def install_hooks(kit, claude_dir):
    src, dst = os.path.join(kit, "hooks"), os.path.join(claude_dir, "hooks")
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        s = os.path.join(src, f); d = os.path.join(dst, f)
        if os.path.isfile(s):
            shutil.copy2(s, d)
            if f.endswith((".sh", ".py")):
                os.chmod(d, os.stat(d).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    log(f"hooks: installed {len(os.listdir(src))} files (overwrote managed copies)")


def install_agents(kit, claude_dir):
    src, dst = os.path.join(kit, "agents"), os.path.join(claude_dir, "agents")
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in sorted(os.listdir(src)):
        if f in MANAGED_AGENTS:
            shutil.copy2(os.path.join(src, f), os.path.join(dst, f)); n += 1
    log(f"agents: installed {n} managed agents")


def install_skills(kit, claude_dir):
    src, dst = os.path.join(kit, "skills"), os.path.join(claude_dir, "skills")
    os.makedirs(dst, exist_ok=True)
    added, skipped = [], []
    for name in sorted(os.listdir(src)):
        s = os.path.join(src, name)
        if not os.path.isdir(s):
            continue
        d = os.path.join(dst, name)
        if os.path.exists(d):
            skipped.append(name)
        else:
            shutil.copytree(s, d); added.append(name)
    log(f"skills: added {len(added)} ({', '.join(added) or 'none'})")
    if skipped:
        log(f"skills: LEFT EXISTING untouched ({', '.join(skipped)}) — review/merge by hand if you want the ported version")


def merge_settings(kit, claude_dir):
    tmpl = json.load(open(os.path.join(kit, "templates", "settings.hooks.json")))["hooks"]
    path = os.path.join(claude_dir, "settings.json")
    cfg = {}
    if os.path.isfile(path):
        try: cfg = json.load(open(path))
        except Exception:
            log("settings.json unreadable — leaving it, writing hooks to settings.json.harness-port.json instead")
            json.dump({"hooks": tmpl}, open(path + ".harness-port.json", "w"), indent=2); return
    hooks = cfg.setdefault("hooks", {})
    added = 0
    for event, groups in tmpl.items():
        existing = hooks.setdefault(event, [])
        existing_cmds = {h.get("command") for g in existing for h in g.get("hooks", [])}
        for g in groups:
            new_cmds = [h for h in g.get("hooks", []) if h.get("command") not in existing_cmds]
            if not new_cmds:
                continue
            # try to fold into a group with the same matcher; else append a new group
            match = g.get("matcher")
            folded = False
            for eg in existing:
                if eg.get("matcher") == match:
                    eg.setdefault("hooks", []).extend(new_cmds); folded = True; break
            if not folded:
                grp = {"hooks": new_cmds}
                if match is not None: grp = {"matcher": match, **grp}
                existing.append(grp)
            added += len(new_cmds)
    json.dump(cfg, open(path, "w"), indent=2); open(path, "a").write("\n")
    log(f"settings.json: merged hook wiring (+{added} commands, existing preserved)")


def append_claude_md(kit, claude_dir):
    block = open(os.path.join(kit, "templates", "CLAUDE.md.append.md")).read().strip()
    path = os.path.join(claude_dir, "CLAUDE.md")
    cur = open(path).read() if os.path.isfile(path) else ""
    if BEGIN in cur and END in cur:
        pre = cur[:cur.index(BEGIN)].rstrip()
        post = cur[cur.index(END) + len(END):].lstrip()
        new = (pre + "\n\n" + block + "\n\n" + post).strip() + "\n"
        log("CLAUDE.md: replaced existing HARNESS-PORT block (idempotent)")
    else:
        new = (cur.rstrip() + "\n\n" + block + "\n").lstrip()
        log("CLAUDE.md: appended discipline block")
    open(path, "w").write(new)


def install_config(kit, claude_dir, config, force):
    path = os.path.join(claude_dir, "harness.config.json")
    if os.path.isfile(path) and not force:
        log("harness.config.json exists — left as-is (use --force to overwrite)"); return
    if config and os.path.isfile(config):
        shutil.copy2(config, path); log(f"harness.config.json: installed from {config}")
    elif not os.path.isfile(path):
        json.dump({"version": 1, "project_roots": [], "protected_globs": [],
                   "commit_gate": {"typecheck": "", "test": ""},
                   "token_registry_path": "~/.claude/token-registry.json",
                   "deploy": {}}, open(path, "w"), indent=2)
        log("harness.config.json: wrote a minimal stub (fill via the interview)")


def seed_state(claude_dir):
    os.makedirs(os.path.join(claude_dir, "state"), exist_ok=True)
    reg = os.path.join(claude_dir, "token-registry.json")
    if not os.path.isfile(reg):
        json.dump({"_warning": "METADATA ONLY — never store token VALUES here.", "tokens": []},
                  open(reg, "w"), indent=2)
        log("token-registry.json: seeded empty (metadata-only)")


def main():
    kit_default = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--kit", default=kit_default)
    ap.add_argument("--home", default=os.path.expanduser("~"))
    ap.add_argument("--config", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    home = tempfile.mkdtemp(prefix="harness-dry-") if a.dry else a.home
    claude = os.path.join(home, ".claude")
    os.makedirs(claude, exist_ok=True)
    print(f"Installing portable harness -> {claude}" + ("  (DRY RUN)" if a.dry else ""))
    backup(claude)
    install_hooks(a.kit, claude)
    install_agents(a.kit, claude)
    install_skills(a.kit, claude)
    merge_settings(a.kit, claude)
    append_claude_md(a.kit, claude)
    install_config(a.kit, claude, a.config, a.force)
    seed_state(claude)
    print("Done. Next: run port-test.py to verify, then restart Claude Code (or /hooks) to load the wiring.")
    if a.dry:
        print(f"\nDRY-RUN tree at {claude}:")
        for r, _, fs in os.walk(claude):
            for f in fs:
                print("   " + os.path.relpath(os.path.join(r, f), home))


if __name__ == "__main__":
    main()
