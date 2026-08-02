# QA Issue Taxonomy

> Reference document for integration-test-agent and QA workflows.
> Loaded via `## Required Reading` section in agent definition.

## Severity Levels

| Level | Name | Criteria | Action |
|-------|------|----------|--------|
| S1 | Critical | App crash, data loss, security breach, auth bypass | Block release. Fix immediately. |
| S2 | High | Major feature broken, no workaround available | Must fix before merge. |
| S3 | Medium | Feature degraded but workaround exists | Fix in current sprint. |
| S4 | Low | Cosmetic issue, minor UX friction | Backlog — fix when convenient. |

## Issue Categories

| Category | What to Look For |
|----------|-----------------|
| Visual/UI | Misalignment, overflow, z-index stacking, responsive breakage, missing assets |
| Functional | Button/link doesn't work, wrong data displayed, broken workflow, form errors |
| UX | Confusing interaction, missing feedback, unexpected behavior, slow perceived response |
| Content | Typos, placeholder text left in, wrong labels, missing translations |
| Performance | Page load >3s, memory leak, unnecessary re-renders, large bundle size |
| Console/Errors | JS errors, failed API calls (4xx/5xx), deprecation warnings, unhandled rejections |
| Accessibility | Missing alt text, keyboard trap, low contrast (<4.5:1), missing ARIA labels |

## Per-Page Exploration Checklist

When testing any page, follow this 8-step sequence:

1. **Visual scan** — Check layout, spacing, alignment at current viewport. Resize to mobile/tablet.
2. **Interactive elements** — Click every button, link, dropdown. Verify expected behavior.
3. **Forms** — Submit valid data, then invalid data. Check validation messages and error states.
4. **Navigation** — Verify all routes reachable. Test browser back/forward buttons.
5. **States** — Test empty state, loading state, error state, success state, edge cases (max length, special chars).
6. **Console** — Open DevTools console. No errors or warnings in happy path.
7. **Responsiveness** — Test at 375px (mobile), 768px (tablet), 1280px (desktop) breakpoints.
8. **Auth boundaries** — Verify protected routes redirect unauthenticated users. Test role-based access.
