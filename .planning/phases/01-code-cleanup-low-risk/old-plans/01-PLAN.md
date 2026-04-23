---
wave: 1
plan_id: "01"
depends_on: []
files_modified:
  - src/modules/workflow.py
autonomous: true
requirements_addressed: []
---

# Plan 01: Remove WIP Step Functions

<objective>
Xóa 7 step functions không sử dụng (step1_prepare through step7_dub) từ src/modules/workflow.py. Các functions này được tạo cho tính năng step-by-step UI nhưng không bao giờ được gọi vì UI không được hoàn thành.
</objective>

<tasks>

<task id="1.1">
<read_first>
- src/modules/workflow.py (toàn bộ file để xác định vị trí các step functions)
- main.py (verify không có calls đến step functions)
</read_first>

<action>
Xóa 7 step functions từ src/modules/workflow.py:
- step1_prepare() (lines ~108-145)
- step2_transcribe() (lines ~148-160)
- step3_translate() (lines ~163-183)
- step4_cover() (lines ~186-230)
- step5_export() (lines ~233-280)
- step6_burn() (lines ~283-320)
- step7_dub() (lines ~323-360)

Giữ nguyên:
- process_video() function (main pipeline, đang được sử dụng)
- Tất cả helper functions (_make_log, _apply_subtitle_timing, _retime_cover_events)
- Tất cả imports

Xóa comment block "CÁC HÀM STEP RIÊNG LẺ" (lines ~104-106) nếu có.
</action>

<acceptance_criteria>
- src/modules/workflow.py không chứa def step1_prepare(
- src/modules/workflow.py không chứa def step2_transcribe(
- src/modules/workflow.py không chứa def step3_translate(
- src/modules/workflow.py không chứa def step4_cover(
- src/modules/workflow.py không chứa def step5_export(
- src/modules/workflow.py không chứa def step6_burn(
- src/modules/workflow.py không chứa def step7_dub(
- src/modules/workflow.py vẫn chứa def process_video(
- grep -r "step[1-7]_" src/ main.py returns no results (không có calls)
- python -m py_compile src/modules/workflow.py exits 0 (syntax valid)
- wc -l src/modules/workflow.py shows ~350 lines (giảm từ ~600)
</acceptance_criteria>
</task>

<task id="1.2">
<read_first>
- src/modules/workflow.py (verify changes)
</read_first>

<action>
Verify rằng process_video() vẫn hoạt động sau khi xóa step functions:
- Check imports vẫn đầy đủ
- Check helper functions vẫn tồn tại
- Check không có references đến step functions
</action>

<acceptance_criteria>
- src/modules/workflow.py imports đầy đủ (download, transcribe, translate, etc.)
- _make_log, _apply_subtitle_timing, _retime_cover_events vẫn tồn tại
- process_video() function hoàn chỉnh và không reference step functions
</acceptance_criteria>
</task>

</tasks>

<verification>
## Functional Verification
- [ ] App launches: python main.py (no import errors)
- [ ] Workflow module imports: from src.modules.workflow import process_video
- [ ] No references to removed functions: grep -r "step[1-7]_" src/ main.py

## Code Quality
- [ ] Syntax valid: python -m py_compile src/modules/workflow.py
- [ ] No unused imports: flake8 --select=F401 src/modules/workflow.py
- [ ] Line count reduced: wc -l src/modules/workflow.py (~350 lines)

## Regression Testing
- [ ] Quick smoke test: Launch app, verify all tabs visible
- [ ] Process video still works (test with dummy_in.mp4 if available)
</verification>

<must_haves>
- step1-7 functions completely removed
- process_video() function intact and working
- No syntax errors
- App still launches
</must_haves>

<rollback_plan>
If removal breaks anything:
1. Restore src/modules/workflow.py from backup
2. Investigate what was calling the step functions (should be nothing)
3. Fix the actual issue before re-attempting removal
</rollback_plan>
