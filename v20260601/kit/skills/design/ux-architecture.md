# Information Architecture

## OOUX Methodology

Object-Oriented UX: design around objects users care about, not pages.

1. **Extract objects** — the nouns (Projects, Tasks, Users, Reports)
2. **Define attributes** — what properties does each have?
3. **Map relationships** — how do objects connect? (1:1, 1:many, many:many)
4. **Identify actions** — what can users do? (CRUD + domain-specific)

```
Object: Project
├── Attributes: name, status, deadline, owner
├── Relationships: has many Tasks, belongs to Team
└── Actions: create, archive, share, export
```

---

## User Flow Mapping

| Flow Type | Purpose | When |
|-----------|---------|------|
| Happy Path | Ideal completion route | Map first, always |
| Error Path | Recovery from mistakes | After happy path |
| Edge Cases | Unusual but valid | Before dev handoff |
| Entry/Exit | How users arrive/leave | Navigation design |

**Notation:**
```
[Start] → (Decision?) → [Action] → [End]
              ↓
         [Alt Path]
```

**Happy Path Checklist:**
- [ ] Single clear goal identified
- [ ] Minimum steps to completion
- [ ] Each step has clear next action
- [ ] Progress visible to user
- [ ] Completion celebrated/confirmed

**Edge Cases to always consider:**
1. Empty states (first-time user, no data)
2. Error states (validation, server, network)
3. Partial completion (user abandons mid-flow)
4. Return visits
5. Permission edge cases

---

## Navigation Patterns

| Pattern | Best For | Avoid When |
|---------|----------|------------|
| Hierarchical | Deep content, clear categories | Flat info, frequent cross-linking |
| Flat | Few top-level items | Deep content, many items |
| Hub & Spoke | Focused tasks | Exploratory browsing |
| Sequential | Wizards, onboarding | Random access needed |

**Primary:** 5-7 items max
**Anti-patterns:** >7 primary items · nested dropdowns >2 levels · hamburger menu on desktop for critical paths

---

## Sitemap Format

```
Home
├── Dashboard
├── Projects
│   ├── Project List
│   ├── Project Detail
│   │   ├── Tasks
│   │   └── Settings
│   └── Create Project
└── Settings
    ├── Profile
    └── Integrations
```

**Validation:** every screen has parent · no orphans · depth ≤ 3 for core flows · reflects user mental model

---

## Decision Gates

Pause for approval at:
1. **Object model** — before designing screens
2. **Happy path flows** — before edge cases
3. **Navigation structure** — before wireframes
4. **Sitemap** — before detailed design
