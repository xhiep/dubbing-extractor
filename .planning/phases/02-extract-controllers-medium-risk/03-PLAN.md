---
wave: 2
plan_id: "03"
depends_on: ["01", "02"]
files_modified:
  - src/controllers/subtitle_controller.py
  - main.py
autonomous: true
requirements_addressed: []
---

# Plan 03: Extract Subtitle Controller

<objective>
Tách tất cả event handlers của Subtitle tab từ main.py vào SubtitleController. Follow pattern đã establish trong Plan 02 (SourceController).
</objective>

<tasks>

<task id="3.1">
<read_first>
- main.py (tìm tất cả event handlers liên quan đến subtitle tab)
- src/modules/video_processing/subtitle_cover.py (để hiểu cover interface)
- src/modules/video_processing/subtitle_burn.py (để hiểu burn interface)
</read_first>

<action>
Identify subtitle tab event handlers trong main.py:

1. Search for event handlers:
   grep -n "def on_cover\|def on_preset\|def on_blur\|def on_subtitle" main.py

2. Identify handlers to extract:
   - on_cover_mode_changed() - Cover mode selection (blur/blackbar/none)
   - on_preview_subtitle() - Preview subtitle layout
   - on_blur_params_changed() - Blur parameter adjustments
   - on_preset_changed() - Subtitle preset selection
   - on_subtitle_params_changed() - Font size, margin, etc.
   - Helper functions được gọi bởi các handlers trên

3. Document widget dependencies:
   - Widgets được read: cover_mode_combo, blur_radius, blur_strength, preset_combo, font_size, margin_v, etc.
   - Widgets được updated: preview_area, status_label, etc.
   - Config keys được accessed: cover_mode, blur_params, subtitle_preset, font_params, etc.

4. Document SUBTITLE_PRESETS constant:
   - Constant này có thể cần move vào controller hoặc separate config file
   - Document current location và usage
</action>

<acceptance_criteria>
- List of all subtitle tab event handlers identified
- Widget dependencies documented
- Config dependencies documented
- SUBTITLE_PRESETS usage documented
</acceptance_criteria>
</task>

<task id="3.2">
<read_first>
- main.py (event handlers identified in task 3.1)
- src/controllers/subtitle_controller.py (skeleton)
</read_first>

<action>
Extract event handlers vào SubtitleController:

1. Copy on_cover_mode_changed() logic:
   - Tìm function trong main.py
   - Copy toàn bộ logic vào SubtitleController.on_cover_mode_changed()
   - Replace direct widget access với self.widgets['name']
   - Replace direct config access với self.config['key']

2. Copy on_preview_subtitle() logic:
   - Tìm function trong main.py
   - Copy vào SubtitleController.on_preview_subtitle()
   - Replace widget/config access

3. Copy on_blur_params_changed() logic:
   - Tìm function trong main.py
   - Copy vào SubtitleController.on_blur_params_changed()
   - Replace widget/config access

4. Copy on_preset_changed() logic:
   - Tìm function trong main.py
   - Copy vào SubtitleController.on_preset_changed()
   - Replace widget/config access
   - Handle SUBTITLE_PRESETS constant

5. Copy on_subtitle_params_changed() logic:
   - Tìm function trong main.py
   - Copy vào SubtitleController.on_subtitle_params_changed()
   - Replace widget/config access

6. Copy helper functions nếu có:
   - Tìm helper functions được gọi bởi handlers
   - Copy vào SubtitleController as private methods (_helper_name)

7. Handle SUBTITLE_PRESETS constant:
   - Option 1: Move vào SubtitleController as class constant
   - Option 2: Keep in main.py, pass via constructor
   - Recommend: Move vào controller để encapsulate subtitle logic

8. Add imports needed:
   ```python
   from pathlib import Path
   from src.modules.video_processing.subtitle_cover import apply_cover
   from src.modules.video_processing.subtitle_burn import burn_subtitles
   # ... any other imports needed
   ```
</action>

<acceptance_criteria>
- All subtitle tab event handlers copied to SubtitleController
- All widget access uses self.widgets['name']
- All config access uses self.config['key']
- SUBTITLE_PRESETS handled (moved or passed)
- All necessary imports added
- python -m py_compile src/controllers/subtitle_controller.py exits 0
- No business logic duplicated (calls to modules unchanged)
</acceptance_criteria>
</task>

<task id="3.3">
<read_first>
- main.py (subtitle tab creation code)
- src/controllers/subtitle_controller.py (extracted handlers)
</read_first>

<action>
Wire up SubtitleController trong main.py:

1. Tìm subtitle tab creation code trong main.py:
   - Tìm function tạo subtitle tab (có thể là create_subtitle_tab() hoặc inline code)
   - Identify tất cả widgets trong subtitle tab

2. Create widget dictionary:
   ```python
   # After creating all subtitle tab widgets
   subtitle_widgets = {
       'cover_mode': cover_mode_combo,
       'blur_radius': blur_radius_slider,
       'blur_strength': blur_strength_slider,
       'preset_combo': preset_combo,
       'font_size': font_size_input,
       'margin_v': margin_v_input,
       'margin_h': margin_h_input,
       'preview_area': preview_area,
       'status_label': status_label,
       # ... all widgets needed by controller
   }
   ```

3. Import controller:
   ```python
   from src.controllers import SubtitleController
   ```

4. Create controller instance:
   ```python
   # After creating subtitle_widgets dict
   subtitle_ctrl = SubtitleController(subtitle_widgets, config)
   ```

5. Wire up events:
   ```python
   # Replace old event handlers with controller methods
   cover_mode_combo.bind('<<ComboboxSelected>>', subtitle_ctrl.on_cover_mode_changed)
   preset_combo.bind('<<ComboboxSelected>>', subtitle_ctrl.on_preset_changed)
   blur_radius_slider.config(command=subtitle_ctrl.on_blur_params_changed)
   blur_strength_slider.config(command=subtitle_ctrl.on_blur_params_changed)
   preview_button.config(command=subtitle_ctrl.on_preview_subtitle)
   # ... wire all events
   ```

6. Remove old event handler functions:
   - Delete on_cover_mode_changed() function từ main.py
   - Delete on_preview_subtitle() function từ main.py
   - Delete on_blur_params_changed() function từ main.py
   - Delete on_preset_changed() function từ main.py
   - Delete on_subtitle_params_changed() function từ main.py
   - Delete helper functions đã moved to controller
   - Delete SUBTITLE_PRESETS constant nếu đã moved to controller
</action>

<acceptance_criteria>
- SubtitleController imported trong main.py
- subtitle_widgets dict created với all required widgets
- SubtitleController instance created
- All events wired to controller methods
- Old event handler functions removed từ main.py
- SUBTITLE_PRESETS removed từ main.py nếu moved to controller
- python -m py_compile main.py exits 0
- App launches: python main.py
</acceptance_criteria>
</task>

<task id="3.4">
<read_first>
- main.py (verify changes)
- src/controllers/subtitle_controller.py (verify implementation)
</read_first>

<action>
Test SubtitleController integration:

1. Launch app:
   python main.py

2. Test subtitle tab functionality:
   - Change cover mode (blur/blackbar/none)
   - Verify on_cover_mode_changed fires
   - Adjust blur parameters
   - Verify on_blur_params_changed fires
   - Select subtitle preset
   - Verify preset applied correctly
   - Change font size/margin
   - Verify on_subtitle_params_changed fires
   - Click preview button
   - Verify preview works

3. Test error handling:
   - Try invalid blur values
   - Verify error message shows
   - Try invalid font size
   - Verify validation works

4. Test config integration:
   - Change subtitle settings
   - Close app
   - Reopen app
   - Verify settings persisted

5. Count lines saved:
   wc -l main.py
   # Should be ~200-250 lines less than after Plan 02
</action>

<acceptance_criteria>
- App launches without errors
- Cover mode selection works
- Blur parameter adjustments work
- Preset selection works
- Font/margin adjustments work
- Preview button works
- Error handling works
- Config integration works
- main.py reduced by ~200-250 lines
</acceptance_criteria>
</task>

</tasks>

<verification>
## Functional Verification
- [ ] App launches: python main.py
- [ ] Subtitle tab loads correctly
- [ ] Cover mode selection works
- [ ] Blur parameters adjustable
- [ ] Preset selection applies correctly
- [ ] Font/margin adjustments work
- [ ] Preview button works
- [ ] Error messages display correctly

## Code Quality
- [ ] SubtitleController syntax valid
- [ ] main.py syntax valid
- [ ] No duplicate code (business logic in modules)
- [ ] Widget access via self.widgets dict
- [ ] Config access via self.config dict

## Integration
- [ ] Controller properly wired to UI
- [ ] All events fire correctly
- [ ] Config save/load still works
- [ ] SUBTITLE_PRESETS handled correctly

## Regression Testing
- [ ] Run complete pipeline (download → dub)
- [ ] Verify no functionality lost
- [ ] Verify all subtitle tab features work
</verification>

<must_haves>
- SubtitleController fully implemented
- All subtitle tab handlers extracted
- Controller wired to UI
- All functionality working
- No regressions
</must_haves>

<notes>
Wave 2 because depends on Plan 01 (controller structure) and Plan 02 (pattern established).

This follows same pattern as SourceController extraction.

SUBTITLE_PRESETS constant should be moved into SubtitleController to keep subtitle logic encapsulated.

Estimated lines moved: ~200-250 from main.py to subtitle_controller.py
</notes>

<rollback_plan>
If extraction breaks subtitle tab:
1. Restore main.py from backup
2. Identify which handler broke
3. Check widget dict keys match
4. Check SUBTITLE_PRESETS access
5. Fix and re-test
</rollback_plan>
