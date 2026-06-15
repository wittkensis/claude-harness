#!/usr/bin/env python3
"""ref_lint.py — dangling skill-reference linter for the harness.

A skill SKILL.md may reference other skills as `family--name`. A reference is
*dangling* when the named skill is neither (a) installed in the skills dir nor
(b) declared by the referencing skill as an intentional forward-pointer.

Forward-pointers are declared in YAML frontmatter:

    metadata:
      refs-external:        # skills this file points to but that aren't seeded
        - plan--prd
        - log--issues

This keeps "Related / Downstream" links to skills the user will author later
*explicit and accounted for*, while still catching genuine typos/rot
(e.g. `ops--sesion-start`) that point at nothing and were never declared.

Usage:
    python3 ref_lint.py [SKILLS_DIR]      (default: $HOME/.claude/skills,
                                           falling back to ./seed/skills)

Exit codes: 0 clean · 1 dangling refs found · 2 usage error
"""
import os
import re
import sys

REF_RX = re.compile(r"`([a-z][a-z0-9]*--[a-z0-9][a-z0-9-]*)`")
# refs that are illustrative placeholders, never meant to resolve:
PLACEHOLDER_PREFIXES = ("myapp--", "myfleet--", "family--", "yourapp--")


def parse_frontmatter_external(text):
    """Return set of skills declared under metadata.refs-external (cheap YAML)."""
    out = set()
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    if end == -1:
        return out
    fm = text[3:end]
    in_block = False
    for line in fm.splitlines():
        stripped = line.strip()
        if re.match(r"^refs-external\s*:", stripped):
            in_block = True
            continue
        if in_block:
            m = re.match(r"^-\s*([a-z][a-z0-9]*--[a-z0-9-]+)\s*$", stripped)
            if m:
                out.add(m.group(1))
            elif stripped and not stripped.startswith("-"):
                in_block = False  # next key
    return out


def discover_skills(skills_dir):
    """Skill names = subdirectory names that contain a SKILL.md."""
    names = set()
    if not os.path.isdir(skills_dir):
        return names
    for entry in os.listdir(skills_dir):
        if os.path.isfile(os.path.join(skills_dir, entry, "SKILL.md")):
            names.add(entry)
    return names


def lint(skills_dir):
    installed = discover_skills(skills_dir)
    dangling = []  # (skill, ref, lineno)
    for name in sorted(installed):
        path = os.path.join(skills_dir, name, "SKILL.md")
        text = open(path, encoding="utf-8", errors="ignore").read()
        declared = parse_frontmatter_external(text)
        for i, line in enumerate(text.splitlines(), 1):
            for ref in REF_RX.findall(line):
                if ref == name:
                    continue
                if ref.startswith(PLACEHOLDER_PREFIXES):
                    continue
                if ref in installed or ref in declared:
                    continue
                dangling.append((name, ref, i))
    return installed, dangling


def main(argv):
    if len(argv) > 2:
        print("usage: ref_lint.py [SKILLS_DIR]", file=sys.stderr)
        return 2
    if len(argv) == 2:
        skills_dir = argv[1]
    else:
        home = os.path.expanduser("~/.claude/skills")
        skills_dir = home if os.path.isdir(home) else os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "seed", "skills",
        )

    installed, dangling = lint(skills_dir)
    if not installed:
        print(f"ref_lint: no skills found under {skills_dir}", file=sys.stderr)
        return 2

    if dangling:
        print(f"ref_lint: {len(dangling)} dangling reference(s) in {skills_dir}:",
              file=sys.stderr)
        for (skill, ref, lineno) in dangling:
            print(f"  {skill}/SKILL.md:{lineno}  ->  `{ref}` "
                  f"(not installed, not in metadata.refs-external)", file=sys.stderr)
        print("\nFix: install the skill, correct the name, or declare it under "
              "`metadata.refs-external` if it's an intentional forward-pointer.",
              file=sys.stderr)
        return 1

    print(f"ref_lint: clean ({len(installed)} skills, all references resolve)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
