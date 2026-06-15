---
name: design
description: Visual design, UX architecture, and diagramming. Routes to Figma extraction, UX/IA patterns, and FigJam diagrams. Structure before style — IA and flows before visual polish.
---

# Design

## Specialties

| File | When |
|------|------|
| [figma.md](figma.md) | Extracting tokens and components from Figma via MCP |
| [ux-architecture.md](ux-architecture.md) | IA, sitemaps, object models, user flows, navigation patterns |
| [ux-process.md](ux-process.md) | Design process order, accessibility, component states, decision gates |
| [figjam.md](figjam.md) | FigJam diagram style, color system, Mermaid constraints |

## Default Design System

There is **no built-in design system in this port** — the home machine's design-system tokens
did not travel. Establish the work design system from one of:

```
Existing work brand/design system? → map tokens from it (see figma.md)
Greenfield with brand guidelines?   → create project tokens from the brand
No brand yet?                        → present options with trade-offs, then commit one
```

Record the chosen tokens in the project and reference them consistently — don't re-decide per screen.

## Design Order

**Structure before style. Never skip phases:**

1. Strategic Foundation (goals, personas)
2. Information Architecture (objects, relationships)
3. Navigation Strategy
4. Wireframes
5. Component Design
6. Visual Design (last)
