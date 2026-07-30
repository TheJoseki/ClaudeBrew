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
| TECH spec | `docs/specs/detail-design/TECH-payment-processing.md` |

---

## Phases & Gates

### Phase 1 — Requirements (G1)
**Status**: ✅ COMPLETE
**Output**: `docs/specs/requirements/SRS-payment-processing.md`
**Gate criterion**: SRS approved by user, all user stories have acceptance criteria

| Task | Owner | Status |
|------|-------|--------|
| Write SRS with user stories (checkout, invoice, refund) | ba-agent | ✅ |
| Define acceptance criteria for FR-PAY-01 through FR-PAY-08 | ba-agent | ✅ |
| User review + approval | User | ✅ |

---

### Phase 2 — UI Design (G2)
**Status**: ✅ COMPLETE
**Output**: `docs/specs/requirements/SCREEN-payment-processing.md`
**Gate criterion**: All screen states defined (default/loading/error/success/empty)

| Task | Owner | Status |
|------|-------|--------|
| Checkout page: cart summary, payment form, order confirmation | ui-designer-agent | ✅ |
| Invoice PDF template design | ui-designer-agent | ✅ |
| Error states: card declined, network error, 3DS redirect | ui-designer-agent | ✅ |

---

### Phase 3a — Basic Design (G3a)
**Status**: ✅ COMPLETE
**Output**: `docs/specs/basic-design/BASIC-payment-processing.md`
**Gate criterion**: Module list, DB table list, API endpoint list approved

| Task | Owner | Status |
|------|-------|--------|
| Module structure: PaymentModule, InvoiceModule, WebhookModule | architect-agent | ✅ |
| DB tables: payments, invoices, payment_methods | architect-agent | ✅ |
| API endpoints: POST /payments, GET /invoices/:id, POST /webhooks/stripe | architect-agent | ✅ |

---

### Phase 3b — Detail Design (G3b)
**Status**: ✅ COMPLETE
**Output**: `docs/specs/detail-design/TECH-payment-processing.md`
**Gate criterion**: ORM schema, service methods, DTOs complete; TECH spec approved

| Task | Owner | Status |
|------|-------|--------|
| ORM entities: Payment, Invoice, PaymentMethod | architect-agent | ✅ |
| Service design: PaymentService.createIntent(), confirmPayment(), refund() | architect-agent | ✅ |
| Stripe webhook signature verification flow | architect-agent | ✅ |
| DTO validation: CreatePaymentDto, ConfirmPaymentDto | architect-agent | ✅ |

---

### Phase 3c — Test Viewpoint (G3c)
**Status**: ✅ COMPLETE
**Output**: `docs/TEST_VIEWPOINT.md` (updated)

---

### Phase 4 — Implementation (agents spawned concurrently)
**Status**: ⏳ IN PROGRESS
**Spawn**: developer-agent + unit-test-agent + integration-test-agent (concurrent)

#### developer-agent tasks:
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

#### unit-test-agent (Mode A):
| Task | Output | Status |
|------|--------|--------|
| UTC document for PaymentService + InvoiceService | `docs/test-cases/UTC-payment-processing.md` | ⏳ |

#### integration-test-agent (Mode A):
| Task | Output | Status |
|------|--------|--------|
| ITC document for /payments + /invoices + /webhooks/stripe | `docs/test-cases/ITC-payment-processing.md` | ⏳ |

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
| 3 | Risk | Webhook replay attack window — need idempotency key | developer-agent |

---

## Resume

```
@orchestrator-agent Resume feature payment-processing
Plan file: docs/plans/PLAN-payment-processing-20260320.md
Continue from Phase 4 (Implementation) — status ⏳ IN PROGRESS
developer-agent: continue from task 4.4 (confirmPayment)
```
