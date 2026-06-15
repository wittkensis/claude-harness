---
triggers: [chain of thought, think through, reason step by step, complex problem, confidence, meta-cognitive, decompose, analyze carefully]
description: Structured meta-cognitive reasoning for complex problems. Decompose → solve with confidence scores → verify → synthesize → reflect. Use when facing ambiguous decisions, multi-constraint tradeoffs, or problems where the first obvious answer may be wrong.
---

# Chain of Thought

For complex problems where the first answer may be wrong. Skip to direct answer for simple questions.

## Process

### 1. DECOMPOSE
Break into sub-problems. Name each explicitly.

### 2. SOLVE
Address each sub-problem with explicit confidence (0.0–1.0).
- "Sub-problem A: [answer]. Confidence: 0.8 because [reasoning]."
- State assumptions that would change the answer

### 3. VERIFY
For each sub-answer:
- Is the logic sound?
- Are facts accurate?
- Is coverage complete?
- Is there hidden bias?

### 4. SYNTHESIZE
Combine sub-answers, weighted by confidence.
- If sub-problems have conflicting answers, resolve explicitly
- Overall confidence = weighted average, penalized for conflicts

### 5. REFLECT
If overall confidence < 0.8:
- Identify the weakest link
- Ask: what would I need to know to raise confidence?
- Either research that gap or state it as a caveat
- Retry if information is obtainable

## Output Format

```
**Sub-problem 1:** [question]
→ [answer]. Confidence: 0.85 | Assumption: [X]

**Sub-problem 2:** [question]
→ [answer]. Confidence: 0.6 | Gap: [what I don't know]

**Synthesis:** [combined answer]
**Confidence:** 0.72
**Key caveat:** [the thing that would change this]
```

## When to Use

- Architectural decisions with multiple valid approaches
- Debugging where the cause is genuinely ambiguous
- Trade-off analysis with conflicting stakeholder needs
- Any response where the user says "think carefully" or "what's your confidence"
- Situations where being wrong has high cost

## When NOT to Use

- Simple factual questions
- Tasks with clear known solutions
- When the user needs speed over rigor
