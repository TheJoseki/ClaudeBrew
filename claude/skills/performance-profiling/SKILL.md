---
name: performance-profiling
description: "Analyzes and optimizes application performance. Covers Core Web Vitals, bundle analysis, runtime profiling, memory leaks, and optimization priorities. Use when investigating slow performance, optimizing page load, or profiling applications."
allowed-tools: Read, Grep, Glob, Bash
metadata:
  version: "3.1"
  category: quality
---

# Performance Profiling

$ARGUMENTS

---

## Core Workflow

```
1. BASELINE  → Measure current state
2. IDENTIFY  → Find the bottleneck
3. FIX       → Make targeted change
4. VALIDATE  → Confirm improvement
```

---

## Core Web Vitals Targets

| Metric | Good | Poor | Measures |
| ------ | ---- | ---- | -------- |
| LCP | < 2.5s | > 4.0s | Loading |
| INP | < 200ms | > 500ms | Interactivity |
| CLS | < 0.1 | > 0.25 | Visual stability |

---

## Profiling Tool Selection

| Problem | Tool |
| ------- | ---- |
| Page load | Lighthouse |
| Bundle size | Bundle analyzer |
| Runtime | DevTools Performance tab |
| Memory | DevTools Memory tab |
| Network | DevTools Network tab |
| Backend | Framework-specific profiler |

---

## Bundle Analysis

| Finding | Action |
| ------- | ------ |
| Large dependency | Import specific modules |
| Duplicate deps | Dedupe, update versions |
| Route in main bundle | Code split |
| Unused exports | Tree shake |

---

## Runtime Profiling Indicators

| Pattern | Meaning |
| ------- | ------- |
| Long tasks (>50ms) | UI blocking |
| Many small tasks | Batching opportunity |
| Layout/paint events | Rendering bottleneck |
| Growing heap | Possible memory leak |
| Detached DOM nodes | Not cleaned up |

---

## Common Bottlenecks

| Symptom | Likely Cause |
| ------- | ------------ |
| Slow initial load | Large JS, render-blocking resources |
| Slow interactions | Heavy event handlers |
| Scroll jank | Layout thrashing |
| Growing memory | Leaks, retained references |
| Slow API responses | N+1 queries, missing indexes |

---

## Quick Win Priority

| Priority | Action | Impact |
| -------- | ------ | ------ |
| 1 | Enable compression | High |
| 2 | Lazy load images | High |
| 3 | Code split routes | High |
| 4 | Cache static assets | Medium |
| 5 | Optimize images | Medium |
| 6 | Defer non-critical JS | Medium |

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Guess at problems | Profile first |
| Micro-optimize early | Fix the biggest bottleneck |
| Optimize prematurely | Optimize when measured data shows need |
| Ignore real user data | Use RUM alongside synthetic tests |

---

> The fastest code is code that doesn't run. Remove before optimizing.

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Prerequisite | Application running with measurable baseline | Profile only against a functional, deployed app |
| On regressions found | `fix-bug` | Fix performance regressions in implementation |
| On structural bottlenecks | `architecture` | When bottleneck requires architecture-level change |
| Escalate | `fix-bug` | For complex perf issues needing deeper root cause analysis |
| Related | `code-quality` | After profiling, apply clean code to remove unnecessary computation |
