# Implementation Plan: payment-processing

> **Worked example** — demonstrates the expected output format from `/cbr-plan`.
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

## Phases & Checkpoints

### Phase 1 — Requirements (REQUIREMENT)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/requirements/SRS.md`
**Checkpoint criterion**: SRS approved by user, all user stories have acceptance criteria

| Task | Owner | Status |
|------|-------|--------|
| Write SRS with user stories (checkout, invoice, refund) | `cbr-plan` | ✅ |
| Define acceptance criteria for FR-PAY-01 through FR-PAY-08 | `cbr-plan` | ✅ |
| User review + approval | User | ✅ |

---

### Phase 2 — UI Design (process-only stop)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/requirements/SCREEN.md`
**Checkpoint criterion**: All screen states defined (default/loading/error/success/empty)

| Task | Owner | Status |
|------|-------|--------|
| Checkout page: cart summary, payment form, order confirmation | `cbr-plan` | ✅ |
| Invoice PDF template design | `cbr-plan` | ✅ |
| Error states: card declined, network error, 3DS redirect | `cbr-plan` | ✅ |

---

### Phase 3a — Basic Design (Basic Design stop)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/design/BASIC.md`
**Checkpoint criterion**: Module list, DB table list, API endpoint list approved

| Task | Owner | Status |
|------|-------|--------|
| Module structure: PaymentModule, InvoiceModule, WebhookModule | `cbr-plan` | ✅ |
| DB tables: payments, invoices, payment_methods | `cbr-plan` | ✅ |
| API endpoints: POST /payments, GET /invoices/:id, POST /webhooks/stripe | `cbr-plan` | ✅ |

---

### Phase 3b — Detail Design (DESIGN)
**Status**: ✅ COMPLETE
**Output**: `docs/streams/payment-processing-20260320/design/TECH.md`
**Checkpoint criterion**: ORM schema, service methods, DTOs complete; TECH spec approved

| Task | Owner | Status |
|------|-------|--------|
| ORM entities: Payment, Invoice, PaymentMethod | `cbr-plan` | ✅ |
| Service design: PaymentService.createIntent(), confirmPayment(), refund() | `cbr-plan` | ✅ |
| Stripe webhook signature verification flow | `cbr-plan` | ✅ |
| DTO validation: CreatePaymentDto, ConfirmPaymentDto | `cbr-plan` | ✅ |

---

### Phase 3c — Test Viewpoint (process-only stop)
**Status**: ✅ COMPLETE
**Output**: `docs/TEST_VIEWPOINT.md` (updated)

---

### Phase 4 — Implementation
**Status**: ⏳ IN PROGRESS
**Stages**: `cbr-implement` (`--parallel`), then `cbr-implement`'s Unit Mode A and
Integration Mode A test-authoring phases — each its own gated internal phase, started by the user.

#### `cbr-implement` tasks:
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

#### `cbr-implement` Unit Mode A:
| Task | Output | Status |
|------|--------|--------|
| UTC document for PaymentService + InvoiceService | `docs/streams/payment-processing-20260320/test-cases/UTC.md` | ⏳ |

#### `cbr-implement` Integration Mode A:
| Task | Output | Status |
|------|--------|--------|
| ITC document for /payments + /invoices + /webhooks/stripe | `docs/streams/payment-processing-20260320/test-cases/ITC.md` | ⏳ |

---

### Phase 5a — Code Review (REVIEW)
**Status**: ⏳ PENDING
**Prerequisite**: Phase 4 complete

---

### Phase 6 — Unit Tests (UNIT)
**Status**: ⏳ PENDING
**Target**: 100% pass, ≥85% coverage
**Run**: `cd backend && npx jest --testPathPattern=payment --coverage`

---

### Phase 7a — API Integration Tests (INTEGRATION)
**Status**: ⏳ PENDING
**Note**: Use Stripe test mode (sk_test_*), real test DB

---

### Phase 5b — Security Re-scan (Pre-Delivery Re-scan stop)
**Status**: ⏳ PENDING
**Focus**: Payment Card Industry (PCI) surface — no card data in logs, HTTPS only, Stripe PK not in bundle

---

### Phase 8 — Delivery
**Status**: ⏳ PENDING

---

## Open Items

| # | Type | Description | Owner |
|---|------|-------------|-------|
| 1 | Decision | PDF generation library — pdfkit vs puppeteer? | Architect |
| 2 | Config | STRIPE_SECRET_KEY env var needs CI/CD secret | DevOps |
| 3 | Risk | Webhook replay attack window — need idempotency key | `cbr-implement` |

---

## Resume

```
Next stage: /cbr-implement payment-processing
Plan file: docs/streams/payment-processing-20260320/plan/PLAN.md
Resume at Phase 4 (Implementation) — status ⏳ IN PROGRESS
Continue from task 4.4 (confirmPayment)
```
