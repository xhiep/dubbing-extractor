---
wave: 2
plan_id: "02"
depends_on: ["01"]
files_modified:
  - src/controllers/source_controller.py
  - main.py
autonomous: true
requirements_addressed: []
---

# Plan 02: Extract Source Controller

<objective>
Tách tất cả event handlers của Source tab từ main.py vào SourceController. Đây là controller đầu tiên được extract để establish pattern cho các controllers khác.
</objective>

<tasks>

<task id="2.1">
<read_first>
- main.py (tìm tất cả event handlers liên quan đến source tab)
- src/modules/workflow.py (để hiểu process_video interface)
- src/modules/downloader/ytdlp_wrapper.py (để hiểu check_source_preconditions, fetch_preview_info)
</read_first>

<action>
Identify source tab event handlers trong main.py:

1. Search for event handlers:
   grep -n "def on_start\|def on_source\|def on_preview\|def on_fetch" main.py

2. Identify handlers to extract:
   - on_start_clicked() hoặc tương tự - Start processing button
   - on_source_changed() hoặc tương tự - Source input validation
   - on_preview_clicked() hoặc tương tự - Preview video info
   - Bất kỳ helper functions nào được gọi bởi các handlers trên

3. Document widget dependencies:
   - Widgets được read: source_input, cover_mode, whisper_model, etc.
   - Widgets được updated: log_area, status_label, progress_bar, etc.
   - Config keys được accessed: source_input, cover_mode, burn_sub, etc.

4. Document callback patterns:
   - Progress callback cho process_video()
   - Log callback cho workflow updates
</action>

<acceptance_criteria>
- List of all source tab event handlers identified
- Widget dependencies documented
- Config dependencies documented
- Callback patterns documented
</acceptance_criteria>
</task>

<task id="2.2">
<read_first>
- main.py (event handlers identified in task 2.1)
- src/controllers/source_controller.py (skeleton)
</read_first>

<action>
Extract event handlers vào SourceController:

1. Copy on_start_clicked() logic:
   - Tìm function trong main.py
   - Copy toàn bộ logic vào SourceController.on_start_clicked()
   - Replace direct widget access với self.widgets['name']
   - Replace direct config access với self.config['key']
   - Keep business logic calls unchanged (process_video, etc.)

2. Copy on_source_changed() logic:
   - Tìm function trong main.py
   - Copy vào SourceController.on_source_changed()
   - Replace widget/config access

3. Copy on_preview_clicked() logic:
   - Tìm function trong main.py
   - Copy vào SourceController.on_preview_clicked()
   - Replace widget/config access

4. Copy helper functions nếu có:
   - Tìm helper functions được gọi bởi handlers
   - Copy vào SourceController as private methods (_helper_name)

5. Implement _log_callback():
   ```python
   def _log_callback(self, message: str):
       \"\"\"Callback for progress updates.\"\"\"
       if 'log_area' in self.widgets:
           self.widgets['log_area'].append(message)
   ```

6. Add imports needed:
   ```python
   from pathlib import Path
   from src.modules.workflow import process_video
   from src.modules.downloader.ytdlp_wrapper import check_source_preconditions, fetch_preview_info
   from src.utils.file_utils import is_local_file
   # ... any other imports needed
   ```
</action>

<acceptance_criteria>
- All source tab event handlers copied to SourceController
- All widget access uses self.widgets['name']
- All config access uses self.config['key']
- All necessary imports added
- python -m py_compile src/controllers/source_controller.py exits 0
- No business logic duplicated (calls to modules unchanged)
</acceptance_criteria>
</task>

<task id="2.3">
<read_first>
- main.py (source tab creation code)
- src/controllers/source_controller.py (extracted handlers)
</read_first>

<action>
Wire up SourceController trong main.py:

1. Tìm source tab creation code trong main.py:
   - Tìm function tạo source tab (có thể là create_source_tab() hoặc inline code)
   - Identify tất cả widgets trong source tab

2. Create widget dictionary:
   ```python
   # After creating all source tab widgets
   source_widgets = {
       'source_input': source_input,
       'cover_mode': cover_mode_combo,
       'whisper_model': whisper_model_combo,
       'burn_sub': burn_sub_checkbox,
       'log_area': log_text_area,
       'status_label': status_label,
       'progress_bar': progress_bar,
       # ... all widgets needed by controller
   }
   ```

3. Import controller:
   ```python
   from src.controllers import SourceController
   ```

4. Create controller instance:
   ```python
   # After creating source_widgets dict
   source_ctrl = SourceController(source_widgets, config)
   ```

5. Wire up events:
   ```python
   # Replace old event handlers with controller methods
   start_button.config(command=source_ctrl.on_start_clicked)
   source_input.bind('<FocusOut>', source_ctrl.on_source_changed)
   preview_button.config(command=source_ctrl.on_preview_clicked)
   # ... wire all events
   ```

6. Remove old event handler functions:
   - Delete on_start_clicked() function từ main.py
   - Delete on_source_changed() function từ main.py
   - Delete on_preview_clicked() function từ main.py
   - Delete helper functions đã moved to controller
</action>

<acceptance_criteria>
- SourceController imported trong main.py
- source_widgets dict created với all required widgets
- SourceController instance created
- All events wired to controller methods
- Old event handler functions removed từ main.py
- python -m py_compile main.py exits 0
- App launches: python main.py
</acceptance_criteria>
</task>

<task id="2.4">
<read_first>
- main.py (verify changes)
- src/controllers/source_controller.py (verify implementation)
</read_first>

<action>
Test SourceController integration:

1. Launch app:
   python main.py

2. Test source tab functionality:
   - Enter source URL/path
   - Verify on_source_changed fires
   - Click preview button
   - Verify preview works
   - Click start button
   - Verify processing starts
   - Verify progress updates appear in log

3. Test error handling:
   - Enter invalid source
   - Verify error message shows
   - Try empty source
   - Verify validation works

4. Test config integration:
   - Change settings
   - Start processing
   - Verify settings used correctly

5. Count lines saved:
   wc -l main.py
   # Should be ~200-300 lines less than before
</action>

<acceptance_criteria>
- App launches without errors
- Source input works
- Preview button works
- Start button works
- Progress updates appear in log
- Error handling works
- Config integration works
- main.py reduced by ~200-300 lines
</acceptance_criteria>
</task>

</tasks>

<verification>
## Functional Verification
- [ ] App launches: python main.py
- [ ] Source tab loads correctly
- [ ] Source input accepts text
- [ ] Preview button fetches video info
- [ ] Start button starts processing
- [ ] Progress updates show in log
- [ ] Error messages display correctly

## Code Quality
- [ ] SourceController syntax valid
- [ ] main.py syntax valid
- [ ] No duplicate code (business logic in modules)
- [ ] Widget access via self.widgets dict
- [ ] Config access via self.config dict

## Integration
- [ ] Controller properly wired to UI
- [ ] All events fire correctly
- [ ] Callbacks work (progress updates)
- [ ] Config save/load still works

## Regression Testing
- [ ] Run complete pipeline (download → dub)
- [ ] Verify no functionality lost
- [ ] Verify all source tab features work
</verification>

<must_haves>
- SourceController fully implemented
- All source tab handlers extracted
- Controller wired to UI
- All functionality working
- No regressions
</must_haves>

<notes>
Wave 2 because depends on Plan 01 (controller structure).

This is the first controller extraction - establishes pattern for others.

If this works, Plans 03-05 will follow same pattern for other controllers.

Estimated lines moved: ~200-300 from main.py to source_controller.py
</notes>

<rollback_plan>
If extraction breaks source tab:
1. Restore main.py from backup
2. Identify which handler broke
3. Check widget dict keys match
4. Check callback signatures match
5. Fix and re-test
</rollback_plan>
