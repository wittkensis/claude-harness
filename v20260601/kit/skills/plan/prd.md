---
name: to-prd
description: Turn the current conversation context into a structured PRD. Use when user wants to create a PRD from the current context, formalize requirements, or document a feature spec.
---

Synthesize the current conversation context and codebase understanding into a PRD. Do NOT interview the user — just synthesize what you already know.

## Process

1. Explore the repo to understand current state. Use domain vocabulary throughout.
2. Sketch major modules to build/modify. Identify opportunities for deep modules (simple testable interface, rich implementation).
3. Check with user that modules match expectations. Confirm which need tests.
4. Write the PRD using the template below.

## PRD Template

```markdown
## Problem Statement
[The user's problem, from the user's perspective]

## Solution
[The solution, from the user's perspective]

## User Stories
[Numbered list — extensive, cover all aspects]
1. As a <actor>, I want <feature>, so that <benefit>

## Implementation Decisions
- Modules to build/modify
- Interface changes
- Architectural decisions
- Schema changes
- API contracts
(No specific file paths or code snippets unless from a prototype)

## Testing Decisions
- What makes a good test (behavior, not implementation)
- Which modules get tests
- Prior art in the codebase

## Out of Scope
[What's explicitly excluded]

## Further Notes
[Anything else]
```
