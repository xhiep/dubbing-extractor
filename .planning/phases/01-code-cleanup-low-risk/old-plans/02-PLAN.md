---
wave: 1
plan_id: "02"
depends_on: []
files_modified:
  - main.py
autonomous: true
requirements_addressed: []
---

# Plan 02: Remove Pipeline State Dict and Duplicate Checkbox

<objective>
Xóa pipeline_state dict không sử dụng và duplicate quick_dub_toggle checkbox từ main.py. Cả hai đều là dead code từ tính năng step-by-step UI chưa hoàn thành.
</objective>

<tasks>

<task id="2.1">
<read_first>
- main.py (toàn bộ file để tìm pipeline_state declarations và references)
</read_first>

<action>
Tìm và xóa tất cả references đến pipeline_state:
- Search: grep -n "pipeline_state" main.py
- Xóa declaration: pipeline_state = {} hoặc pipeline_state = dict()
- Xóa tất cả reads: pipeline_state.get(...), pipeline_state[...]
- Xóa tất cả writes: pipeline_state[...] = ..., pipeline_state.update(...)

Nếu pipeline_state nằm trong function, xóa cả function đó nếu function chỉ để init pipeline_state.
</action>

<acceptance_criteria>
- grep -n "pipeline_state" main.py returns no results
- python -m py_compile main.py exits 0 (syntax valid)
- App launches without errors
</acceptance_criteria>
</task>

<task id="2.2">
<read_first>
- main.py (lines 190-220 để tìm duplicate checkbox)
- Tìm tất cả references đến quick_dub_toggle
</read_first>

<action>
Xóa duplicate quick_dub_toggle checkbox (lines 196-209 theo ROADMAP):

1. Tìm cả hai instances:
   grep -n "quick_dub_toggle" main.py

2. Xác định instance nào là duplicate:
   - Kiểm tra xem cả hai có cùng command/variable không
   - Kiểm tra xem cả hai có cùng parent container không

3. Xóa ONE instance (giữ instance ở vị trí đúng trong UI):
   - Xóa Checkbox widget creation
   - Xóa grid/pack placement
   - Giữ variable binding nếu được share

4. Verify chỉ còn MỘT checkbox visible trong UI.
</action>

<acceptance_criteria>
- grep -n "quick_dub_toggle" main.py returns exactly ONE widget creation (không phải hai)
- Hoặc: grep -c "Checkbox.*dub.*toggle" main.py returns 1 (chỉ một checkbox)
- python -m py_compile main.py exits 0
- Visual check: Chỉ một TTS enable checkbox trong UI
- Functional check: Checkbox vẫn controls TTS on/off
</acceptance_criteria>
</task>

<task id="2.3">
<read_first>
- main.py (verify changes)
</read_first>

<action>
Verify không có side effects:
- Check rằng TTS functionality vẫn hoạt động
- Check rằng config save/load vẫn hoạt động
- Check rằng không có orphaned variables
</action>

<acceptance_criteria>
- TTS checkbox vẫn controls enable_dub config
- Config.json vẫn saves/loads enable_dub setting
- Không có unused variables liên quan đến removed code
</acceptance_criteria>
</task>

</tasks>

<verification>
## Functional Verification
- [ ] App launches: python main.py
- [ ] No pipeline_state references: grep "pipeline_state" main.py
- [ ] Only one TTS checkbox visible in UI
- [ ] TTS checkbox controls dubbing on/off
- [ ] Config saves TTS setting correctly

## Code Quality
- [ ] Syntax valid: python -m py_compile main.py
- [ ] No unused variables from removed code
- [ ] Line count reduced by ~25-35 lines

## Regression Testing
- [ ] Launch app, check all tabs
- [ ] Toggle TTS checkbox, verify it works
- [ ] Save config, reload app, verify TTS setting persists
- [ ] Run one pipeline with TTS enabled
- [ ] Run one pipeline with TTS disabled
</verification>

<must_haves>
- pipeline_state completely removed
- Only one TTS checkbox remains
- TTS functionality still works
- Config save/load still works
- No syntax errors
</must_haves>

<rollback_plan>
If removal breaks TTS or config:
1. Restore main.py from backup
2. Investigate which checkbox was the "correct" one
3. Investigate if pipeline_state was actually used somewhere
4. Fix dependencies before re-attempting removal
</rollback_plan>
