# UX Design

## Core Philosophy

**"Harmonizing people, business, & machines through trusted design."**

Never optimize for just one stakeholder. Design is collaborative discussion.

---

## Logical Order of Operations (never skip phases)

1. **Strategic Foundation** — goals, constraints, personas, success metrics
2. **Information Architecture** — mental models, object relationships, happy paths
3. **Navigation Strategy** — only after IA is solid
4. **Wireframes** — core templates based on IA
5. **Component Design** — behavior, states, variants, tokens
6. **Visual Design** — applied last to validated structure

---

## Accessibility (WCAG AA Minimum)

| Requirement | Value |
|-------------|-------|
| Text contrast | 4.5:1 |
| Large text / UI elements | 3:1 |
| Touch targets | 44×44px minimum |
| Keyboard navigation | All interactive elements |
| Focus indicators | Visible |

```html
<!-- Good -->
<button type="submit">Save Changes</button>

<!-- Bad -->
<div onclick="save()">Save Changes</div>
```

**Forms:** labels associated with inputs · errors linked to fields · required fields indicated · instructions before fields

---

## Component State Checklist

Every interactive component needs:
- [ ] Default
- [ ] Hover
- [ ] Focus (keyboard)
- [ ] Active/pressed
- [ ] Disabled
- [ ] Loading (if async)
- [ ] Error (if validation)
- [ ] Dirty State (if AI modified – accept, reject, refine)

---

## Responsive Breakpoints

```
Mobile:  < 640px
Tablet:  640px - 1024px
Desktop: > 1024px
```

---

## Decision Gates

Pause for user input at:
1. Persona definitions → before journeys
2. IA approach → before navigation
3. Visual direction → which aesthetic
4. Component strategy → architecture decisions
5. Trade-offs → when UX and business KPIs conflict

---

## Anti-Patterns

**NEVER:** Jump to wireframes before personas/journeys · design navigation before IA is solid · apply visual before structure validated · present single solution (always 2-3 with trade-offs) · ignore accessibility
**ALWAYS:** Ask about project context first · ground in user understanding · document decisions with rationale · present trade-offs honestly
