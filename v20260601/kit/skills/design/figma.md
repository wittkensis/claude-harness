---
triggers: [figma, design extraction, figma mcp, design tokens, figma to code]
description: Extract design systems and components from Figma efficiently using MCP
---

# Figma Design Extraction

## Overview

Extract design tokens, components, and patterns from Figma files using the Figma MCP server. Optimized for context efficiency and Tailwind integration.

---

## MCP Server Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `get_metadata` | XML outline of file structure | **Always first** - maps nodes without context overload |
| `get_variable_defs` | Extract design tokens | Token extraction (colors, spacing, typography) |
| `get_design_context` | Full component structure | After identifying target nodes |
| `get_screenshot` | Visual reference | Verify layout accuracy |
| `get_code_connect_map` | Link to existing components | Check for existing implementations |

---

## Extraction Workflow

### Step 1: Map File Structure

**Always start here** to avoid context overflow:

```
> Use Figma MCP: get_metadata for [file URL]
```

This returns a sparse XML outline with node IDs, names, and types. Use this to identify:
- Design token pages
- Component frames
- Target sections

### Step 2: Extract Design Tokens

```
> Use Figma MCP: get_variable_defs for [file URL]
```

Returns token definitions including:
- Colors (with hex values)
- Spacing values
- Typography settings
- Custom variables

### Step 3: Fetch Specific Components

**Never fetch entire pages.** Target specific nodes by ID:

```
> Use Figma MCP: get_design_context for node [node_id]
```

Process components in batches of 5-10 to manage context.

### Step 4: Visual Verification

```
> Use Figma MCP: get_screenshot for [file URL or node]
```

Compare generated code against visual reference.

---

## Token-to-Tailwind Mapping

### Color Tokens

Figma naming → Tailwind config:

```javascript
// From Figma: color/primary/500
// To tailwind.config.js:
colors: {
  primary: {
    500: '#3B82F6',
  }
}
```

### Typography Tokens

**Watch for differences:**
- Figma line-height: absolute pixels (e.g., 24px)
- CSS line-height: ratio (e.g., 1.5) or rem

```javascript
// Figma: font-size/lg = 18, line-height = 28
// Tailwind: text-lg with leading-7
fontSize: {
  lg: ['1.125rem', { lineHeight: '1.75rem' }]
}
```

### Spacing Tokens

Map to Tailwind 4px base scale:

| Figma Value | Tailwind Class |
|-------------|----------------|
| 4px | space-1 |
| 8px | space-2 |
| 12px | space-3 |
| 16px | space-4 |
| 24px | space-6 |
| 32px | space-8 |

---

## Output Formats

### Request Specific Frameworks

`get_design_context` supports format parameter:

| Format | Use Case |
|--------|----------|
| `react-tailwind` | Default, React + Tailwind |
| `vue-tailwind` | Vue projects |
| `html-css` | Static sites |
| `swiftui` | iOS apps |

---

## Context Optimization

### Budget Guidelines

| Action | Token Cost | Recommendation |
|--------|------------|----------------|
| `get_metadata` | Low (~500-1000) | Always use first |
| `get_variable_defs` | Low-Medium | Cache results |
| `get_design_context` | High (varies) | Target specific nodes |
| `get_screenshot` | Medium | Use sparingly |

### Efficient Patterns

<do>
  - Use `get_metadata` before any extraction
  - Target specific nodes by ID
  - Process components in batches (5-10)
  - Cache variable definitions (change infrequently)
  - Skip screenshots for token-only extraction
</do>

<do_not>
  - Fetch entire pages with `get_design_context`
  - Request all components at once
  - Re-fetch tokens that haven't changed
  - Use `get_design_context` without knowing target nodes
</do_not>

---

## Figma File Best Practices

For optimal extraction, advise users to structure their Figma files:

1. **Dedicated token page** - Separate from UI designs
2. **Semantic naming** - "CardContainer" not "Group 5"
3. **Auto Layout** - Communicates responsive intent
4. **Figma Variables** - Modern token system
5. **Component variants** - Rather than duplicate components

---

## Example Extraction Session

```markdown
1. "Get file structure overview"
   → Use get_metadata
   → Identify: Design Tokens page, Components frame

2. "Extract design tokens"
   → Use get_variable_defs
   → Map to tailwind.config.js

3. "Extract Button component"
   → From metadata, find Button node ID
   → Use get_design_context for that specific node
   → Generate component code

4. "Verify visual accuracy"
   → Use get_screenshot for Button node
   → Compare against generated code
```

---

## Integration with your design system

When extracting for your-design-system-based projects:

1. Map Figma tokens to existing your design system palette
2. Use `font-serif` for Libre Baskerville headings
3. Apply 15% opacity status pattern for semantic colors
4. Ensure dark mode is default

---

## Related Skills

- `frontend-design` - your design system design system patterns
- `tech-stacks` - Framework selection
- `code-architect` - Component implementation standards
