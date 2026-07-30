# Đánh giá bộ skills ClaudeBrew — Thừa & Merge cho SDLC

**Ngày:** 2026-07-30 · **Phạm vi:** `plugins/cbr/skills/*` (40 skills), đối chiếu 10 agents + 16 rules
**Loại:** Report-only (đánh giá, KHÔNG thực thi xoá/merge) · **Nhánh:** main

---

## 1. Nguyên tắc phân loại (trục đánh giá)

Không đánh giá skill theo "chủ đề" mà theo **vai trò trong pipeline** — vì đó là thứ quyết định skill nào an toàn để bỏ/merge:

| Vai trò | Đặc điểm | Có được merge? |
|---------|----------|----------------|
| **Executor (bind agent)** | Mỗi phase SDLC = 1 `Agent` call → 1 role agent (`.*-agent` matcher trong `hooks.json`) | **KHÔNG** — vỡ hợp đồng "1 agent / 1 phase" |
| **Knowledge/reference** | Tài liệu hướng dẫn, được executor tham chiếu | **CÓ** — ứng viên merge chính |
| **Meta/orchestrator** | Điều phối, định tuyến | Có overlap nội tại → gộp |
| **Infrastructure** | Command-runner thuần, không bind agent | Merge dễ nhất |

**9 executor bind agent (BẤT KHẢ XÂM PHẠM):** `analyze-requirement`↔ba, `design-screen`↔ui-designer, `design-function`↔architect, `implement-feature`↔developer, `review-code`↔code-review, `unit-test`↔unit-test, `integration-test`↔integration-test, `fix-bug`↔bug-fix, `vulnerability-scanner`↔security-tester.

---

## 2. Blast radius (đo trước khi khuyến nghị)

Grep 16 tên skill ứng viên trên toàn tree: **206 lượt / 63 file**. Phân bố:
- Chủ yếu là `NOT FOR:` guards giữa các skill + bảng của `intelligent-routing` (13 lượt, **đã lỗi thời** — chỉ liệt kê 16/40 skill, còn trỏ `.claude/skills/`, còn nhắc Vuetify).
- Vài agent/rule body: `bug-fix-agent`(3), `agent-best-practices.md`(4), `ui-designer/unit-test/integration-test-agent`(mỗi 1).
- `hooks.json`(1).
- `docs/`: chỉ **5 lượt / 3 file** (BACKLOG-REGISTRY + 2 journal) → tác động tài liệu thấp.
- `context-inject`: **chỉ self-reference** (SKILL + evals của chính nó) → xoá sạch.

> **Chi phí chung của mọi merge/xoá:** (a) sửa cross-ref `NOT FOR:` ở skill anh em; (b) cập nhật bảng `intelligent-routing`; (c) **gộp `evals/evals.json`** (CLAUDE.md coi "cả 40 skill có evals" là thành quả reconcile — merge = hợp nhất eval set, không chỉ prose); (d) cập nhật prose CLAUDE.md.

---

## 3. TẦNG 1 — Bỏ hẳn (dead weight)

| Skill | Dòng | Lý do | Chi phí |
|-------|------|-------|---------|
| `context-inject` | 226 | Tự đánh dấu **DEPRECATED** — đã thay bằng hook `subagent-context-inject.js`. Grep chỉ ra self-reference. | Trivial: xoá thư mục + 1 dòng prose CLAUDE.md (đã ghi "self-marked DEPRECATED"). |

---

## 4. TẦNG 2 — Meta/orchestrator (gộp trùng lặp)

### 4.1 ⭐ HEADLINE: `full-sdlc` + `orchestrate` — trùng pipeline SDLC
- **Bằng chứng:** `orchestrate` (301) có Step 0 triage → 4 workflow; nhánh "Full SDLC" (Step 1→8) là **bản inline độ chính xác thấp hơn** của `full-sdlc` (327): thiếu gate G3c (test-viewpoint), thiếu bảng sizing/batching, thiếu spawn UTC/ITC nền, thiếu voting design, thiếu auto-retro. Ngược lại `full-sdlc` thiếu triage + các workflow Bug-Fix/Enhancement/Simple.
- **Khuyến nghị (đáp thẳng câu hỏi "merge làm 1 cho SDLC"):** giữ `orchestrate` làm **cửa vào triage duy nhất**; nhánh NEW_FEATURE **gọi lại `full-sdlc`** thay vì tái hiện inline. Bỏ đoạn Step 1→8 trùng trong `orchestrate`. Kết quả: 1 nguồn sự thật cho pipeline, vẫn giữ cả triage lẫn 4 workflow variant.
- **Chi phí:** trung bình — sửa `orchestrate` (bỏ ~100 dòng Step 1→8, trỏ sang full-sdlc), giữ nguyên full-sdlc.

### 4.2 `behavioral-modes` → gộp vào `intelligent-routing` (hoặc bỏ)
- **Bằng chứng:** 7 "mode" mỗi cái chỉ là alias của 1 skill đã tồn tại (BRAINSTORM→brainstorming, IMPLEMENT→implement-feature, DEBUG→fix-bug, REVIEW→review-code, SHIP→deployment-procedures, ORCHESTRATE→orchestrate). Cả hai đều `user-invocable: false`. Chồng chéo chức năng "request → hành động".
- **Khuyến nghị:** giữ lại bảng mode-detection (phần hữu ích duy nhất) đưa vào `intelligent-routing`; bỏ `behavioral-modes`. **Bonus:** `intelligent-routing` đang lỗi thời — nên refresh bảng skill trong cùng lượt.

### 4.3 `parallel-agents` → `references/` dưới `orchestrate`
- Là **pattern** orchestrator gọi, không phải stage người dùng trigger. Hạ cấp thành reference file → bớt 1 skill top-level.

---

## 5. TẦNG 3 — Merge cụm knowledge (phần "gọn hoá SDLC" thực sự)

Mỗi cụm reference đều phục vụ **1 executor**. Merge cụm reference, GIỮ executor.

| # | Cụm merge | Dòng | Phục vụ executor | Độ tin cậy |
|---|-----------|------|------------------|-----------|
| 5.1 | `lint-and-validate`(87) + `run-tests`(99) → 1 "validate-and-test" | 186 | (infra, không bind agent) | ⭐ **Cao nhất** — command-runner thuần, merge sạch nhất suite |
| 5.2 | `testing-patterns`(85) + `tdd-workflow`(109) → 1 "testing-strategy" | 194 | unit-test / integration-test | Cao |
| 5.3 | `clean-code`(122) + `code-review-checklist`(92) → 1 "code-quality" | 214 | review-code | Cao |
| 5.4 | `systematic-debugging`(215) → `references/` của `fix-bug` | 215 | fix-bug (đã escalate sang nó) | Trung bình (vẫn dùng standalone) |

### 5.5 UI/UX — merge CÓ RÀNG BUỘC kích thước
`design-system`(315) + `ui-styling`(412) + `ui-ux-pro-max`(305) = **1032 dòng** > ngân sách SKILL.md <500.
- **Hình dạng bắt buộc:** 1 SKILL.md gọn + **3 file `references/`**. `ui-ux-pro-max` mang theo Python scripts + CSV database → **đắt để fold**.
- **Khuyến nghị thực dụng:** merge `design-system` + `ui-styling` → "ui-implementation"; **giữ `ui-ux-pro-max` standalone** (nó là intelligence có DB, bản chất khác). Cả 3 cùng phục vụ executor `design-screen`.

### 5.6 ⚠️ Technical-design cluster — TÙY CHỌN, có cảnh báo
`architecture`(125) + `api-patterns`(90) + `database-design`(100) = 315 dòng (khả thi về size).
- **CẢNH BÁO (đừng đảo quyết định đã chốt):** CLAUDE.md + reconcile ghi rõ `TRIGGER:`/`NOT FOR:` guards đã được **cố ý thêm vào đúng 3 skill này** để khử chồng chéo *bằng cách phân định thay vì gộp*. Theo rule `review-audit-self-decision`, không đảo quyết định đã verify vì lo ngại trừu tượng.
- **Khuyến nghị:** trình bày như **tùy chọn** kèm trade-off; KHÔNG xếp là "win hiển nhiên". Chỉ merge nếu bạn ưu tiên giảm số skill top-level và chấp nhận viết lại guards thành phân mục nội bộ.

---

## 6. Đặt câu hỏi về tư cách standalone

| Skill | Dòng | Vấn đề |
|-------|------|--------|
| `create-pr` | 45 | Mỏng nhất tree, không bind agent. Cân nhắc fold vào đuôi `implement-feature` hoặc 1 skill "ship/delivery". |

---

## 7. GIỮ NGUYÊN (distinct / load-bearing)

- **9 executor bind agent** (mục 1) — hợp đồng 1-agent-1-phase.
- `brainstorming`, `worktree` — reference core, house style (đọc trước khi tác giả skill khác).
- `plan-writing`, `estimate`, `handoff`, `retro` — deliverable riêng biệt.
- `setup` — infra duy nhất (merge harness settings).
- `performance-profiling`, `deployment-procedures`, `documentation-templates`, `browser-devtools` — domain riêng, không trùng.

---

## 8. Tổng kết tác động

| Hành động | Δ skill | Độ tin cậy |
|-----------|---------|-----------|
| Bỏ `context-inject` | −1 | Chắc chắn |
| `lint-and-validate` + `run-tests` | −1 | ⭐ Cao nhất |
| `full-sdlc` ⟷ `orchestrate` de-dupe | −0/−1 | Cao (headline) |
| `behavioral-modes` → routing | −1 | Cao |
| `parallel-agents` → ref | −1 | Cao |
| `testing-patterns` + `tdd-workflow` | −1 | Cao |
| `clean-code` + `code-review-checklist` | −1 | Cao |
| `systematic-debugging` → fix-bug ref | −1 | Trung bình |
| `design-system` + `ui-styling` | −1 | Trung bình (cần refs) |
| **Technical-design cluster** | −2 | ⚠️ Tùy chọn (đảo quyết định) |
| `create-pr` fold | −1 | Cần user quyết |

**Kịch bản khuyến nghị (high-confidence):** 40 → ~**32** skills (áp dụng 3, 4, 5.1–5.4). Nếu thêm 5.5 + tùy chọn: xuống ~**29**.

---

## 9. Quyết định user (2026-07-30) + phát hiện bổ sung

> **SUPERSEDED / cập nhật (2026-07-31):** Cả 2 fork "còn mở" bên dưới đã được chốt, và quyết định "dọn agent layer" đã được **tinh chỉnh** sau nghiên cứu xia (ClaudeKit): KHÔNG bỏ hết agent — **giữ 1 pool ~4–5 capability agent** (reviewer/tester/researcher/developer). Nguồn sự thật hiện tại là `plans/260730-2316-single-layer-sdlc-refactor/plan.md` (Decisions §1–6) + `reports/xia-synthesis-and-challenge.md`. Đọc plan đó, không dùng phần "2 fork còn mở" dưới đây làm trạng thái hiện tại.

### Quyết định đã chốt
| # | Quyết định | Ghi chú thực thi |
|---|-----------|------------------|
| 1 | **Bỏ cả `full-sdlc` + `orchestrate`** | Lý do user: ép entry qua orchestrator → cascade quá chặt, không gọi thì artifact bị skip. Khớp house style "hard gate, no cascade". **KHÔNG giữ orchestrator mỏng.** |
| 2 | **Gộp cụm UI → 1 skill `design-system`** | design-system + ui-styling + ui-ux-pro-max → 1 SKILL.md gọn + 3 `references/`; scripts/CSV của ui-ux-pro-max chuyển thành `design-system/scripts` + `design-system/data` (merge ≠ xoá asset). |
| 3 | **Bỏ `create-pr`** | Fold thao tác PR vào đuôi execution/ship nếu cần. |
| 4 | **Bỏ `parallel-agents`** | Parallel thành **argument mode** trong skill execution (design/coding/test), không còn skill riêng. |

### Phát hiện bổ sung (scouting sau quyết định)
- **Gates KHÔNG nằm ở orchestrator** — G1–G8 + bảng artifact-path là của `rules/sdlc-conventions.md` (always-loaded). Xoá orchestrator KHÔNG mất định nghĩa gate.
- **Stage skill đã self-sufficient** — `analyze-requirement` có Step 0→3 riêng, ghi đúng `SRS-[feature].md`, có G1 checklist; bảng "on-success" chỉ là gợi ý (không cascade). Đây chính là house-style path.
- **⚠️ Agent layer thành mồ côi** — stage skill KHÔNG có `Agent` tool (`analyze-requirement`: Read/Grep/Glob/Write/Edit) → skill làm việc **inline**, không spawn `ba-agent`. Chỉ orchestrator có `Agent`+`spawn-templates.md`. Bỏ orchestrator ⇒ 10 role agents + `orchestrator-agent` + hook `.*-agent` (`SubagentStart`/`SubagentStop`) + rule chỉ phục vụ orchestration (spawn-sizing, planning-council, team-lifecycle, interrupt-protocol) **mất người gọi**.
- **Entry point biến mất** — `intelligent-routing` (đã lỗi thời, còn liệt kê full-sdlc/orchestrate ở L1) là router de-facto duy nhất còn lại.

### 2 fork còn mở (cần user quyết)
1. **Technical-design cluster** (`architecture`+`api-patterns`+`database-design`): giữ (guards đã chốt trong reconcile) hay merge?
2. **Phạm vi dọn agent layer**: bỏ luôn lớp agent mồ côi + hook + rule orchestration, hay để lại/deferred?

### Khuyến nghị đi kèm (không chặn)
- **Router/entry:** theo house style → KHÔNG cần router; user gọi thẳng stage skill. `intelligent-routing` nên retire hoặc thu về 1 bảng tra cứu tĩnh. `behavioral-modes` bỏ (mode ORCHESTRATE mất nghĩa).
- **`retro`:** mất auto-trigger (Phase 8.5 của full-sdlc) → chuyển thành skill user gọi tay sau delivery.
- **CLAUDE.md:** phần "The SDLC engine" (two-layer) cần viết lại theo mô hình single-layer.
