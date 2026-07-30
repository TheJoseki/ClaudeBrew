---
description: Deployment process rules — pre-deploy gates, environment promotion, DB migrations, rollback, versioning. Always loaded to ensure safe releases.
---

# Deployment & Release Standards

> Defines mandatory rules for deploying and releasing software. The `/deployment-procedures` skill provides detailed guidance — this file defines the RULES that cannot be skipped.

## 1. Pre-Deployment Gate (MANDATORY)

Before ANY deployment to staging or production, verify ALL:

| Check | Condition | Block Deploy If |
|-------|-----------|----------------|
| Quality Gates | G4 (review), G5 (security), G6 (UT), G7 (IT) all PASS | Any gate not PASS |
| Open Defects | 0 Critical (S1), 0 Major (S2) open | Any S1/S2 OPEN |
| DB Migrations | Tested on staging with production-equivalent data | Migration fails or irreversible |
| Build | Production build succeeds | Build fails |
| Env Vars | All required vars documented and set in target env | Missing critical var |
| Rollback Plan | Documented: how to revert code + DB changes | No rollback plan |
| Changelog | Release notes list all changes, fixes, known issues | Missing for production |

**Rule**: No exceptions. ANY check fails → deployment is BLOCKED until resolved.

## 2. Environment Promotion Path

```
local → dev → staging → production
```

| Environment | Purpose | Data | Deploy Frequency |
|-------------|---------|------|-----------------|
| local | Developer machine | Seed/mock | Continuous |
| dev | Integration testing, demos | Seed data | Per-commit or per-merge |
| staging | Pre-production validation | Production-like (anonymized) | Per-release candidate |
| production | Live users | Real data | Per-release (scheduled) |

### Promotion Rules
- Code MUST pass all tests on current env before promoting to next
- No direct deploy to production — must go through staging first
- Staging MUST mirror production configuration (DB engine, env vars, infra)
- Hotfixes: may skip dev → deploy to staging → production (with user approval)

## 3. Database Migration Sequencing

### Zero-Downtime Migration Pattern

```
Phase 1: EXPAND   — Add new column/table (nullable or with default)
                    Deploy code that writes to BOTH old and new
Phase 2: MIGRATE  — Backfill data from old to new location
                    Deploy code that reads from new location
Phase 3: CONTRACT — Remove old column/table (after verification period)
                    Deploy code that only uses new location
```

### Migration Rules

| Rule | Detail |
|------|--------|
| Reversibility | Every migration MUST have a working down/rollback script |
| Test first | Run migration on staging with production-equivalent data volume |
| Order | Schema changes BEFORE data migrations. Never mix in one file |
| No destructive single-step | DROP COLUMN, RENAME TABLE → use EXPAND/MIGRATE/CONTRACT |
| Lock awareness | ALTER TABLE on large tables may lock — test timing on staging |
| Seed separation | Seed data scripts separate from schema migrations |

## 4. Rollback Triggers and Procedures

### When to Rollback (decide within 15 minutes)

| Symptom | Action | Urgency |
|---------|--------|---------|
| App crash / 5xx spike | Rollback immediately | < 5 min |
| Data corruption detected | Rollback + notify DBA | < 5 min |
| Auth/security broken | Rollback immediately | < 5 min |
| Performance degraded >50% | Rollback | < 15 min |
| Feature bug (non-critical) | Fix forward if <1hr; else rollback | < 30 min |

### Rollback Procedure
1. **Revert code** — Deploy previous known-good version
2. **Revert DB** — Run down migration ONLY if data not yet modified by users
3. **Verify** — Run smoke tests on rolled-back version
4. **Notify** — Update team/stakeholders with incident timeline
5. **Post-mortem** — Document in CAR (see `risk-issue-management.md`) + add to PROJECT-MEMORY

**Rule**: Rollback first, debug later. Never try multiple forward fixes under pressure.

## 5. Post-Deploy Verification

| Window | Action |
|--------|--------|
| 0–5 min | Health check endpoint returns 200 |
| 0–5 min | Error log monitoring — no new error patterns |
| 5–15 min | Smoke test critical user flows (login, core CRUD, key workflow) |
| 15–60 min | Monitor error rates, response times, resource usage |
| 24 hours | Review metrics vs pre-deploy baseline |

**Minimum smoke tests** (always required):
- Application starts and health endpoint responds
- Authentication flow works (login → protected route → logout)
- Primary business workflow completes end-to-end
- Database connectivity confirmed

## 6. Feature Flags

### When to Use
- Large features spanning multiple sprints
- Risky changes needing instant disable without rollback
- A/B testing or gradual rollout

### Feature Flag Rules

| Rule | Detail |
|------|--------|
| Naming | `FF_<FEATURE_NAME>` uppercase snake_case |
| Default | New flags OFF in production |
| Cleanup | Remove flag code within 2 sprints after permanent |
| No nesting | Max 1 level of flag dependency |
| Document | Every flag in PROJECT.md or FLAGS.md with owner + expiry |

## 7. Release Versioning (SemVer)

```
MAJOR.MINOR.PATCH — e.g., 2.3.1
```

| Increment | When |
|-----------|------|
| MAJOR | Breaking API/schema changes, incompatible upgrades |
| MINOR | New features, backward-compatible additions |
| PATCH | Bug fixes, security patches, no new features |

- Every production deploy MUST have a git tag: `v[MAJOR].[MINOR].[PATCH]`
- Tags are immutable — never delete or move
- Pre-release: `v2.1.0-rc.1` for release candidates
- Hotfix: increment PATCH from latest production tag
