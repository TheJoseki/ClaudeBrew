# Brainstorm: Houseplant Watering Tracker

- **Date:** 2026-05-25
- **Mode:** single
- **Status:** draft            <!-- set to "approved" only once the user approves -->
- **Author:** brainstorming skill

> **Process note.** The user declined the structured clarify-loop questions twice,
> which I read as a "stop asking, pick reasonable defaults" override. Per the
> never-guess playbook, that override is honored but logged: every default I picked
> appears in §6 as a **low-confidence assumption** and in §7 as a **carried-forward
> open question** for the `requirement` stage to confirm. Nothing guessed here
> travels downstream invisibly.

## 1. Problem statement & context
People who keep houseplants routinely lose track of which plants need watering and
when, leading to both under-watering (wilting) and over-watering (root rot — the
most common houseplant killer). There is no record today: the user is relying on
memory across a growing collection of plants with different needs. They want a
lightweight app to record their plants and tell them, at a glance, what needs
water now. This is a greenfield build — the repository contains no prior code.

## 2. Stakeholders & personas
- **Primary user — the plant owner (hobbyist):** owns a handful to a few dozen
  houseplants; wants a fast daily "what needs water today?" answer and a place to
  record each plant. Not necessarily technical; uses a phone most of the time.
- **Decision-maker — the requester (you):** approves scope and direction for each
  SDLC stage.
- **Future stakeholder — multi-household / sharing users:** explicitly *out of
  scope* for v1 (see §4); noted so the data model doesn't paint us into a corner.

## 3. Goals & success criteria
Measurable definition of "this works":
- **G1 — Fast capture:** a user can add a plant (name + watering interval) in
  **under 30 seconds**, with no account or setup.
- **G2 — Correct "due" logic:** the dashboard classifies every plant as **Overdue
  (N days)**, **Due today**, or **Next due in N days**, computed as
  `last_watered + interval_days` vs today's local date.
- **G3 — One-tap update:** marking a plant watered sets `last_watered = today` and
  recomputes the next-due date immediately.
- **G4 — Durable local data:** plant data and watering history **persist across
  browser restarts** with no backend and no login.
- **G5 — Offline + installable:** after first load the app **works offline** and
  is installable to a phone home screen (PWA); p95 first-contentful-paint
  **< 2s** on a mid-tier mobile.
- **G6 — History retained:** each plant keeps a **watering log** (timestamped
  entries) the user can review.
- **G7 — Recoverable:** the user can **export** all data to a file and **import**
  it back, so local-only storage is not a single point of permanent loss.

## 4. Scope & non-scope
**In scope (v1):**
- Create / read / update / delete plants.
- Per-plant **fixed watering interval** (`water every N days`), user-set.
- **Mark-as-watered** action; per-plant **watering history log**.
- **Dashboard** listing plants sorted by due status (overdue → due → upcoming).
- **Local persistence** via IndexedDB (no server, no account).
- **PWA**: installable + offline after first load.
- **JSON export / import** for backup and device migration.
- Per-plant metadata: name, room/location (free text), interval, last-watered
  date, free-text notes.

**Out of scope (v1) — explicitly NOT delivered:**
- Accounts, authentication, cloud sync, multi-device live sync, sharing.
- Species catalog / auto-suggested intervals (deferred; see §7 / §8 DAR-2).
- Weather- or season-adjusted scheduling.
- Push / email / calendar notifications (in-app dashboard only for v1).
- Fertilizing, repotting, light/sunlight, pest, or growth tracking.
- Native iOS / Android apps.
- Plant **photos** (deferred to open question §7 — adds blob storage concerns).
- Internationalization / multi-language (English only).

## 5. Constraints
- **Greenfield repo** with no build/test system yet; the chosen stack must bring
  its own (Vite handles this).
- **No backend budget assumed** — the v1 default is static files only, no server
  to run or pay for. (This is a *default*, not a user-confirmed constraint — see
  §6/§7.)
- **Platform reality:** iOS Safari historically limits PWA web-push; v1 sidesteps
  this by making the in-app dashboard the primary surface, not notifications.
- **Single developer / fast iteration** assumed; favors a mainstream, well-
  documented stack over anything exotic.

## 6. Assumptions
Each assumption carries a confidence label and how it was validated.

| # | Assumption | Confidence | Validation |
|---|---|---|---|
| A1 | The core job is "record plants + know when to water them." | confirmed-by-user | Stated directly in the original request. |
| A2 | Target platform is a **web app (PWA)**, not native mobile or desktop. | low | Default picked; user deferred the question. DAR-1 supports it on effort/cost. |
| A3 | **Single-user, local storage** (no accounts, no sync) for v1. | low | Default picked; user deferred. YAGNI for a personal tracker. |
| A4 | Watering schedule = **fixed interval per plant**. | low | Default picked; user deferred. DAR-2 shows this **ties** with species-based — genuinely open (§7). |
| A5 | Reminders are delivered via an **in-app "due today" dashboard**, not push/email. | low | Default picked; user deferred. Avoids notification infra + iOS push limits. |
| A6 | Tracking is **watering-only** for v1 (no fertilizer/repot/light). | low | Default picked to honor YAGNI; user deferred. |
| A7 | Stack = **React + Vite + TypeScript + Tailwind + IndexedDB**. | low | Default picked; standard local-first PWA stack. Stage 2 should validate via Context7. |
| A8 | Scale is **tens of plants per user**, not thousands. | medium | Reasonable for a hobbyist; affects no architecture at this size. |
| A9 | English-only UI for v1. | low | Default picked; user deferred. |
| A10 | Dates are handled as **local date-only** (a watering is "a day", not a timestamp-with-timezone). | medium | Reduces timezone/DST bugs; standard for habit trackers. Confirm in Stage 2. |

## 7. Open questions (carried forward to `requirement` stage)
These do **not** block brainstorming, but Stage 2 **must** close them:
1. **Platform:** confirm web PWA (A2) vs native mobile vs desktop/CLI.
2. **Users & data:** confirm single-user local (A3) vs accounts + sync vs sharing.
3. **Schedule logic:** resolve the DAR-2 tie — **fixed interval (v1)** vs
   **species-based catalog**. Strong candidate for a v1.1 fast-follow either way.
4. **Reminders:** is in-app-only (A5) acceptable for v1, or is push/email/calendar
   a v1 requirement (changes architecture — may force a backend)?
5. **Photos:** should a plant have an optional photo in v1? (Adds IndexedDB blob
   handling + storage-size management.)
6. **Tracking scope:** anything beyond watering needed soon (fertilizing, repot,
   light) that should shape the data model now?
7. **Tech stack (A7):** confirm React+Vite+TS+Tailwind, or a preferred stack.
8. **Backup expectation:** is JSON export/import sufficient (G7), or is real
   cross-device sync expected sooner than "later"?
9. **Target devices/browsers:** any must-support set (e.g., iOS Safari) that
   constrains PWA features?
10. **External research not yet performed** (see §11): Stage 2 should validate the
    stack and any plant-care data source before locking them.

## 8. Considered approaches & decisions

### DAR-1 — Platform & persistence architecture
**Decision:** How is the app delivered and where does data live?

| Criterion (weight) | A. Local-first web PWA | B. Native mobile | C. Server-backed web (accounts+DB) |
|---|---|---|---|
| Build effort — lower is better (0.30) | 5 | 2 | 3 |
| Convenience for a daily habit (0.25) | 4 | 5 | 4 |
| Infra cost / ops (0.20) | 5 | 4 | 2 |
| Reminder capability (0.15) | 3 | 5 | 4 |
| Privacy / simplicity (0.10) | 5 | 4 | 3 |
| **Weighted total** | **4.45** | 3.80 | 3.20 |

**Chosen: A — Local-first web PWA.** Wins decisively on build effort and infra
cost while staying convenient (installable, offline). Its weakest axis is proactive
reminders, which v1 deliberately doesn't need (the dashboard is the surface). This
is a reversible-enough call: a backend can be added later behind the same UI.

### DAR-2 — Watering schedule logic
**Decision:** How is "when to water" computed?

| Criterion (weight) | A. Fixed interval | B. Species catalog | C. Weather-smart |
|---|---|---|---|
| Implementation simplicity / no data to source (0.35) | 5 | 3 | 1 |
| Accuracy of guidance (0.30) | 3 | 4 | 5 |
| Onboarding friction — add a plant fast (0.20) | 3 | 5 | 3 |
| Extensibility (0.15) | 4 | 4 | 3 |
| **Weighted total** | **3.85** | **3.85** | 2.90 |

**Chosen for v1: A — Fixed interval, with B flagged as the leading fast-follow.**
A and B **tie** — an honest signal this is a real, open product decision, not an
obvious default. A wins for v1 only because it requires **zero plant-data sourcing**
(YAGNI / fastest path to working), while B's advantage (auto-suggested intervals →
lower onboarding friction) is best added once a curated catalog exists. Because the
score is a tie, this is carried to §7 (#3) for the user to confirm.

### Minor / reversible (DAR skipped)
- **Framework choice (React+Vite+TS+Tailwind):** mainstream, swappable, low lock-in
  — recorded as assumption A7, not worth a full DAR.
- **IndexedDB access pattern (thin wrapper vs library like `idb`/Dexie):** an
  implementation detail for the `design`/`coding` stages, not an architecture fork.

## 9. Recommended approach
Build a **local-first, installable web PWA** (DAR-1) in **React + Vite +
TypeScript + Tailwind**, persisting all data in **IndexedDB**. The core model is a
`Plant` (name, location, `interval_days`, `last_watered`, notes) plus an append-only
`WateringEvent` log. The home screen is a **due-status dashboard** that computes
`next_due = last_watered + interval_days` and sorts plants Overdue → Due today →
Upcoming, each with a one-tap **"Water"** button (DAR-2: fixed interval). Data
safety comes from **JSON export/import** (G7) rather than a backend. No accounts, no
server, works offline. Species-based intervals and push notifications are designed
*around* but deferred — the data model leaves room for both without committing to
them now.

## 10. Risks & mitigations
| Risk | Likelihood | Impact | Mitigation / contingency |
|---|---|---|---|
| **Local data loss** (user clears browser storage / switches device) | Medium | High | JSON export/import (G7); prompt periodic backups; design model so sync can be added later. |
| **iOS PWA push limitations** if reminders are wanted later | Medium | Medium | v1 relies on in-app dashboard, not push; revisit push only if §7 #4 demands it. |
| **Scope creep** into species DB / weather / extra tracking | High | Medium | v1 scope locked to watering + fixed interval (§4); deferrals recorded in §7. |
| **Date math bugs** (timezones, DST, "is it due today") | Medium | Medium | Store/compare **local date-only** values (A10); add unit tests for due-status boundaries in Stage 4. |
| **No external research performed yet** (§11) — stack/data assumptions unvalidated | Medium | Medium | Stage 2 validates stack via Context7 and confirms any plant-care data source before lock-in. |
| **Default-heavy spec** (user deferred clarifications) | High | Medium | All defaults logged as low-confidence (§6) and as open questions (§7); Stage 2 confirms before requirements freeze. |

## 11. References
**No external sources were fetched during this brainstorm.** The session was
fast-tracked at the user's direction (clarify questions declined), and the
recommendations rest on established, mainstream engineering practice rather than
cited research. This is itself logged as a risk (§10) and an open item (§7 #10):
the `requirement` stage should validate the proposed stack with **Context7**
(React, Vite, the chosen IndexedDB wrapper) and confirm a plant-care data source
*before* any species-based scheduling work begins.

## 12. Handoff notes
Start from this file. The single most important thing for Stage 2 to know: **this
spec is deliberately default-heavy because the user opted to skip clarification**,
so the first job of `requirement` is to close §7 — especially #1 (platform), #3
(the fixed-interval-vs-species **tie**), and #4 (whether real notifications are a
v1 requirement, since that is the one answer that could force a backend and
invalidate DAR-1). The architecture (local-first PWA, IndexedDB, no accounts) is
sound *if* those three hold; treat them as the load-bearing assumptions. Everything
else (stack, photos, extra tracking) is low-risk to adjust. Nothing here is code or
design yet — the hard gate holds until the user approves this artifact.
