#!/usr/bin/env python3
"""Post-install verification for the ported harness. Runs against an installed
~/.claude (default $HOME, or --home for a dry-run tree). Behavioral, not just
syntactic — it exercises the hooks the way Claude Code will.

Usage: port-test.py [--home DIR]
Exit 0 if all pass, 1 otherwise.
"""
import argparse, json, os, re, subprocess, sys, tempfile, glob, shutil

ap = argparse.ArgumentParser(); ap.add_argument("--home", default=os.path.expanduser("~"))
HOME = ap.parse_args().home
H = os.path.join(HOME, ".claude")
HOOKS, SKILLS, AGENTS = f"{H}/hooks", f"{H}/skills", f"{H}/agents"
results = []
def check(name, cond, detail=""): results.append((bool(cond), name, detail))

def run_hook(script, payload, env=None):
    cmd = (["python3", f"{HOOKS}/{script}"] if script.endswith(".py") else ["bash", f"{HOOKS}/{script}"])
    e = dict(os.environ); e["HOME"] = HOME
    if env: e.update(env)
    r = subprocess.run(cmd, input=json.dumps(payload), capture_output=True, text=True, env=e)
    return r.returncode, r.stdout, r.stderr

# 1. hooks present + executable
for f in ["guard.py","commit-gate.sh","lint-fix.sh","auth-failure.sh","session-context.sh",
          "stop-checklist.sh","deferq.py","tokens.py","harness_config.py","lib.sh"]:
    p = f"{HOOKS}/{f}"
    check(f"hook present: {f}", os.path.isfile(p), p)

# 2. settings wiring
try:
    cfg = json.load(open(f"{H}/settings.json"))
    for ev in ("PreToolUse","PostToolUse","SessionStart","Stop","PostToolUseFailure"):
        check(f"settings hooks: {ev} wired", ev in cfg.get("hooks", {}))
    cmds = [h.get("command","") for arr in cfg.get("hooks",{}).values() for g in arr for h in g.get("hooks",[])]
    for c in cmds:
        for p in re.findall(r"\$HOME(/\S+\.(?:py|sh))", c):
            fp = os.path.join(HOME, p.lstrip("/"))
            check(f"wired script exists: {os.path.basename(p)}", os.path.isfile(fp), fp)
except Exception as e:
    check("settings.json parses", False, str(e))

# 3. guard behavioral (set HARNESS_CONFIG to a temp config w/ a protected glob)
tcfg = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
json.dump({"version":1,"protected_globs":["/tmp/protdir/**"]}, tcfg); tcfg.close()
genv = {"HARNESS_CONFIG": tcfg.name}
gcases = [
    ("guard blocks .env", {"tool_name":"Edit","tool_input":{"file_path":"/tmp/x/.env"}}, 2),
    ("guard allows .env.example", {"tool_name":"Edit","tool_input":{"file_path":"/tmp/x/.env.example"}}, 0),
    ("guard allows .env.local", {"tool_name":"Edit","tool_input":{"file_path":"/tmp/x/.env.local"}}, 0),
    ("guard blocks .env.production", {"tool_name":"Edit","tool_input":{"file_path":"/tmp/x/.env.production"}}, 2),
    ("guard allows normal ts", {"tool_name":"Write","tool_input":{"file_path":"/tmp/x/a.ts"}}, 0),
    ("guard blocks protected glob", {"tool_name":"Write","tool_input":{"file_path":"/tmp/protdir/a.md"}}, 2),
    ("guard blocks rm -rf ~", {"tool_name":"Bash","tool_input":{"command":"rm -rf ~/Docs"}}, 2),
    ("guard allows scoped rm", {"tool_name":"Bash","tool_input":{"command":"rm -rf ./build"}}, 0),
    ("guard allows echo w/ rm text", {"tool_name":"Bash","tool_input":{"command":"echo 'never rm -rf / ok'"}}, 0),
    ("guard blocks force-push main", {"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}, 2),
    ("guard allows force-with-lease", {"tool_name":"Bash","tool_input":{"command":"git push --force-with-lease origin main"}}, 0),
]
for name, payload, want in gcases:
    rc,_,_ = run_hook("guard.py", payload, genv)
    check(name, rc==want, f"want {want} got {rc}")

# 4. commit-gate behavioral (temp failing + passing JS projects)
tmp = tempfile.mkdtemp(prefix="ptgate-")
try:
    os.makedirs(f"{tmp}/node_modules/.bin", exist_ok=True)
    json.dump({"name":"t","scripts":{"test":"exit 1"}}, open(f"{tmp}/package.json","w"))
    open(f"{tmp}/tsconfig.json","w").write("{}")
    open(f"{tmp}/node_modules/.bin/tsc","w").write("#!/bin/sh\nexit 0\n"); os.chmod(f"{tmp}/node_modules/.bin/tsc",0o755)
    rc,_,_ = run_hook("commit-gate.sh", {"tool_name":"Bash","tool_input":{"command":"git commit -m x"},"cwd":tmp})
    check("commit-gate blocks failing test", rc==2, f"got {rc}")
    rc,_,_ = run_hook("commit-gate.sh", {"tool_name":"Bash","tool_input":{"command":"git commit -m '[wip] x'"},"cwd":tmp})
    check("commit-gate [wip] bypass", rc==0, f"got {rc}")
    rc,_,_ = run_hook("commit-gate.sh", {"tool_name":"Bash","tool_input":{"command":"ls"},"cwd":tmp})
    check("commit-gate ignores non-commit", rc==0, f"got {rc}")
    ok = tempfile.mkdtemp(prefix="ptgate-ok-")
    os.makedirs(f"{ok}/node_modules/.bin", exist_ok=True)
    json.dump({"name":"t","scripts":{"test":"exit 0"}}, open(f"{ok}/package.json","w"))
    open(f"{ok}/tsconfig.json","w").write("{}")
    open(f"{ok}/node_modules/.bin/tsc","w").write("#!/bin/sh\nexit 0\n"); os.chmod(f"{ok}/node_modules/.bin/tsc",0o755)
    rc,_,_ = run_hook("commit-gate.sh", {"tool_name":"Bash","tool_input":{"command":"git commit -m ok"},"cwd":ok})
    check("commit-gate passes clean project", rc==0, f"got {rc}")
    shutil.rmtree(ok, ignore_errors=True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# 5. skills integrity
for d in [d for d in glob.glob(f"{SKILLS}/*") if os.path.isdir(d)]:
    name = os.path.basename(d); sk = f"{d}/SKILL.md"
    if not os.path.isfile(sk):
        check(f"skill {name}: SKILL.md", False); continue
    txt = open(sk).read()
    check(f"skill {name}: frontmatter", bool(re.search(r"^name:\s*\S",txt,re.M)) and bool(re.search(r"^description:\s*\S",txt,re.M)))
    check(f"skill {name}: no inert nested SKILL.md", not glob.glob(f"{d}/*/SKILL.md"))
    for link in re.findall(r"\]\(([^)]+\.md)\)", txt):
        if link.startswith("http"): continue
        check(f"skill {name}: link {link}", os.path.isfile(os.path.normpath(os.path.join(d,link))))

# 6. agents
names = set()
for a in glob.glob(f"{AGENTS}/*.md"):
    m = re.search(r"^name:\s*(\S+)", open(a).read(), re.M)
    if m: names.add(m.group(1))
for r in ("evaluator","swarm-worker","deploy-verifier"):
    check(f"agent present: {r}", r in names, str(sorted(names)))

# 7. CLAUDE.md discipline block + config + state
cm = open(f"{H}/CLAUDE.md").read() if os.path.isfile(f"{H}/CLAUDE.md") else ""
check("CLAUDE.md has discipline block", "HARNESS-PORT:BEGIN" in cm and "HARNESS-PORT:END" in cm)
try:
    json.load(open(f"{H}/harness.config.json")); check("harness.config.json parses", True)
except Exception as e:
    check("harness.config.json parses", False, str(e))
# tokens.py/deferq.py runnable
r = subprocess.run(["python3", f"{HOOKS}/deferq.py","count"], capture_output=True, text=True, env={**os.environ,"HOME":HOME})
check("deferq.py count runs", r.returncode==0 and r.stdout.strip().isdigit(), r.stderr[:80])
r = subprocess.run(["python3", f"{HOOKS}/tokens.py","due-count"], capture_output=True, text=True,
                   env={**os.environ,"HOME":HOME,"HARNESS_CONFIG":f"{H}/harness.config.json"})
check("tokens.py due-count runs", r.returncode==0 and r.stdout.strip().isdigit(), r.stderr[:80])

os.unlink(tcfg.name)
# report
passed = sum(1 for c,_,_ in results if c)
print(f"\n{'='*58}\nPORT TEST: {passed}/{len(results)} passed  (home={H})\n{'='*58}")
for ok,name,detail in results:
    if not ok: print(f"FAIL  {name}  [{detail}]")
sys.exit(0 if passed==len(results) else 1)
