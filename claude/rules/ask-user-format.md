# AskUserQuestion Standard Format

> All skills and pool agents MUST follow this format when asking users questions.
> Adapted from gstack's standardized question format for ClaudeBrew's gated workflow.

## 4-Part Format (Mandatory)

### 1. RE-GROUND (1-2 sentences)
- State: project name + current git branch + current task/phase
- Assume user hasn't looked at this window for 20 minutes
- Example: "Working on feature user-auth (branch: feature/user-auth), Phase 3 Detail Design."

### 2. SIMPLIFY
- Plain language a smart 16-year-old could follow
- Say what it DOES, not what it's CALLED
- No raw function names, internal jargon, or implementation details
- Use concrete examples and analogies
- Example:
  - BAD: "Should I refactor the DTO validation pipe in the CreateUserDto?"
  - GOOD: "Should I add input checking so invalid data gets rejected before reaching the database?"

### 3. RECOMMEND
- Format: "RECOMMENDATION: Choose [X] because [one-line reason]"
- Include Completeness score: X/10 per option
  - 10 = full implementation with all edge cases and full test coverage
  - 7 = happy path covered, edge cases deferred
  - 3 = shortcut, significant work deferred to later
- Prefer complete option when marginal effort is low (AI makes completeness near-free)

### 4. OPTIONS
- Lettered: A) B) C) — max 4 options
- Include effort when relevant: (estimated: ~X hours)
- Always include a "do nothing / skip" option if applicable

## Question Batching Rule

- Batch related decisions into ONE AskUserQuestion call (not one question per finding)
- If code review has 5 ASK findings: present them as A/B/C/D/E choices in a single question
- If multiple independent decisions exist: group by topic, present in order of priority

## Anti-Patterns (NEVER do)

- Do not ask without re-grounding context first
- Do not use jargon without explaining what it means
- Do not recommend shortcuts when the complete option costs modest extra effort
- Do not ask multiple separate questions when one batched question works
- Do not show effort only in human terms — include AI-assisted estimate when relevant
