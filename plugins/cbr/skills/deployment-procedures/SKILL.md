---
name: deployment-procedures
description: Guides safe production deployments with pre-flight checks, rollback strategies, and verification procedures. TRIGGER: deploying to production, planning a release, or creating deployment workflows. NOT FOR: development environment setup or code review.
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
metadata:
  version: "3.1"
  category: core-sdlc
---

# Deployment Procedures

$ARGUMENTS

---

## Platform Selection

```
What are you deploying?
  Static site / JAMstack    → Vercel, Netlify, Cloudflare Pages
  Simple web app (managed)  → Railway, Render, Fly.io
  Simple web app (control)  → VPS + PM2/Docker
  Microservices             → Container orchestration
  Serverless                → Edge functions, Lambda
```

---

## 5-Phase Deployment Workflow

```
1. PREPARE   → Verify code, build, env vars
2. BACKUP    → Save current state
3. DEPLOY    → Execute with monitoring open
4. VERIFY    → Health check, logs, key flows
5. CONFIRM   → All good? Confirm. Issues? Rollback.
```

---

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Production build successful
- [ ] Environment variables verified
- [ ] Database migrations ready (if any)
- [ ] Rollback plan documented
- [ ] Team notified
- [ ] Monitoring ready

---

## Post-Deployment Verification

| Window | Action |
| ------ | ------ |
| First 5 min | Active monitoring |
| 15 min | Confirm stable |
| 1 hour | Final verification |
| Next day | Review metrics |

| Check | Why |
| ----- | --- |
| Health endpoint | Service is running |
| Error logs | No new errors |
| Key user flows | Critical features work |
| Response times | Performance acceptable |

---

## Rollback Principles

1. Speed over perfection: rollback first, debug later
2. Don't compound errors: one rollback, not multiple changes
3. Communicate: tell the team
4. Post-mortem: understand why after stable

| Symptom | Action |
| ------- | ------ |
| Service down | Rollback immediately |
| Critical errors | Rollback |
| Performance >50% degraded | Consider rollback |
| Minor issues | Fix forward if quick |

---

## Zero-Downtime Strategies

| Strategy | How | Best For |
| -------- | --- | -------- |
| Rolling | Replace instances one by one | Standard releases |
| Blue-Green | Switch traffic between environments | High-risk changes |
| Canary | Gradual traffic shift | Validation with real traffic |

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Deploy on Friday afternoon | Deploy early in week |
| Rush deployment | Follow the process |
| Skip staging | Always test first |
| Deploy without backup | Backup before deploy |
| Walk away after deploy | Monitor for 15+ min |
| Multiple changes at once | One change at a time |
