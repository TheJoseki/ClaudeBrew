---
name: retro
description: "Retrospective on a delivered feature, phase, or sprint. TRIGGER: user asks for a retro, post-mortem, or lessons-learned review after delivery. Reads the feature's own artifacts (SRS, TECH, review, test, security reports) plus git history, then produces 5-Why root-cause analysis, Lessons Learned per category, git velocity metrics, and prioritized Action Items. Output saved to the feature's work-stream folder (docs/streams/[feature]-*/retro/). NOT FOR: work still in progress (use a handoff/session summary instead)."
allowed-tools: Read, Grep, Glob, Bash, Write
disable-model-invocation: false
argument-hint: "[feature|phase|sprint name]"
metadata:
  version: "4.0"
  category: core-sdlc
---

# Retro

$ARGUMENTS

---

## Step 0: Mode Detection

Parse `$ARGUMENTS` to determine retro mode and scope:

| Pattern | Mode | Example |
|---------|------|---------|
| `feature [name]` | Full-feature retro (all phases) | `feature user-auth` |
| `phase [phase] [name]` | Single-phase retro | `phase Phase6 user-auth` |
| `sprint [date-range]` | Time-boxed sprint retro | `sprint 2026-03-01..2026-03-15` |
| *(no args)* | Prompt user to specify | — |

Determine `[feature-name]` and `[scope]` before proceeding.
Auto-create the `retro/` subfolder of the target stream if it does not exist
(for `sprint` mode, the `docs/streams/sprint-[YYYYMMDD]/retro/` folder — see Step 6).

**Precondition:** the scope must be finished (delivered feature, closed phase, ended sprint). If work is still in progress, stop and say so — a retro on live work produces guesses, not lessons.

---

## Step 1: Collect the Evidence

Glob for the artifacts that exist, then read them. Missing artifacts are themselves a finding — record which ones are absent rather than inventing content.

All artifacts live under the feature's stream folder `docs/streams/[feature]-*/`
(glob the `*` — the folder date is the stream-start date). Read from these
sub-folders:

| Perspective | Artifacts to read |
|-------------|-------------------|
| Requirements | `docs/streams/[feature]-*/requirements/SRS.md` |
| Design | `docs/streams/[feature]-*/design/TECH.md`, `docs/streams/[feature]-*/design/BASIC.md` |
| Implementation | `docs/streams/[feature]-*/work-logs/DEV-*.md` (all batches) |
| Code review | `docs/streams/[feature]-*/reviews/REVIEW-*.md` (all batches) |
| Security | `docs/streams/[feature]-*/security/SEC-*.md` |
| Unit test | `docs/streams/[feature]-*/test-reports/UTR-R*.md` (all rounds), `docs/streams/[feature]-*/test-cases/UTC.md` |
| Integration test | `docs/streams/[feature]-*/test-reports/ITR-R*.md` (all rounds), `docs/streams/[feature]-*/test-cases/ITC.md` |

**Scope filter by mode:**

| Mode | Read |
|------|------|
| `feature` | All rows above |
| `phase PhaseN` | Only the rows for that phase (e.g. Phase 6 → unit test rows; Phase 4 → implementation + code review) |
| `sprint` | Implementation, code review, and test rows for artifacts modified inside the date range (`git log --since --until --name-only`) — skip SRS |

Use `Grep` for `Critical`, `Major`, `REOPENED`, and `BLOCKED` across the collected files to locate the high-signal passages before reading in full.

---

## Step 2: Per-Stage Observations

For each perspective with artifacts present, write 3–6 factual bullets. **Every bullet cites the file it came from.** No bullet may assert something the artifacts do not show.

| Perspective | What to extract |
|-------------|----------------|
| Requirements | AC precision (were any ambiguous?); scope changes after G1; gates marked REOPENED and why |
| Implementation | What was delivered; blockers in the work logs; scope drift vs the TECH spec (compare planned vs actual) |
| Code review | Critical/Major counts per batch; patterns recurring across >1 batch or >1 file; whether `CODING-CHECKLIST.md` covered them |
| Security | Findings by OWASP category; whether they were introduced by a pattern already in the guardrails |
| Unit test | Pass rate per round R1..Rn; failures grouped by type (null ref, auth, validation, business logic); coverage gaps vs the TECH spec |
| Integration test | API and E2E pass rates per round; failure categories (auth flow, data consistency, cross-module assumptions, timing); env-vs-prod differences |

A perspective with no artifacts gets one line: `No [type] artifact found — [what that prevents assessing].`

---

## Step 3: 5-Why on the Top 3 Issues

Rank candidate issues by cost, then take the top 3:

- Critical/High findings in review or security
- Any phase that needed more than R2 test rounds
- Gates marked REOPENED
- Blockers that caused scope drift

For each:

```markdown
### Issue #N: [Issue Title]
**Source**: [artifact file this came from]
**Impact**: [what it cost — extra rounds, gate failure, scope drift]

| Step | Why? | Answer |
|------|------|--------|
| Why 1 | Why did [issue] occur? | [answer] |
| Why 2 | Why [answer from Why 1]? | [answer] |
| Why 3 | Why [answer from Why 2]? | [answer] |
| Why 4 | Why [answer from Why 3]? | [answer] |
| Why 5 | Why [answer from Why 4]? | [root cause] |

**Root Cause**: [concise statement]
**Action Item**: [specific, actionable change to prevent recurrence]
```

Stop early if the chain reaches a genuine root cause before Why 5 — say so rather than padding.

---

## Step 4: Lessons Learned

Synthesize across all perspectives into 4 categories:

```markdown
### Lesson Learned

**Process:**
- [What process step was missing or insufficient]
- [What workflow change would prevent recurrence]

**Design:**
- [What architectural or design decision caused downstream issues]
- [What design pattern or checklist item should be added]

**Testing:**
- [What testing gap allowed bugs through to later rounds]
- [What test infrastructure or strategy change is needed]

**Security:**
- [Only if security findings occurred] What vulnerability pattern should be added to guardrails
```

---

## Step 5: Git Metrics

Collect velocity and quality metrics with read-only git commands:

```bash
# Commit count
git log --oneline --since="[start]" --until="[end]"

# LOC added/removed
git diff --stat [start-commit]..[end-commit]

# Fix ratio (fix: commits vs total)
git log --oneline --since="[start]" | grep -c "^"
git log --oneline --since="[start]" | grep -c "fix:"

# Delivery streak (days with at least 1 commit)
git log --format="%ad" --date=short --since="[start]" | sort -u | wc -l
```

For `feature`/`phase` mode, derive the date range from the artifacts' own timestamps if the user did not supply one.

```markdown
### Metrics

| Metric | Value |
|--------|-------|
| Commits | N |
| LOC added | +N |
| LOC removed | -N |
| Fix ratio | N% (M fix commits / N total) |
| Test rounds avg | R[n] |
| Gate reopens | N |
| Delivery streak | N active days |
```

**Note**: If git history is unavailable or the start date is unknown, skip metrics and write `N/A — git baseline unavailable`. Never estimate them.

---

## Step 6: Write the Report

| Mode | Path |
|------|------|
| `feature [name]` | `docs/streams/[name]-*/retro/RETRO-[YYYYMMDD].md` |
| `phase [phase] [name]` | `docs/streams/[name]-*/retro/RETRO-phase-[phase]-[YYYYMMDD].md` |
| `sprint [date-range]` | `docs/streams/sprint-[YYYYMMDD]/retro/RETRO-[YYYYMMDD].md` |

`feature`/`phase` retros land in that feature's own work-stream folder (the
folder carries the slug, so the filename drops it; the RETRO date is time-series).
A `sprint` retro spans many streams and has no single feature identity, so it gets
its **own** stream folder keyed by the sprint's end date —
`docs/streams/sprint-[YYYYMMDD]/` (folder = identity).

```markdown
# Retro: [Feature/Sprint Name] — [YYYY-MM-DD]

**Mode**: [feature | phase | sprint]
**Scope**: [phases covered]
**Sources**: [list the artifact files actually read]

---

## 1. Delivery Summary
[2-3 sentences: what was delivered, gate results summary]

---

## 2. Stage Observations
### Requirements / Design / Implementation / Code Review / Security / Unit Test / Integration Test
[Step 2 bullets, each citing its source file. Omit stages with no artifacts, or list them under "Missing Artifacts".]

---

## 3. Top Issues — 5 Why Analysis
[Issue #1 / #2 / #3 blocks]

---

## 4. Lesson Learned
[Process / Design / Testing / Security]

---

## 5. Metrics
[Metrics table]

---

## 6. Action Items

| Priority | Action | Owner | Scope | Due |
|----------|--------|-------|-------|-----|
| HIGH | [specific action] | [owner] | next feature | [date] |
| MEDIUM | [specific action] | process | process-wide | [date] |
| LOW | [specific action] | [owner] | optional | — |
```

**Present to user:** show the Action Items table only, plus the report path. The user reads the full report in the stream's `retro/` folder.

Then **stop.** Do not open the action items as work — the user decides what gets picked up.

---

## Lifecycle Placement

The user invokes this skill after delivery, or at any completed checkpoint:

```
After delivery                        → /cbr:retro feature [name]
After a completed phase               → /cbr:retro phase Phase6 [feature]
End of sprint (bi-weekly)             → /cbr:retro sprint [date-range]
Post-incident review                  → /cbr:retro feature [affected-feature]
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Run retro while the feature is still in progress | Wait for the scope to close — mid-flight retros produce guesses |
| Assert a finding the artifacts don't support | Cite the source file for every observation; write "no artifact found" when there isn't one |
| Silently skip a missing artifact | List it under Missing Artifacts — the gap is itself a finding |
| Write vague action items ("improve testing") | Write specific, ownable actions ("Add boundary tests for null input in UserService") |
| Run 5 Why on every minor issue | Focus 5 Why on the top 3 issues only — minor issues go straight to Action Items |
| Estimate git metrics when history is unavailable | Write `N/A — git baseline unavailable` |
| Skip retro for "simple" features | Simple features often carry the most surprising lessons |
