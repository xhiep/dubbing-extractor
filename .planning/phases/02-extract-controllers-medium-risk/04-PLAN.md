---
wave: 2
plan_id: "04"
depends_on: ["01", "02", "03"]
files_modified:
  - src/controllers/tts_controller.py
  - main.py
autonomous: true
requirements_addressed: []
---

# Plan 04: Extract TTS Controller

<objective>
Tách tất cả event handlers của TTS tab từ main.py vào TtsController. Follow pattern đã establish trong Plans 02-03.
</objective>

<tasks>

<task id="4.1">
<read_first>
- main.py (tìm tất cả event handlers liên quan đến TTS tab)
- src/modules/tts/vieneu_tts.py (để hiểu TTS interface)
</read_first>

<action>
Identify TTS tab event handlers trong main.py:

1. Search for event handlers:
   grep -n "def on_dub\|def on_voice\|def on_tts\|def on_ref_audio\|def on_volume" main.py

2. Identify handlers to extract:
   - on_dub_mode_changed() - TTS mode selection (preset/clone/remote)
   - on_voice_changed() - Voice selection
   - on_tts_preview() - TTS preview
   - on_ref_audio_browse() - Browse reference audio file
   - on_volume_changed() - Volume slider adjustments (original/dubbed)
   - Helper functions được gọi bởi các handlers trên

3. Document widget dependencies:
   - Widgets được read: dub_mode_combo, voice_combo, ref_audio_input, volume_original, volume_dubbed, etc.
   - Widgets được updated: tts_status_label, preview_player, etc.
   - Config keys được accessed: dub_mode, voice_name, ref_audio_path, volume_original, volume_dubbed, etc.

4. Document voice list management:
   - Voice list có thể được load từ VieNeu-TTS
   - Document how voice_combo được populated
</action>

<acceptance_criteria>
- List of all TTS tab event handlers identified
- Widget dependencies documented
- Config dependencies documented
- Voice list management documented
</acceptance_criteria>
</task>

<task id="4.2">
<read_first>
- main.py (event handlers identified in task 4.1)
- src/controllers/tts_controller.py (skeleton)
</read_first>

<action>
Extract event handlers vào TtsController:

1. Copy on_dub_mode_changed() logic:
   - Tìm function trong main.py
   - Copy toàn bộ logic vào TtsController.on_dub_mode_changed()
   - Replace direct widget access với self.widgets['name']
   - Replace direct config access với self.config['key']
   - Handle mode-specific UI updates (show/hide ref_audio controls)

2. Copy on_voice_changed() logic:
   - Tìm function trong main.py
   - Copy vào TtsController.on_voice_changed()
   - Replace widget/config access

3. Copy on_tts_preview() logic:
   - Tìm function trong main.py
   - Copy vào TtsController.on_tts_preview()
   - Replace widget/config access
   - Keep TTS module calls unchanged

4. Copy on_ref_audio_browse() logic:
   - Tìm function trong main.py
   - Copy vào TtsController.on_ref_audio_browse()
   - Replace widget/config access
   - Handle file dialog

5. Copy on_volume_changed() logic:
   - Tìm function trong main.py
   - Copy vào TtsController.on_volume_changed()
   - Replace widget/config access
   - Handle both original and dubbed volume

6. Copy helper functions nếu có:
   - Tìm helper functions được gọi bởi handlers
   - Copy vào TtsController as private methods (_helper_name)

7. Add voice list loading method:
   ```python
   def _load_voices(self):
       """Load available voices from VieNeu-TTS."""
       # Logic to populate voice_combo
       pass
   ```

8. Add imports needed:
   ```python
   from pathlib import Path
   from tkinter import filedialog
   from src.modules.tts.vieneu_tts import VieNeuTTS, get_available_voices
   # ... any other imports needed
   ```
</action>

<acceptance_criteria>
- All TTS tab event handlers copied to TtsController
- All widget access uses self.widgets['name']
- All config access uses self.config['key']
- Voice list loading implemented
- All necessary imports added
- python -m py_compile src/controllers/tts_controller.py exits 0
- No business logic duplicated (calls to modules unchanged)
</acceptance_criteria>
</task>

<task id="4.3">
<read_first>
- main.py (TTS tab creation code)
- src/controllers/tts_controller.py (extracted handlers)
</read_first>

<action>
Wire up TtsController trong main.py:

1. Tìm TTS tab creation code trong main.py:
   - Tìm function tạo TTS tab (có thể là create_tts_tab() hoặc inline code)
   - Identify tất cả widgets trong TTS tab

2. Create widget dictionary:
   ```python
   # After creating all TTS tab widgets
   tts_widgets = {
       'dub_mode': dub_mode_combo,
       'voice_combo': voice_combo,
       'ref_audio_input': ref_audio_input,
       'ref_audio_browse': ref_audio_browse_button,
       'volume_original': volume_original_slider,
       'volume_dubbed': volume_dubbed_slider,
       'tts_status': tts_status_label,
       'preview_button': preview_button,
       # ... all widgets needed by controller
   }
   ```

3. Import controller:
   ```python
   from src.controllers import TtsController
   ```

4. Create controller instance:
   ```python
   # After creating tts_widgets dict
   tts_ctrl = TtsController(tts_widgets, config)
   ```

5. Wire up events:
   ```python
   # Replace old event handlers with controller methods
   dub_mode_combo.bind('<<ComboboxSelected>>', tts_ctrl.on_dub_mode_changed)
   voice_combo.bind('<<ComboboxSelected>>', tts_ctrl.on_voice_changed)
   ref_audio_browse_button.config(command=tts_ctrl.on_ref_audio_browse)
   volume_original_slider.config(command=tts_ctrl.on_volume_changed)
   volume_dubbed_slider.config(command=tts_ctrl.on_volume_changed)
   preview_button.config(command=tts_ctrl.on_tts_preview)
   # ... wire all events
   ```

6. Remove old event handler functions:
   - Delete on_dub_mode_changed() function từ main.py
   - Delete on_voice_changed() function từ main.py
   - Delete on_tts_preview() function từ main.py
   - Delete on_ref_audio_browse() function từ main.py
   - Delete on_volume_changed() function từ main.py
   - Delete helper functions đã moved to controller
</action>

<acceptance_criteria>
- TtsController imported trong main.py
- tts_widgets dict created với all required widgets
- TtsController instance created
- All events wired to controller methods
- Old event handler functions removed từ main.py
- python -m py_compile main.py exits 0
- App launches: python main.py
</acceptance_criteria>
</task>

<task id="4.4">
<read_first>
- main.py (verify changes)
- src/controllers/tts_controller.py (verify implementation)
</read_first>

<action>
Test TtsController integration:

1. Launch app:
   python main.py

2. Test TTS tab functionality:
   - Change dub mode (preset/clone/remote)
   - Verify on_dub_mode_changed fires
   - Verify UI updates (ref_audio controls show/hide)
   - Select voice
   - Verify on_voice_changed fires
   - Browse reference audio
   - Verify file dialog works
   - Adjust volume sliders
   - Verify on_volume_changed fires
   - Click preview button
   - Verify TTS preview works

3. Test error handling:
   - Try invalid reference audio path
   - Verify error message shows
   - Try preview without voice selected
   - Verify validation works

4. Test config integration:
   - Change TTS settings
   - Close app
   - Reopen app
   - Verify settings persisted

5. Count lines saved:
   wc -l main.py
   # Should be ~150-200 lines less than after Plan 03
</action>

<acceptance_criteria>
- App launches without errors
- Dub mode selection works
- Voice selection works
- Reference audio browse works
- Volume adjustments work
- TTS preview works
- Error handling works
- Config integration works
- main.py reduced by ~150-200 lines
</acceptance_criteria>
</task>

</tasks>

<verification>
## Functional Verification
- [ ] App launches: python main.py
- [ ] TTS tab loads correctly
- [ ] Dub mode selection works
- [ ] Voice selection works
- [ ] Reference audio browse works
- [ ] Volume sliders work
- [ ] TTS preview works
- [ ] Error messages display correctly

## Code Quality
- [ ] TtsController syntax valid
- [ ] main.py syntax valid
- [ ] No duplicate code (business logic in modules)
- [ ] Widget access via self.widgets dict
- [ ] Config access via self.config dict

## Integration
- [ ] Controller properly wired to UI
- [ ] All events fire correctly
- [ ] Config save/load still works
- [ ] Voice list loads correctly

## Regression Testing
- [ ] Run complete pipeline (download → dub)
- [ ] Verify no functionality lost
- [ ] Verify all TTS tab features work
</verification>

<must_haves>
- TtsController fully implemented
- All TTS tab handlers extracted
- Controller wired to UI
- All functionality working
- No regressions
</must_haves>

<notes>
Wave 2 because depends on Plan 01 (controller structure) and Plans 02-03 (pattern established).

This follows same pattern as SourceController and SubtitleController extraction.

TTS controller is simpler than subtitle controller - fewer handlers, less complex logic.

Estimated lines moved: ~150-200 from main.py to tts_controller.py
</notes>

<rollback_plan>
If extraction breaks TTS tab:
1. Restore main.py from backup
2. Identify which handler broke
3. Check widget dict keys match
4. Check voice list loading
5. Fix and re-test
</rollback_plan>
