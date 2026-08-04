# Brainstorming Artifact Template

This is the **handoff contract** for the SDLC pipeline. Stage 2 (`requirement`)
and every later stage read this file as their starting input, so completeness and
honesty here directly determine downstream quality. Fill every section. If a
section genuinely does not apply, write `Not applicable —` followed by the
one-line reason; never leave it blank or as a placeholder.

Write the file to `docs/streams/<slug>-<YYYYMMDD>/brainstorm/BRAINSTORM.md` (inside
the work-stream folder brainstorming scaffolds — the folder carries the slug, so the
filename drops it).

## Template

```markdown
---
stream: <slug>-<YYYYMMDD>          # persistent cross-artifact identity (required)
---

# Brainstorm: <Topic>

- **Date:** YYYY-MM-DD
- **Mode:** single | team
- **Status:** approved            <!-- only set once the user approves -->
- **Author:** brainstorming skill

## 1. Problem statement & context
What problem are we solving and why now? The situation today, the pain, and what
triggered this. Two to four sentences — no solutions yet.

## 2. Stakeholders & personas
Who is affected and who decides. End users, operators, business owners, etc. For
each, a one-line "who they are and what they need."

## 3. Goals & success criteria
What success looks like, stated **measurably** wherever possible (e.g. "p95
latency < 200ms", "onboarding in under 3 minutes", not "fast" / "easy").

## 4. Scope & non-scope
- **In scope:** what this effort will deliver.
- **Out of scope:** what it explicitly will NOT deliver. The non-scope list
  prevents downstream scope creep and is as important as the in-scope list.

## 5. Constraints
Technical, business, regulatory, timeline, budget, and team constraints that
bound the solution space.

## 6. Assumptions
Every assumption that survived the clarify loop, each with:
- the assumption,
- a **confidence label** (confirmed-by-user | high | medium | low),
- how it was validated (user answer, research citation, or "still open").
Confirmed-by-user assumptions are the strongest; treat low-confidence ones as
risks.

## 7. Open questions (carried forward)
Questions that do NOT need to be answered to finish brainstorming, but that the
`requirement` stage MUST close. This is the explicit to-do list handed to Stage 2.

## 8. Considered approaches & decisions
The audit trail of the divergent motion — what was on the table, not just what won:
- **Problem framings** (when problem-first inversion ran): the ≥3 framings explored
  and which one was adopted (see problem-first.md).
- **Options generated** (the divergent range — obvious / minimal / inverted / wild),
  each with a one-line essence, so the reasoning is reconstructable.
- For each significant decision, a **Decision Record** (see dar-analysis.md): the
  decision and alternatives considered; the DAR criteria, weights, and scores (or a
  note that the choice was minor and reversible, so DAR was skipped); the chosen
  option and rationale.

## 9. Recommended approach
The synthesized direction: which approaches won and how they fit together — the spine
the requirement stage elaborates. State **what would change this recommendation** (the
condition under which you would switch), so downstream stages know what to watch.

## 10. Risks & mitigations
Each known risk with: likelihood, impact, and a mitigation or contingency.

## 11. References
Every source cited during research, as markdown links, each tagged with what it
backs (e.g. "[OWASP ASVS](url) — auth requirements"). This is the source-of-truth
trail behind the recommendations.

## 12. Handoff notes
One paragraph telling the `requirement` stage where to start: the most important
constraints, the open questions to prioritize, and anything fragile.
```

## Quality bar

Before this artifact is shown for approval, it must contain **zero** placeholders,
**zero** unlabeled assumptions, and **zero** uncertainties that were named while
clarifying but never resolved. An open question deliberately
deferred to Stage 2 belongs in §7 — that is different from an unresolved
uncertainty, which is a defect.
