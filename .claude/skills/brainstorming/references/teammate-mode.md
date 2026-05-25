# Team (Teammate) Brainstorming with a Claude Code Agent Team

Team mode runs the brainstorm as a Claude Code **agent team**: several teammates,
each its own Claude Code session with its own context window, explore the problem
from distinct angles and **challenge each other** before the lead synthesizes.
The value is structured disagreement — it defeats the anchoring bias a single
reasoner falls into ("find one plausible answer and stop").

Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (already set in this project's
`.claude/settings.json`). Reference: https://code.claude.com/docs/en/agent-teams

## When to use team mode

Recommend it (Phase 0) when the problem is **broad, ambiguous, high-stakes, or
spans multiple domains** — where parallel exploration and debate beat one line of
reasoning. For narrow or well-bounded requests, single mode is cheaper and just
as good. Teammates cost significantly more tokens, so always show your reasoning
and get the user's confirmation before spawning them.

## Roles — design for disagreement

Spawn teammates with **deliberately different lenses** so they surface different
concerns and can challenge each other. A strong default trio for brainstorming:

- **Product / UX** — user value, jobs-to-be-done, simplest thing that delivers it.
- **Technical architect** — feasibility, architecture, data, integration, cost.
- **Devil's advocate / risk** — attacks both: hidden assumptions, failure modes,
  security, scope creep, "why this will go wrong."

Add a **domain expert** when the topic needs specialized knowledge (e.g.
payments, healthcare, ML). Keep it to 3-5 teammates — the docs note diminishing
returns and rising coordination cost beyond that. If a reusable
[subagent definition](https://code.claude.com/docs/en/sub-agents) fits a role,
spawn the teammate from it.

## How the lead orchestrates

The lead is the session running this skill. The concrete tool lifecycle below is
**verified** (run end-to-end on this project), not just transcribed from docs:

1. **Create the team.** `TeamCreate(team_name, agent_type, description)` — this
   provisions both the team config and a shared task list.
2. **Spawn the roles** with the `Agent` tool, one call per teammate, all in one
   message so they run concurrently. Set `team_name`, a role `name` (e.g.
   `product-ux`, `architect`, `devils-advocate`), and `subagent_type`
   (`general-purpose` for teammates that need web/Context7 research; read-only
   `Explore` works for pure research roles but can't write files). Give each a
   **self-contained spawn prompt** — teammates do NOT inherit the lead's
   conversation history, so include the problem statement, the relevant context
   from Phase 1, the findings/URLs from Phase 2, and the specific lens that
   teammate owns. Spawning is **asynchronous**: the call returns "the agent is
   now running", and each teammate's brief arrives automatically as a new turn
   when it finishes. **Wait, do not poll** — this is harness-tracked work; a
   timer-based poll just burns tokens.
3. **Set the task: explore, then debate.** Each teammate investigates its angle
   AND is told to challenge the others' positions — like a scientific debate. The
   theory that survives cross-examination is far more likely to be right. To run
   an exchange, `SendMessage(to: "<name>", message: "...")` — either lead→teammate
   (relay one teammate's claim and ask them to defend or revise) or
   teammate→teammate directly. A genuine position change from a teammate (not the
   lead overruling) is the signal the debate is working.
4. **Run the clarify loop through the lead.** The never-guess rule still holds:
   when the team surfaces an uncertainty only the user can resolve, the **lead**
   batches it into an `AskUserQuestion` (teammates do not interrogate the user
   directly). Feed the answer back to the relevant teammates.
5. **Run DAR for trade-offs collaboratively.** Use teammates' competing
   positions as the alternatives and evidence feeding the DAR matrix
   (`dar-analysis.md`).
6. **Synthesize.** The lead consolidates the debate into 2-3 approaches, gets the
   user's incremental approvals, and writes the single shared artifact
   (`artifact-template.md`). Teammates contribute; the lead owns the artifact so
   there is one coherent voice.
7. **Tear down (verified sequence).** When the team's work is done, shut each
   teammate down with `SendMessage(to: "<name>", message: {type:
   "shutdown_request", reason: "..."})`; each replies `shutdown_approved` and
   terminates. Once **all** members have terminated, call `TeamDelete` (it fails
   if any member is still active, so always shut down first — only the lead should
   run cleanup). The lead can finish synthesis and write the artifact solo after
   teardown; it does not need the teammates alive for that.

## Caveats (from the agent-teams docs)

- **In-process mode** (this project's `teammateMode`) has known limits: no
  session resumption for teammates (`/resume` won't restore them), task status
  can lag, and shutdown can be slow. If a teammate is lost after a resume, spawn
  a replacement.
- **One team at a time**, **no nested teams** (teammates can't spawn their own
  team), and the **lead is fixed** for the team's lifetime.
- **Avoid file conflicts.** Only the lead writes the artifact; teammates produce
  findings, not edits to the shared file.
- **Token cost scales with teammates** — another reason to confirm with the user
  first and keep the team small.
