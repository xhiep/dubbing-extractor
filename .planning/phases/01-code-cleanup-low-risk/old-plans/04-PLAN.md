---
wave: 3
plan_id: "04"
depends_on: ["01", "02", "03"]
files_modified:
  - CLAUDE.md
  - README.md
  - DESIGN.md
  - .planning/codebase/ARCHITECTURE.md
autonomous: true
requirements_addressed: []
---

# Plan 04: Update Documentation

<objective>
Cập nhật tất cả documentation để phản ánh chính xác codebase sau cleanup: fix line counts, remove references đến removed code, update architecture descriptions.
</objective>

<tasks>

<task id="4.1">
<read_first>
- CLAUDE.md (toàn bộ file)
- main.py (để đếm lines chính xác)
- src/modules/workflow.py (để đếm lines chính xác)
</read_first>

<action>
Update CLAUDE.md với thông tin chính xác:

1. Fix line count trong "Cấu trúc chính":
   - Đếm: wc -l main.py
   - Update: `main.py` — entry point + toàn bộ GUI (Tkinter, ~XXXX dòng)
   - Hiện tại nói ~1760, thực tế ~3000, sau cleanup sẽ ~2800

2. Update "Pipeline workflow" section:
   - Giữ nguyên 7 bước (vẫn đúng với process_video())
   - Không cần thay đổi gì vì process_video() vẫn làm đúng 7 bước

3. REMOVE "Việc đang làm" section hoàn toàn:
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
   
   Replace with:
   ```markdown
   ## Trạng thái hiện tại
   Codebase đã được dọn dẹp (Phase 1 complete - 2026-04-23):
   - Xóa step functions không dùng
   - Xóa pipeline_state dict không dùng
   - Xóa duplicate UI controls
   - Xóa commented code và unused imports
   Backup: `C:\Users\xhiep\Downloads\dubbing-extractor-backup-20260423_1630`
   ```

4. Verify tất cả file paths vẫn đúng.
</action>

<acceptance_criteria>
- CLAUDE.md chứa line count chính xác cho main.py (wc -l main.py)
- CLAUDE.md không còn section "Việc đang làm" về step-by-step UI
- CLAUDE.md có section "Trạng thái hiện tại" mới
- Tất cả file paths trong CLAUDE.md vẫn valid
- CLAUDE.md syntax valid (markdown)
</acceptance_criteria>
</task>

<task id="4.2">
<read_first>
- README.md (toàn bộ file)
- DESIGN.md (toàn bộ file)
</read_first>

<action>
Update README.md và DESIGN.md nếu có references đến removed code:

1. Check README.md:
   - Search for references to step functions: grep -i "step[1-7]" README.md
   - Search for references to pipeline_state: grep -i "pipeline_state" README.md
   - Update any line counts if present
   - Update architecture description if present

2. Check DESIGN.md:
   - Search for UI component references to removed checkboxes
   - Update any component counts if present
   - Verify design system description still accurate

3. If no references found, no changes needed.
</action>

<acceptance_criteria>
- README.md không reference removed code (step functions, pipeline_state)
- DESIGN.md không reference removed UI components
- Line counts accurate nếu có
- Architecture descriptions accurate nếu có
</acceptance_criteria>
</task>

<task id="4.3">
<read_first>
- .planning/codebase/ARCHITECTURE.md
- .planning/codebase/STRUCTURE.md
- .planning/codebase/CONCERNS.md
</read_first>

<action>
Update codebase mapping documents:

1. Update ARCHITECTURE.md:
   - Update line count cho main.py (~2800 sau cleanup)
   - Update line count cho workflow.py (~350 sau cleanup)
   - Remove references to step functions trong "Workflow Orchestration Layer"
   - Update "Pipeline state management (in progress)" → remove hoặc mark as "removed"

2. Update STRUCTURE.md:
   - Update line counts nếu có
   - Verify file structure vẫn accurate

3. Update CONCERNS.md:
   - Remove "Work In Progress" section về step-by-step UI
   - Update "Known Issues" nếu có
   - Mark Phase 1 cleanup as COMPLETE

4. Count actual lines:
   wc -l main.py src/modules/workflow.py
</action>

<acceptance_criteria>
- .planning/codebase/ARCHITECTURE.md có line counts chính xác
- .planning/codebase/ARCHITECTURE.md không reference step functions
- .planning/codebase/CONCERNS.md không còn "Work In Progress" section
- .planning/codebase/STRUCTURE.md accurate
- All line counts match actual: wc -l <file>
</acceptance_criteria>
</task>

<task id="4.4">
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
   - Lines removed: ~450 total
   - Files cleaned: main.py, workflow.py, all modules
   - Documentation updated: CLAUDE.md, codebase maps
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
- [ ] CLAUDE.md line counts accurate: wc -l main.py src/modules/workflow.py
- [ ] CLAUDE.md không reference removed code
- [ ] README.md accurate (if updated)
- [ ] DESIGN.md accurate (if updated)
- [ ] .planning/codebase/*.md accurate

## Consistency Check
- [ ] All docs agree on line counts
- [ ] All docs agree on architecture
- [ ] No contradictions between docs
- [ ] No references to removed features

## Completeness
- [ ] All changed files documented
- [ ] All removed code documented
- [ ] Phase 1 marked complete in CONCERNS.md
</verification>

<must_haves>
- CLAUDE.md accurate and up-to-date
- No references to removed code in any documentation
- Line counts match reality
- Codebase maps reflect current state
</must_haves>

<notes>
Wave 3 because documentation should be updated AFTER all code changes are complete. This ensures line counts and references are accurate.

This task is pure documentation - no code changes, no risk of breaking functionality.
</notes>

<rollback_plan>
Documentation changes are easily reversible:
1. Restore old documentation files from backup
2. Re-apply updates with correct information
3. No code impact
</rollback_plan>
