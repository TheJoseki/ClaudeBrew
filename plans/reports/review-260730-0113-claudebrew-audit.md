# ClaudeBrew — Đánh giá lại toàn bộ (advisory review)

- **Ngày:** 2026-07-30
- **Phạm vi:** toàn bộ `plugins/cbr/` (40 skills, 10 agents, 16 rules, hook set) + packaging + evals
- **Phương pháp:** ground-truth grep + 4 scout agent song song (committed core / orchestration / hooks / skills-breadth). Mọi finding kèm `file:line`.
- **Kết luận 1 câu:** Phần *committed core* viết tốt về mặt văn bản, nhưng **các đảm bảo "cứng" (hard gate) của dự án phần lớn KHÔNG thực sự chạy trong bản ship** — và suite import vẫn chưa executable. Nợ kỹ thuật nặng hơn CLAUDE.md mô tả.

---

## 0. TL;DR — 5 vấn đề nghiêm trọng nhất (mới, ngoài "known gaps")

> Các finding về hook contract đã được **verify với docs chính thức** (`code.claude.com/docs/en/hooks.md`) qua agent `claude-code-guide`, không chỉ suy từ repo. Trong quá trình verify, **2 finding scout ban đầu đã bị bác bỏ** (xem §7 "Retracted") — giữ lại để minh bạch.

| # | Vấn đề | Mức | Bằng chứng |
|---|--------|-----|-----------|
| 1 | **Worktree gate — lời hứa trung tâm — không được ship.** `hooks.json` KHÔNG register `enforce-worktree.py`; slot Edit\|Write chạy `protect-files.sh` (secrets guard). SKILL/enforcement khẳng định gate tự bật khi cài plugin → SAI với end user. *(Verifiable thuần từ repo.)* | 🔴 high | `hooks.json:45-54`; `worktree/SKILL.md:33-40,104-108`; `worktree/references/enforcement.md:95-113` |
| 2 | **3 PreToolUse security guard là no-op hoàn toàn** — đọc sai nguồn input. **Docs xác nhận `CLAUDE_TOOL_INPUT` KHÔNG tồn tại**; payload PreToolUse chỉ đến qua stdin JSON (`tool_name`/`tool_input`). Cả 3 thoát sớm ở `[ -z "$TOOL_INPUT" ] && exit 0`. | 🔴 high (doc-confirmed) | `protect-files.sh:14`, `guard-bash.sh:10`, `guard-webfetch.sh:9` (đối chiếu `enforce-worktree.py:63` đọc stdin đúng) |
| 3 | **Pipeline import KHÔNG executable như viết**: `retro` khai báo thiếu tool (`allowed-tools: Read,Grep,Glob,Bash` — không có Agent/Write/Edit) nhưng spawn 5 agent + ghi report, lại `context: fork`; `orchestrator-agent` phase 4–8 trỏ file sai thư mục; `context7-prefetch.md` không tồn tại. | 🔴 high | `retro/SKILL.md:4,6,37,267`; `full-sdlc/SKILL.md:306`; `orchestrator-agent.md:27-28,115,145-148` |
| 4 | **Eval coverage ~0**: 38/40 skill không có `evals/evals.json` (chỉ `brainstorming`, `worktree` có). Không thể verify trigger reliability của cả suite. | 🔴 high | `plugins/cbr/skills/*/evals` |
| 5 | **Wrong `.claude/agents/*` paths** — 10 refs trỏ agent tới `.claude/agents/`, nhưng file ở `plugins/cbr/agents/`. Khi cài, agent không resolve. *(Verifiable thuần từ repo.)* | 🔴 high | `orchestrate/SKILL.md:57,60`; `phase-0-council.md:25,44`; `spawn-templates.md:22,39`; `parallel-agents/SKILL.md:66` |

---

## 1. Committed core (brainstorming + worktree) — reference nhưng có lời hứa sai

**Điểm mạnh (thật):** cả 2 SKILL.md gọn (<250 dòng), đẩy chi tiết vào `references/` đúng cách, cross-link khớp số section, evals match hành vi. `enforce-worktree.py` *bản thân* viết đúng: fail-open khi git/JSON lỗi, check base-branch trước path, normalize backslash, exploit `fnmatch` `*`-spans-`/` đúng và có document. → làm reference *về văn phong* thì ổn.

**Vấn đề:**
- 🔴 `hooks.json:45-54` + `worktree/SKILL.md:33-40` — gate quảng cáo "live whenever plugin enabled" nhưng **không register trong hooks.json**. Chỉ contributor được gate (qua dev `.claude/settings.json:34` dùng `${CLAUDE_PROJECT_DIR}`). End user cài plugin → **không có base-branch denial**.
- 🟡 `worktree/references/enforcement.md:95-113` in một snippet hooks.json register `enforce-worktree.py` **không khớp** hooks.json thật → sibling author copy sẽ tin gate có ship.
- 🟡 `worktree/references/artifact-template.md:34` nói gate ở `.claude/settings.json`, mâu thuẫn `enforcement.md:132` ("no separate settings.json registration"). Tự mâu thuẫn trong 1 skill.
- 🟡 `evals/test_hook.py:47-68` test *script* trực tiếp, không test *wiring* → pass trong khi gate chưa register (false confidence). Không cover: branch `master`, `notebook_path`, branch `develop`, path ngoài repo.
- 🟢 `enforce-worktree.py:81` — cross-drive `relpath` raise ValueError → `rel=absolute` → không match exempt glob → **false-positive DENY** khi repo trên main (Windows đa ổ đĩa).

## 2. Hooks & scripts — tầng bảo vệ phần lớn là inert

- 🔴 **3 guard no-op** (mục #2 TL;DR — doc-confirmed: `CLAUDE_TOOL_INPUT` không tồn tại; PreToolUse payload chỉ qua stdin JSON). Hệ quả: secrets guard, bash guard, webfetch guard **không bảo vệ gì**. Ngay cả khi wiring đúng, `protect-files.sh` còn miss `.npmrc`, `*.tfvars`, `.pgpass`, `aws credentials`. Fix rẻ: parse stdin bằng jq/python thay `$CLAUDE_TOOL_INPUT` (giống `enforce-worktree.py`).
- 🟡 **Portability (đã hạ từ high — conditional risk, không phải defect chắc chắn).** Mọi hook `.sh` spawn qua `bash "..."` (`hooks.json:51,60,69,78,112,122,133,143`); Claude Code trên Windows *thường* có git-bash (Bash tool của session này chính là Git Bash), nên thường chạy — nhưng **không đảm bảo** trên máy end user thiếu bash. Rủi ro chắc chắn hơn là **`jq`**: không bundle mặc định (Windows/macOS) → `subagent-quality-gate.sh:20,25,26`, `compact-context-saver.sh:17,18` fail-open thành no-op. Nên xác minh dependency git-bash + jq, hoặc port sang Python/Node.
- 🟡 `hooks.json:17,38,87,100` — 4 call `pixel-status-update.js` (file không tồn tại; async → fail im lặng). **Lưu ý: CLAUDE.md ghi "5 places", thực tế 4** → doc drift.
- 🟢 `post-compact-reinject.sh` — redundant: header script tự nói "Replaces re-inject-context.sh" nhưng cả PostCompact reinject VÀ SessionStart:compact reinject cùng register → nhiều khả năng double-inject context. (Event `PostCompact` HỢP LỆ — xem §7.)
- 🟢 `post-compact-reinject.sh:64-65` — `grep -c ... || echo "0"` cho "0\n0" → `[ -gt 0 ]` lỗi "integer expression expected" (non-fatal).
- 🟢 `guard-bash.sh` heuristic-only, dễ bypass (`| /bin/sh`, `eval$IFS`, `python -c`, `source <(curl)`).

**Điểm ĐÚNG (đọc stdin theo contract chuẩn):** `subagent-quality-gate.sh`, `subagent-context-inject.js`, `compact-context-saver.sh` — đọc stdin bằng jq/node đúng cách; cơ chế exit-2 + loop-guard của quality-gate hợp lệ. Chỉ 3 PreToolUse guard dùng env-var sai.

## 3. Orchestration layer import — không executable + tự mâu thuẫn

- 🔴 `retro/SKILL.md:4,6` thiếu tool + `context: fork` → không spawn/ghi được; `full-sdlc/SKILL.md:306` Phase 8.5 giao toàn bộ retro cho skill này → **phase retrospective non-executable**.
- 🔴 `orchestrator-agent.md:27-28,145-148` — Required Reading trỏ `skills/orchestrate/references/phase-4-implementation.md` & `phase-5-8-execution.md`, nhưng file nằm ở `skills/full-sdlc/references/`. Dùng đúng `CLAUDE_PLUGIN_ROOT` nhưng **sai subdir** → đây là *lớp path-bug MỚI*, khác nhóm `.claude/` đã biết. Phase 4–8 trỏ file chết.
- 🔴 `orchestrator-agent.md:115` đọc `context7-prefetch.md` — không tồn tại ở đâu trong tree. Phase 0.2f chết.
- 🟡 `orchestrate/SKILL.md:110-198 vs 292-294` — workflow Full SDLC **không có security phase** (5=code-review,6=unit,7=integration,8=delivery) nhưng Success Criteria khẳng định "Security Scan: PASS". orchestrate **âm thầm bỏ security nhưng report là pass**. Mâu thuẫn `full-sdlc` Phase 5 + `orchestrator-agent.md:145` (G5).
- 🟡 `context-inject` DEPRECATED (auto-hook thay thế) nhưng `full-sdlc:111`, `orchestrate:89`, `spawn-templates.md:1-8` vẫn **BẮT BUỘC** gọi thủ công ("FAILURE TO INJECT = agent runs blind"); `orchestrator-agent.md:122-124` lại nói hook auto, "No manual action needed". Skill-layer vs agent-layer chỉ dẫn ngược nhau; path bắt buộc đã chết + skill vẫn model-invocable → double-injection.
- 🟡 `sdlc-conventions.md:18,20,24` định nghĩa gate G3d (architect DESIGN_REVIEW) + G5a/G5b split, nhưng không orchestrator nào spawn design-review; full-sdlc chỉ 1 security scan (G5a), orchestrate không có. **Tập gate định nghĩa ≠ tập gate thực thi.**
- 🟡 `full-sdlc/SKILL.md:80-84 vs sdlc-conventions.md:94-98` — full-sdlc fix "1 UTC + 1 ITC" cho mọi size; authority nói Large = 3 UT + 2 IT.
- 🟡 `parallel-agents/SKILL.md:66-79` + `intelligent-routing:60-68` roster **thiếu `security-tester-agent`** → routing không bao giờ chọn được agent security dù nó tồn tại. `parallel-agents:107` ghi `docs/specs/REQ-*` (non-canonical).
- 🟢 Bootstrapping gap: registries tạo "from `docs/_templates/PLAN-REGISTRY.md`" nhưng **không có template file** nào ship → first-run init không có nguồn.
- ✅ Điểm tốt: **name resolution đúng** — 10/10 agent tồn tại, `name:` khớp bare spawn name.

## 4. Breadth & consistency (40 skills)

- ✅ 40/40 có frontmatter `name`+`description` hợp lệ, không collision, tất cả <500 dòng (max `ui-styling` 412). `evals/` + `examples/` ở root đúng chỗ (dev-only, không leak vào plugin). `setup`, `clean-code` chất lượng cao, on-style.
- 🔴 38/40 thiếu evals (mục #5).
- 🔴 Wrong `.claude/agents/*` paths (đã biết, 10 refs) → agent không resolve khi cài.
- 🟡 **3 convention artifact-path cùng tồn tại**: `brainstorming` (`docs/specs/YYYY-MM-DD-*`), suite import (`docs/specs/requirements/SRS-*`, `TECH-*` — 33 file/131 refs), `clean-code:97` (`docs/decisions/`) → **đứt handoff giữa các stage** (contract chính của dự án).
- 🟡 **Trigger overlap** giữa cặp knowledge/executor: `design-system`/`ui-styling`/`ui-ux-pro-max`/`design-screen`; `testing-patterns`/`tdd-workflow`/`unit-test`/`integration-test`/`run-tests`; `clean-code`/`code-review-checklist`/`review-code`; `architecture`/`design-function`/`api-patterns`/`database-design`. Executor có `TRIGGER:`/`NOT FOR:` guard; knowledge skill phần lớn thiếu → mis-routing.
- 🟡 ClaudeKit leftovers ở 16 file (grep xác nhận): rules + `vulnerability-scanner/scripts/run_audit.sh`, `lint-and-validate/scripts/detect_stack.sh`, `estimate/scripts/calc_estimate.py`, `design-system/scripts/generate-slide.py`, `design-screen/references/design-tool-reference.md`, hook scripts.
- 🟢 `ui-styling/scripts/.coverage` — artifact coverage của Python ship vào cache user (dev cruft).
- 🟢 Metadata không đồng nhất: suite dùng `metadata.version "3.1"`+`category`; core không có; `retro` có block `metadata:` rỗng. `plugin.json` vẫn `0.1.0` dù đã mở rộng lớn.

---

## 5. Root cause (không chỉ triệu chứng)

1. **Hai hệ hook đến từ hai contract khác nhau.** `enforce-worktree.py` (native, đọc stdin, viết bởi tác giả core) đúng; nhóm `.sh` guard (import) đọc env var theo contract của một harness khác → toàn bộ tầng PreToolUse import là inert. Đây là *một* nguyên nhân sinh ra nhiều finding high.
2. **Suite import chưa qua một lần "chạy thật" nào.** retro thiếu tool, path phase-4–8 sai, context7-prefetch thiếu, gate định nghĩa ≠ thực thi → chưa từng execute end-to-end; nếu đã chạy sẽ lộ ngay.
3. **Doc/skill mô tả trạng thái *mong muốn*, không phải trạng thái *đang có*.** worktree/enforcement, "Security Scan PASS", context-inject mandate — tất cả mô tả hệ thống lý tưởng, lệch với file thật. CLAUDE.md cũng drift ("5 places").
4. **Không có harness kiểm chứng.** 38/40 skill không eval; test_hook test script chứ không test wiring → sai lệch không bị bắt.

## 6. Khuyến nghị ưu tiên (cho giai đoạn reconcile)

**P0 — sửa lời hứa sai / bảo mật inert (đe doạ tính đúng đắn):**
1. **[Quyết định: port Python]** Viết lại 3 guard bằng **Python stdlib**, đọc stdin JSON (`tool_name`/`tool_input`) như `enforce-worktree.py`; bỏ `$CLAUDE_TOOL_INPUT` + bỏ bash/jq. Mở rộng scope secrets (`.npmrc`, `*.tfvars`, `.pgpass`, aws creds).
2. **[Quyết định: opt-in]** Worktree gate KHÔNG wire always-on trong plugin. Thay vào đó `/cbr:setup` hỏi & ghi `enforce-worktree.py` vào **user settings.json** (opt-in). Sửa `worktree/SKILL.md`+`enforcement.md`+`artifact-template.md` để mô tả đúng cơ chế opt-in (thôi khẳng định "always-on khi cài plugin"). Fix `enforce-worktree.py:81` cross-drive ValueError.
3. `test_hook.py`: thêm test verify *wiring* (setup ghi đúng registration), không chỉ script; cover `master`/`develop`/`notebook_path`.

**P1 — làm suite import chạy được (reconcile-to-ship):**
4. `retro`: thêm `Agent,Write,Edit` vào allowed-tools, bỏ/điều chỉnh `context: fork`.
5. Sửa path dead: `orchestrator-agent` phase 4–8 → `full-sdlc/references/`; tạo hoặc gỡ `context7-prefetch.md`.
6. Thống nhất security phase: orchestrate phải chạy security phase (add `security-tester-agent` vào roster của `parallel-agents`+`intelligent-routing`) HOẶC bỏ "Security Scan PASS" khỏi success criteria — nhưng vì ship thật, nên **thêm phase**.
7. Gỡ mandate `context-inject` thủ công (đã có auto-hook SubagentStart) — set `disable-model-invocation: true` cho skill, xoá 4 chỗ mandate trong orchestrate/full-sdlc/spawn-templates.
8. Sửa 10 refs `.claude/agents|rules/*` → `${CLAUDE_PLUGIN_ROOT}/agents|rules/*`. Đồng bộ sizing UT/IT giữa full-sdlc vs sdlc-conventions.

**P2 — nhất quán & portability:**
9. **[Quyết định: SRS/TECH]** Hợp nhất artifact-path về `docs/specs/<stage>/<TYPE>-<slug>.md` (authority). Migrate `brainstorming` (→ ví dụ `docs/specs/brainstorms/`), `worktree`, `clean-code` (`docs/decisions/`) theo scheme này.
10. Rename "ClaudeKit"→"ClaudeBrew" (16 file), bump `plugin.json`, gỡ `ui-styling/scripts/.coverage`, thêm `TRIGGER:/NOT FOR:` cho knowledge skill, thêm `evals/evals.json` cho 38 skill, ship template registries (`docs/_templates/*`). Sửa CLAUDE.md doc drift ("5 places"→4).

---

## 7. Retracted findings (minh bạch — scout sai, docs bác bỏ)

Trong lúc verify hook contract với docs chính thức, 2 finding trong bản scout đầu đã bị **bác bỏ** — giữ lại để không lặp lại:

- ❌ ~~"`subagent-quality-gate.sh:25-26` đọc field không chuẩn `agent_type`/`last_assistant_message`"~~ → **SAI.** Docs xác nhận `SubagentStop` payload **có** cả `agent_type` và `last_assistant_message` là field chuẩn. Script đọc đúng contract. Không phải defect.
- ❌ ~~"`PostCompact` là event không tồn tại → hook không fire"~~ → **SAI.** `PostCompact` là event hợp lệ, được hỗ trợ. `post-compact-reinject.sh` được wire đúng event; vấn đề còn lại chỉ là *redundancy* (§2), không phải dead hook.

**Bài học:** scout suy luận "repo không set biến X ⇒ biến X không tồn tại" là category error — harness (không phải repo) mới set env var/field cho hook. Finding nào phụ thuộc hành vi harness phải verify với docs, không suy từ repo. (Finding #2 guards no-op cũng thuộc loại này nhưng đã verify → đứng vững.)

## Quyết định đã chốt (user, 2026-07-30)
1. **Suite import**: RECONCILE để ship dùng thật → mọi P0+P1 load-bearing.
2. **Worktree gate**: OPT-IN qua `/cbr:setup` (không always-on trong plugin) + sửa doc cho khớp.
3. **Hook runtime**: PORT sang Python stdlib (đọc stdin, bỏ bash/jq) — fix no-op + cross-platform một lượt.
4. **Artifact-path**: hợp nhất về authority scheme `docs/specs/<stage>/<TYPE>-<slug>.md`; migrate thiểu số (brainstorming/worktree/clean-code).

→ Sẵn sàng chuyển sang giai đoạn PLAN với 4 quyết định trên làm ràng buộc thiết kế.
