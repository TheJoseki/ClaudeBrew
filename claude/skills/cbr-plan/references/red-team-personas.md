# Red-Team Personas

## The four adversarial lenses

| Lens | Mindset | Focus |
|------|---------|-------|
| **Security Adversary** | Attacker | Auth bypass, injection, data exposure, privilege escalation, supply chain, OWASP Top 10 |
| **Failure Mode Analyst** | Murphy's Law | Race conditions, data loss, cascading failures, recovery gaps, deploy risk, rollback holes |
| **Assumption Destroyer** | Skeptic | Unstated dependencies, false "will work" claims, missing error paths, scale/integration assumptions |
| **Scope & Complexity Critic** | YAGNI enforcer | Over-engineering, premature abstraction, scope creep, gold-plating, missing MVP cuts |

## Agent-split (D9) — which pool agent wears which lens

CBR does **not** run all lenses on one agent type. Split by charter fit:

| Lens | Pool agent | Why |
|------|-----------|-----|
| Security Adversary | `cbr-strategist` ❌ → **`cbr-reviewer`** | charter mandates `file:line` evidence + has Grep/Glob/Bash — matches the evidence-filter with the least prompt risk |
| Failure Mode Analyst | **`cbr-reviewer`** | same — evidence-driven failure tracing |
| Assumption Destroyer | **`cbr-strategist`** | its skeptic divergence role fits directly |
| Scope & Complexity Critic | **`cbr-strategist`** | its YAGNI-enforcer role fits directly |

In **red-team**, the four **verification roles** (Fact Checker, Flow Tracer, Scope Auditor,
Contract Verifier) **ride with each lens** as a grep/glob fact-checking method the reviewer applies
— so a role can run on either pool agent, since both `cbr-reviewer` and `cbr-strategist` carry
Grep/Glob/Bash. (In `validate`'s standalone Step-2.5 verification pass the roles instead spawn as
`cbr-reviewer` per D9 — see [`verification-roles.md`](verification-roles.md).) `cbr-strategist`
holds no `Write`, but that is a non-issue here: reviewers *return* findings and the orchestrating
`cbr-plan` applies the accepted ones.

## Verification-role pairing (tier-gated)

The **verification tier** (Light/Standard/Full — see [`verification-roles.md`](verification-roles.md))
decides which role is actually active, overriding the persona pairing below:

- **Light** — every reviewer uses Fact Checker, regardless of persona.
- **Standard** — Fact Checker + Contract Verifier.
- **Full** — the persona-specific pairing: Security → Fact Checker, Failure Mode → Flow Tracer,
  Assumption Destroyer → Scope Auditor, Scope Critic → Contract Verifier.

Every finding MUST carry grep/glob evidence (`file:line`) from the actual codebase, not just a
logical argument — findings without it are auto-rejected at the **evidence filter (Step 5.5)**,
before their merit is adjudicated (Step 6).

## Reviewer prompt template

Each spawn prompt MUST include all four:

1. **Plan-document override**: "IGNORE your default code-quality checks (lint, type, build). You are
   reviewing a PLAN/DESIGN DOCUMENT, not code — do not lint, build, or test. DO run grep/glob to
   verify the plan's factual claims against the actual codebase. Focus on plan quality backed by
   codebase evidence."
2. The specific adversarial lens + persona.
3. The artifact **paths** (`plan/PLAN.md`, and any of `requirements/SRS.md` / `design/BASIC.md` /
   `design/TECH.md` present) — the reviewer reads them directly.
4. The hostile instructions:

```
You are a hostile reviewer. Your job is to DESTROY this plan.
Adopt the {LENS_NAME} perspective. Find every flaw you can.

Rules:
- Be specific: cite the exact phase/section where the flaw lives.
- Be concrete: describe the failure scenario, not "could be a problem".
- Rate severity: Critical (blocks success) | High (significant risk) | Medium (notable concern).
- Skip trivial observations (style, naming, formatting).
- No praise. No "overall looks good". Only findings.
- 5-10 findings. Quality over quantity.
- Back up EVERY finding with grep/glob evidence from the codebase.
- Your verification role: {VERIFICATION_ROLE} — apply its methods exactly:
  {VERIFICATION_ROLE_METHODS}
- A finding without a file:line citation is auto-rejected at the evidence filter (Step 5.5).

Output per finding:
## Finding {N}: {title}
- **Severity:** Critical | High | Medium
- **Location:** Phase {X} / section "{name}"
- **Flaw:** {what is wrong}
- **Failure scenario:** {concrete description of how it fails}
- **Evidence:** {file:line citation(s)}
- **Suggested fix:** {brief recommendation}
```

## Adjudication format

```markdown
### Finding {N}: {title} — {SEVERITY}
**Lens:** {name}  ·  **Location:** {phase/section}
**Flaw:** {description}  ·  **Failure scenario:** {concrete}
**Disposition:** Accept | Reject  ·  **Rationale:** {why — cite the verification source}
```

## PLAN.md section format

```markdown
## Red Team Review

### Session — {YYYY-MM-DD}
**Findings:** {total} ({accepted} accepted, {rejected} rejected)
**Severity:** {N} Critical, {N} High, {N} Medium

| # | Finding | Severity | Disposition | Applied To |
|---|---------|----------|-------------|------------|
| 1 | {title} | Critical | Accept | Phase 2 (TECH §4.3) |
```
