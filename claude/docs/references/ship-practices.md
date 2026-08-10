# Ship Practices — ClaudeBrew

> On-demand detail behind the contract's "confirm before deploys" line. Load this when preparing a
> deployment or a release. Judgment guidance, not ceremony — apply what the project's environment calls
> for. (Relocated from the former `deployment-release-standards.md`.)

## Pre-deploy gate

Before any deploy to staging or production, confirm all of these; any failure blocks the deploy:

- The review, security, unit, and integration stages have passed and the user approved them.
- No open Critical or Major defect.
- DB migrations tested on a production-equivalent dataset, and reversible.
- The production build succeeds; every required env var is documented and set in the target.
- A rollback plan exists (how to revert both code and DB).
- Release notes list the changes, fixes, and known issues.

Promotion path is `local → dev → staging → production`; production is reached only through staging, and
staging mirrors production configuration. A hotfix may skip dev with user approval.

## Database migrations — expand / migrate / contract

Never do a destructive single-step schema change (`DROP COLUMN`, `RENAME TABLE`) on a live system. Split
it across deploys:

1. **Expand** — add the new column/table (nullable or defaulted); deploy code that writes both old and new.
2. **Migrate** — backfill old → new; deploy code that reads from new.
3. **Contract** — remove the old column/table after a verification period.

Every migration has a working down script. Schema changes ship before data migrations (never mixed in one
file). On large tables, test `ALTER` timing on staging first — it may lock.

## Rollback — first, debug later

Roll back rather than attempting multiple forward fixes under pressure. Decide within ~15 minutes.

| Symptom | Action |
|---------|--------|
| App crash / 5xx spike, data corruption, auth or security broken | Roll back immediately |
| Performance degraded >50% | Roll back |
| Non-critical feature bug | Fix forward if under ~1h, else roll back |

Procedure: revert code to the last known-good version → revert the DB via the down migration only if users
have not yet modified data → run smoke tests → notify stakeholders with a timeline → capture the lesson
for `retro`.

## Post-deploy smoke tests (always)

- The application starts and its health endpoint returns 200.
- The auth flow works end to end (login → protected route → logout).
- The primary business workflow completes end to end.
- Database connectivity is confirmed.

Then watch error rates, response times, and resource usage against the pre-deploy baseline.

## Versioning (SemVer)

`MAJOR.MINOR.PATCH` — MAJOR for breaking API/schema changes, MINOR for backward-compatible additions, PATCH
for bug/security fixes with no new features. Tag every production release `vMAJOR.MINOR.PATCH`; tags are
immutable. Pre-releases use `-rc.N`.
