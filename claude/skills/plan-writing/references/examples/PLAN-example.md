# Implementation Plan: payment-processing

> **Worked example** — demonstrates the expected output format from `/plan-writing`.
> Feature: "Payment Processing — Stripe integration, checkout flow, invoice generation"

---

## Overview

| Field | Value |
|-------|-------|
| Feature | Payment Processing |
| Created | 2026-03-20 |
| Estimate | 3 weeks (2 BE devs + 1 FE dev) |
| Branch | `feature/payment-processing` |
| Stream | `docs/streams/payment-processing-20260320/` |
| TECH spec | `docs/streams/payment-processing-20260320/design/TECH.md` |

---

## Phases & Gates

### Phase 1 — Requirements (G1)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/requirements/SRS.md`
**Gate criterion**: SRS approved by user, all user stories have acceptance criteria

| Task | Owner | Status |
|------|-------|--------|
| Write SRS with user stories (checkout, invoice, refund) | `analyze-requirement` | ✅ |
| Define acceptance criteria for FR-PAY-01 through FR-PAY-08 | `analyze-requirement` | ✅ |
| User review + approval | User | ✅ |

---

### Phase 2 — UI Design (G2)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/requirements/SCREEN.md`
**Gate criterion**: All screen states defined (default/loading/error/success/empty)

| Task | Owner | Status |
|------|-------|--------|
| Checkout page: cart summary, payment form, order confirmation | `design-screen` | ✅ |
| Invoice PDF template design | `design-screen` | ✅ |
| Error states: card declined, network error, 3DS redirect | `design-screen` | ✅ |

---

### Phase 3a — Basic Design (G3a)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/design/BASIC.md`
**Gate criterion**: Module list, DB table list, API endpoint list approved

| Task | Owner | Status |
|------|-------|--------|
| Module structure: PaymentModule, InvoiceModule, WebhookModule | `design-function` | ✅ |
| DB tables: payments, invoices, payment_methods | `design-function` | ✅ |
| API endpoints: POST /payments, GET /invoices/:id, POST /webhooks/stripe | `design-function` | ✅ |

---

### Phase 3b — Detail Design (G3b)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/design/TECH.md`
**Gate criterion**: ORM schema, service methods, DTOs complete; TECH spec approved

| Task | Owner | Status |
|------|-------|--------|
| ORM entities: Payment, Invoice, PaymentMethod | `design-function` | ✅ |
| Service design: PaymentService.createIntent(), confirmPayment(), refund() | `design-function` | ✅ |
| Stripe webhook signature verification flow | `design-function` | ✅ |
| DTO validation: CreatePaymentDto, ConfirmPaymentDto | `design-function` | ✅ |

---

### Phase 3c — Test Viewpoint (G3c)
**Status**: ✅ COMPLETE
**Output**: `docs/TEST_VIEWPOINT.md` (updated)

---

### Phase 4 — Implementation
**Status**: ⏳ IN PROGRESS
**Stages**: `implement-feature` (`--parallel`), then `unit-test` (Mode A) and
`integration-test` (Mode A) — each its own gated stage, started by the user.

#### `implement-feature` tasks:
| # | Task | File | Status |
|---|------|------|--------|
| 4.1 | Payment entity + migration | `src/payment/payment.entity.ts` | ✅ |
| 4.2 | Invoice entity + migration | `src/invoice/invoice.entity.ts` | ✅ |
| 4.3 | PaymentService — createIntent() | `src/payment/payment.service.ts` | ✅ |
| 4.4 | PaymentService — confirmPayment() | `src/payment/payment.service.ts` | ⏳ |
| 4.5 | PaymentService — refund() | `src/payment/payment.service.ts` | ⏳ |
| 4.6 | Stripe webhook handler | `src/webhook/stripe.controller.ts` | ⏳ |
| 4.7 | InvoiceService — generate PDF | `src/invoice/invoice.service.ts` | ⏳ |
| 4.8 | Checkout FE component | `src/components/Checkout.vue` | ⏳ |
| 4.9 | Payment store (Pinia) | `src/stores/payment.ts` | ⏳ |

#### `unit-test` (Mode A):
| Task | Output | Status |
|------|--------|--------|
| UTC document for PaymentService + InvoiceService | `docs/streams/payment-processing-20260320/test-cases/UTC.md` | ⏳ |

#### `integration-test` (Mode A):
| Task | Output | Status |
|------|--------|--------|
| ITC document for /payments + /invoices + /webhooks/stripe | `docs/streams/payment-processing-20260320/test-cases/ITC.md` | ⏳ |

---

### Phase 5a — Code Review (G4)
**Status**: ⏳ PENDING
**Prerequisite**: Phase 4 complete

---

### Phase 6 — Unit Tests (G6)
**Status**: ⏳ PENDING
**Target**: 100% pass, ≥85% coverage
**Run**: `cd backend && npx jest --testPathPattern=payment --coverage`

---

### Phase 7a — API Integration Tests (G7a)
**Status**: ⏳ PENDING
**Note**: Use Stripe test mode (sk_test_*), real test DB

---

### Phase 5b — Security Re-scan (G5b)
**Status**: ⏳ PENDING
**Focus**: Payment Card Industry (PCI) surface — no card data in logs, HTTPS only, Stripe PK not in bundle

---

### Phase 8 — Delivery (G8)
**Status**: ⏳ PENDING

---

## Open Items

| # | Type | Description | Owner |
|---|------|-------------|-------|
| 1 | Decision | PDF generation library — pdfkit vs puppeteer? | Architect |
| 2 | Config | STRIPE_SECRET_KEY env var needs CI/CD secret | DevOps |
| 3 | Risk | Webhook replay attack window — need idempotency key | `implement-feature` |

---

## Resume

```
Next stage: /cbr:implement-feature payment-processing
Plan file: docs/streams/payment-processing-20260320/plan/PLAN.md
Resume at Phase 4 (Implementation) — status ⏳ IN PROGRESS
Continue from task 4.4 (confirmPayment)
```
