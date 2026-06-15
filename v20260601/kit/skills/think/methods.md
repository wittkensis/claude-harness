# Research Methods

## Core Philosophy

Question assumptions, seek disconfirming evidence, connect findings to decisions.

---

## Source Evaluation

**Tier 1 (High):** Peer-reviewed, primary data, authoritative reports
**Tier 2 (Medium):** Reputable journalism, industry publications, expert opinions
**Tier 3 (Low):** Unverified claims, promotional content, outdated info

**Rules:** Never single-source critical findings · cross-verify across 2+ independent sources · prefer sources < 2 years for fast-moving domains

---

## Research Types

| Type | Questions |
|------|-----------|
| Market Analysis | How big? Growing how fast? What segments? |
| Competitive Intelligence | Who competes? How positioned? Where's the gap? |
| User Research Synthesis | What patterns? What surprises? What validates assumptions? |
| Technology Assessment | What are the tradeoffs? Who uses it? Maintenance burden? |

---

## Report Structure

**Executive Summary (required):** 3-5 paragraphs answering — what was the question? what did we find? what does it mean for our decision?

**Body sections:**
1. Research Objectives
2. Methodology
3. Findings (with citations)
4. Analysis
5. Implications
6. Limitations
7. Next Steps

**Citation format:**
```
[Source Name, Date] - Brief relevance description
Credibility: Tier 1/2/3
URL or reference
```

---

## Hypothesis Testing

```markdown
## Hypothesis: [Statement]
**Origin:** Where did this assumption come from?
**Risk Level:** High/Medium/Low
**Test Method:** How to validate?
**Success Criteria:** How will we know if true/false?
**Status:** Proposed / In Progress / Validated / Invalidated
```

---

## Synthesis Techniques

**Pattern Recognition:** Group by theme, note frequency, identify outliers

**Contradiction Analysis:**
1. Check for different definitions
2. Check for different time periods
3. Check for different contexts
4. Note the disagreement explicitly

**Gap Identification:** What remains unanswered? What would change our recommendation?

---

## File Organization

```
/Research/
├── landscape.md       # Competitive/market
├── architecture.md    # Technical
├── user-needs.md      # User research
└── [topic]-analysis.md
```

---

## Quality Checklist

- [ ] Executive summary answers the core question
- [ ] All claims cited
- [ ] Sources evaluated for credibility
- [ ] Contradictions noted
- [ ] Limitations acknowledged
- [ ] Implications connected to decisions
- [ ] Findings triangulated

---

## Librarian Delegation

Delegate when:
- Market research requires 5+ sources
- Competitive analysis covers 3+ competitors
- Technology assessment compares multiple options

Request format:
```
"Research [topic] and summarize:
- Key findings (3-5 bullets)
- Source credibility assessment
- Recommendation with rationale
- Confidence level"
```

Returns ~500 token summary — keeps main context clean.
