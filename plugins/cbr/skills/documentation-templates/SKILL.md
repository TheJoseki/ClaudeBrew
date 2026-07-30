---
name: documentation-templates
description: "Provides templates and structure guidelines for README, API docs, changelogs, ADRs, and AI-friendly documentation. Use when creating documentation, structuring project docs, or setting up documentation standards."
allowed-tools: Read, Grep, Glob
metadata:
  version: "3.1"
  category: domain-guidance
---

# Documentation Templates

$ARGUMENTS

---

## README Structure

| Section | Purpose |
| ------- | ------- |
| Title + One-liner | What is this? |
| Quick Start | Running in <5 min |
| Features | What can it do? |
| Configuration | How to customize |
| API Reference | Link to detailed docs |
| Contributing | How to help |
| License | Legal |

---

## API Documentation (Per-Endpoint)

```
## METHOD /path/:param

Brief description.

Parameters:
| Name | Type | Required | Description |

Response:
- 200: Success description
- 4xx: Error description

Example: request and response
```

---

## Code Comment Guidelines

| Comment | Don't Comment |
| ------- | ------------- |
| Why (business logic) | What (obvious code) |
| Complex algorithms | Every line |
| Non-obvious behavior | Self-explanatory code |
| API contracts | Implementation details |

---

## Changelog (Keep a Changelog format)

```
## [Unreleased]
### Added / Changed / Fixed / Removed

## [1.0.0] - YYYY-MM-DD
### Added
- Initial release
```

---

## Architecture Decision Record (ADR)

```
# ADR-NNN: Title

## Status: Accepted / Deprecated / Superseded

## Context: Why are we making this decision?

## Decision: What did we decide?

## Consequences: What are the trade-offs?
```

---

## AI-Friendly Documentation

For AI crawlers and agents, provide `llms.txt`:

```
# Project Name
> One-line objective.

## Core Files
- [src/index.ts]: Main entry
- [src/api/]: API routes

## Key Concepts
- Concept 1: Brief explanation
```

---

## Principles

| Principle | Why |
| --------- | --- |
| Scannable | Use headers, lists, tables |
| Examples first | Show, don't just tell |
| Progressive detail | Simple then complex |
| Up to date | Outdated docs mislead |
