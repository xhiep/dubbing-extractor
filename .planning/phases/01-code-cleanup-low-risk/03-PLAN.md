---
wave: 2
plan_id: "03"
depends_on: ["01", "02"]
files_modified:
  - CLAUDE.md
  - .planning/codebase/ARCHITECTURE.md
  - .planning/codebase/CONCERNS.md
autonomous: true
requirements_addressed: []
---

# Plan 03: Update Documentation

<objective>
Cập nhật tất cả documentation để phản ánh chính xác tình trạng codebase: fix line counts, remove outdated "Việc đang làm" section, update architecture descriptions.
</objective>

<tasks>

<task id="3.1">
<read_first>
- CLAUDE.md (toàn bộ file)
- main.py (để đếm lines chính xác)
- src/modules/workflow.py (để đếm lines chính xác)
</read_first>

<action>
Update CLAUDE.md với thông tin chính xác:

1. Count actual lines:
   wc -l main.py src/modules/workflow.py

2. Update line count trong "Cấu trúc chính":
   - Current: `main.py` — entry point + toàn bộ GUI (Tkinter, ~1760 dòng)
   - Update to: `main.py` — entry point + toàn bộ GUI (Tkinter, ~2481 dòng)

3. REMOVE "Việc đang làm" section completely (lines 39-43):
   ```markdown
   ## Việc đang làm (dở dang từ session trước)
   Tách `process_video` thành 7 hàm step riêng trong `workflow.py`,
   thêm UI chạy từng bước vào tab Nguồn trong `main.py`:
   - Nút Bước 1→5 trong tab Nguồn (bấm Bước N = chạy từ đầu đến bước N)
   - Ô edit SRT sau bước dịch (+ nút mở file ngoài, lưu thay đổi)
   - Xóa duplicate checkbox lồng tiếng (quick_dub_toggle dòng 196-209)
   - Thêm `pipeline_state` dict để lưu state giữa các bước
   Backup đã có tại: `C:\Users\xhiep\Downloads\dubbing-extractor-backup-20260423_1630`
   ```

4. ADD new "Tính năng hiện tại" section:
   ```markdown
   ## Tính năng hiện tại
   
   **Hai chế độ xử lý video:**
   1. **Monolithic mode** (nút "Bắt Đầu Xử Lý"): Chạy toàn bộ pipeline một lần
   2. **Step-by-step mode** (7 nút "Bước 1-7"): Chạy từng bước riêng, có thể edit SRT giữa chừng
   
   Cả hai mode đều sử dụng các step functions trong `workflow.py`.
   ```

5. Keep "Pipeline workflow" section unchanged (vẫn đúng)

6. Keep backup reference (vẫn hợp lệ)
</action>

<acceptance_criteria>
- CLAUDE.md line count accurate: ~2481 for main.py
- CLAUDE.md không còn section "Việc đang làm"
- CLAUDE.md có section "Tính năng hiện tại" mới
- CLAUDE.md syntax valid (markdown)
- Backup reference preserved
</acceptance_criteria>
</task>

<task id="3.2">
<read_first>
- .planning/codebase/ARCHITECTURE.md (toàn bộ file)
- main.py (để verify line count)
- src/modules/workflow.py (để verify line count)
</read_first>

<action>
Update ARCHITECTURE.md với line counts chính xác:

1. Count actual lines:
   wc -l main.py src/modules/workflow.py

2. Find and update line count references:
   - Search for "main.py" line count mentions
   - Update to ~2481 lines
   - Search for "workflow.py" line count mentions
   - Update to ~567 lines

3. Update "Workflow Orchestration Layer" section:
   - Remove any mention of "step functions (in progress)"
   - Update to: "Step functions (step1-7) used by both monolithic and step-by-step modes"

4. Remove any "Work In Progress" markers related to step-by-step UI

5. Verify all file paths still valid
</action>

<acceptance_criteria>
- ARCHITECTURE.md has accurate line counts (main.py ~2481, workflow.py ~567)
- ARCHITECTURE.md không reference "in progress" cho step functions
- ARCHITECTURE.md describes step functions as implemented
- All file paths valid
</acceptance_criteria>
</task>

<task id="3.3">
<read_first>
- .planning/codebase/CONCERNS.md (toàn bộ file)
</read_first>

<action>
Update CONCERNS.md to remove outdated WIP section:

1. Find "Work In Progress" section about step-by-step UI

2. REMOVE or UPDATE to:
   ```markdown
   ## Completed Features
   
   **Step-by-step UI** (Previously listed as WIP):
   - ✅ 7 step buttons implemented
   - ✅ pipeline_state tracking implemented
   - ✅ SRT editor integration implemented
   - Status: COMPLETE and functional
   ```

3. Keep other concerns (RTX 5060 limitations, etc.)

4. Update "Last updated" timestamp to 2026-04-23
</action>

<acceptance_criteria>
- CONCERNS.md không còn list step-by-step UI as "Work In Progress"
- CONCERNS.md marks step-by-step UI as COMPLETE
- Other concerns preserved
- Timestamp updated
</acceptance_criteria>
</task>

<task id="3.4">
<read_first>
- All updated documentation files
</read_first>

<action>
Final documentation verification:

1. Verify all line counts accurate:
   - main.py: wc -l main.py
   - workflow.py: wc -l src/modules/workflow.py
   - Compare với documentation

2. Verify no broken references:
   - All file paths exist
   - All function names exist
   - All module names exist

3. Verify consistency:
   - Same information across all docs
   - No contradictions
   - No outdated information

4. Create summary of changes:
   - Documentation updated to reflect reality
   - Step-by-step UI marked as complete
   - Line counts corrected
</action>

<acceptance_criteria>
- All line counts in docs match actual files
- No broken references to removed code
- No contradictions between documents
- Documentation consistent and accurate
</acceptance_criteria>
</task>

</tasks>

<verification>
## Documentation Accuracy
- [ ] CLAUDE.md line counts accurate
- [ ] CLAUDE.md không reference outdated WIP
- [ ] ARCHITECTURE.md line counts accurate
- [ ] CONCERNS.md marks step-by-step UI as complete

## Consistency Check
- [ ] All docs agree on line counts
- [ ] All docs agree on feature status
- [ ] No contradictions between docs
- [ ] No references to "work in progress" for completed features

## Completeness
- [ ] All changed files documented
- [ ] Phase 1 cleanup documented
- [ ] Step-by-step UI status clarified
</verification>

<must_haves>
- CLAUDE.md accurate and up-to-date
- No references to outdated WIP status
- Line counts match reality
- Documentation reflects actual codebase state
</must_haves>

<rollback_plan>
Documentation changes are easily reversible:
1. Restore old documentation files from backup
2. Re-apply updates with correct information
3. No code impact
</rollback_plan>
