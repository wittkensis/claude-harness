---
triggers: [figjam, figma diagram, diagram, mermaid, generate diagram, flowchart, architecture diagram, schema diagram]
description: FigJam diagramming — Eric's stylistic preferences, color system, Mermaid constraints, and workflow for generating diagrams into existing boards.
---

# FigJam Diagramming

## Workflow

1. **Always add to an existing board** — never create a new file unless explicitly asked.
2. If the user provides a FigJam URL, extract the `fileKey` from it: `figma.com/board/{fileKey}/...`
3. Always use `planKey: "team::1164747565436972595"` (Ericville) unless the user specifies otherwise.
4. Call `whoami` first only if you don't have the planKey yet.
5. For multiple diagram variants, call `generate_diagram` in parallel.

## Direction defaults

| Diagram type | Direction |
|---|---|
| Pipeline / workflow / deployment | LR (left-to-right) |
| Layer stack / hierarchy / schema | TD (top-down) |
| Combined layer + trust view | TD |

## Node label format

Always include a one-line purpose description in every node:

```
NODE["table_name — brief purpose, max ~60 chars"]
```

Use `—` (em dash) as the separator. Keep descriptions factual and specific, not generic ("stores data about X" is bad; "all P-number aliases: museum, excavation, publication IDs" is good).

## Color system

Color encodes **meaning**, not decoration. Apply via `classDef` + `:::className`.

### Data layer palette (schema diagrams)
```
L0 Identity:    fill:#5C2E0E,color:#fff   dark brown
L1 Physical:    fill:#7A3B1E,color:#fff   terracotta
L2 Graphemic:   fill:#9B6C1A,color:#fff   amber
L3 Reading:     fill:#3A6B20,color:#fff   olive
L4 Linguistic:  fill:#1A6644,color:#fff   forest green
L5 Semantic:    fill:#1A4D6E,color:#fff   slate blue
Knowledge Graph: fill:#12324A,color:#fff  deep navy
```

### Trust / provenance palette
```
Human/scholar:   fill:#1A4F7A,color:#fff   blue
ML model:        fill:#5B2C6F,color:#fff   purple
Ingestion/import: fill:#1D6A39,color:#fff  green
annotation_runs spine: fill:#1C2833,color:#fff  near-black
```

### Secondary / structural
```
Audit (evidence, decisions, threads): fill:#515A5A,color:#fff  medium gray
Join tables:                          fill:#717D7E,color:#fff  lighter gray
```

### classDef boilerplate (schema diagrams)
```mermaid
classDef c0 fill:#5C2E0E,color:#fff,stroke:#5C2E0E
classDef c1 fill:#7A3B1E,color:#fff,stroke:#7A3B1E
classDef c2 fill:#9B6C1A,color:#fff,stroke:#9B6C1A
classDef c3 fill:#3A6B20,color:#fff,stroke:#3A6B20
classDef c4 fill:#1A6644,color:#fff,stroke:#1A6644
classDef c5 fill:#1A4D6E,color:#fff,stroke:#1A4D6E
classDef ckg fill:#12324A,color:#fff,stroke:#12324A
classDef human fill:#1A4F7A,color:#fff,stroke:#1A4F7A
classDef ml fill:#5B2C6F,color:#fff,stroke:#5B2C6F
classDef imp fill:#1D6A39,color:#fff,stroke:#1D6A39
classDef core fill:#1C2833,color:#fff,stroke:#1C2833
classDef audit fill:#515A5A,color:#fff,stroke:#515A5A
classDef jt fill:#717D7E,color:#fff,stroke:#717D7E
```

## Mermaid constraints (FigJam-specific)

- **No `\n`** in node labels — FigJam does not render newlines in Mermaid text.
- **Quote all node and edge text** in `graph`/`flowchart`: `["Text"]`, `-->|"Edge label"|`
- Color styling only works in `graph` and `flowchart` types — not `sequenceDiagram`, `gantt`, `stateDiagram`.
- No emojis in Mermaid code.
- Dashed cross-cutting arrows: `A -.->|"label"| B` — use for FKs that span layers (e.g. `annotation_run_id`).
- Subgraph IDs must be unique short strings (`L0`, `L1`, `PROV`, `CITE`).
- Connect **nodes to nodes**, not subgraph-to-subgraph, for FK relationships.

## Schema diagram conventions

### Show secondary tables
Always include: join tables, evidence tables, decision tables, discussion thread tables, audit logs. These are styled gray (`:::audit` or `:::jt`) but must appear — they're not optional.

### Comprehensiveness vs clutter
Collapse a group only if there are 5+ identical-purpose tables (e.g. "5 discussion thread types" → one node labeled `discussion_threads (5 types)`). Otherwise show individually.

### Cross-cutting provenance spine
`annotation_runs` connects to every annotated table via dashed arrows:
```
ARUN -.->|"annotation_run_id"| SANN
ARUN -.->|"annotation_run_id"| TREA
ARUN -.->|"annotation_run_id"| LEMM
```
Place `annotation_runs` outside the layer subgraphs so it reads as infrastructure, not a layer.

## Preferred diagram types

| Use case | Type |
|---|---|
| Pipeline / deployment flow | `flowchart LR` |
| Schema layer architecture | `flowchart TD` with subgraphs |
| Combined layer + trust | `flowchart TD` with trust sources at top |
| Key relationships only | `erDiagram` |
| Data journey / process | `sequenceDiagram` (no color) |

## When proposing multiple variants

When asked to propose options: generate all variants in parallel with clearly differentiated organizing principles — not just layout changes. Good axes of difference:
- Architectural (what layer?) vs Trust (who said it?) vs Relational (how does it connect?)
- Process (data journey) vs Structure (ER diagram) vs Lifecycle (state machine)
