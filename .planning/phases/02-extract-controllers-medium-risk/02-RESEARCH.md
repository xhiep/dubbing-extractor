---
phase: 2
name: Extract Controllers (Medium Risk)
created: 2026-04-23
status: complete
---

# Phase 2 Research: Extract Controllers (Medium Risk)

## Objective

Nghiên cứu cách tách event handlers ra khỏi main.py vào controller classes theo MVC pattern, giảm main.py từ ~2800 lines xuống ~2000 lines mà không làm break functionality.

## Phase Scope

**Goal**: Tách event handlers ra khỏi main.py vào controller classes

**Duration**: 3-4 giờ

**Risk Level**: MEDIUM - Di chuyển code, có thể break event handling

## Current Architecture Analysis

### main.py Structure (~2800 lines sau Phase 1)

**Current State**:
- Monolithic file chứa tất cả: UI layout, event handlers, helper functions
- Event handlers mixed với UI creation code
- No clear separation between presentation và control logic

**Breakdown**:
- Imports: ~50 lines
- Helper functions: ~100 lines (_expand_band_from_center, _shift_band, etc.)
- Constants/Presets: ~100 lines (SUBTITLE_PRESETS, etc.)
- Tab creation functions: ~2000 lines (create tabs, wire events)
- Main app class/logic: ~500 lines
- Entry point: ~50 lines

**Event Handlers Currently in main.py**:
1. **Source Tab**:
   - `on_start_clicked()` - Start processing button
   - `on_source_changed()` - Source input change
   - `on_preview_clicked()` - Preview video info
   - `on_fetch_info()` - Fetch video metadata

2. **Subtitle Tab**:
   - `on_cover_mode_changed()` - Cover mode selection (blur/blackbar/none)
   - `on_preview_subtitle()` - Preview subtitle layout
   - `on_blur_params_changed()` - Blur parameter adjustments
   - `on_preset_changed()` - Subtitle preset selection
   - `on_subtitle_params_changed()` - Font size, margin, etc.

3. **TTS Tab**:
   - `on_dub_mode_changed()` - TTS mode selection (preset/clone/remote)
   - `on_voice_changed()` - Voice selection
   - `on_tts_preview()` - TTS preview
   - `on_ref_audio_browse()` - Browse reference audio
   - `on_volume_changed()` - Volume adjustments

4. **App-Level**:
   - `on_config_save()` - Save config.json
   - `on_config_load()` - Load config.json
   - `on_window_close()` - Window close handler
   - `on_tab_changed()` - Tab switch handler

## MVC Pattern for Tkinter

### Model-View-Controller Separation

**Model** (already good):
- `src/modules/workflow.py` - business logic
- `src/modules/downloader/` - download logic
- `src/modules/transcription/` - transcription logic
- `src/modules/video_processing/` - video processing logic
- `src/modules/tts/` - TTS logic

**View** (already good):
- `src/components/ui/` - reusable widgets (Button, Input, etc.)
- `src/components/layout/` - layout containers (Card, Section, etc.)
- `main.py` - tab layouts (will remain)

**Controller** (MISSING - to be created):
- `src/controllers/` - event handlers
- Controllers mediate between View and Model
- Controllers are thin - no business logic

### Controller Pattern Design

**Controller Responsibilities**:
1. Receive events from UI widgets
2. Read data from UI widgets
3. Call Model (business logic)
4. Update UI with results
5. Handle errors and show user feedback

**Controller Structure**:
```python
class SourceController:
    def __init__(self, widgets, config):
        """
        Args:
            widgets: dict of widget references (inputs, buttons, labels, etc.)
            config: global config dict
        """
        self.widgets = widgets
        self.config = config
    
    def on_start_clicked(self):
        """Handle start button click."""
        # 1. Read from UI
        source = self.widgets['source_input'].get()
        cover_mode = self.widgets['cover_mode'].get()
        
        # 2. Validate
        if not source:
            self.widgets['log_area'].append("Error: No source provided")
            return
        
        # 3. Call Model
        try:
            result = process_video(source, cover_mode, log_cb=self._log_callback)
        except Exception as e:
            self.widgets['log_area'].append(f"Error: {e}")
            return
        
        # 4. Update UI
        self.widgets['log_area'].append("Processing complete!")
        self.widgets['output_dir'].set(result['out_dir'])
    
    def _log_callback(self, message):
        """Callback for progress updates."""
        self.widgets['log_area'].append(message)
```

**Key Principles**:
- Controllers don't contain business logic (that's in Model)
- Controllers don't create UI (that's in View/main.py)
- Controllers are thin glue code
- Controllers can be tested by mocking widgets

## Proposed Controller Structure

### Directory Layout

```
src/controllers/
  __init__.py           # Export all controllers
  app_controller.py     # App-level events (config, window close)
  source_controller.py  # Source tab events
  subtitle_controller.py # Subtitle tab events
  tts_controller.py     # TTS tab events
```

### Controller Responsibilities

**app_controller.py**:
- `on_config_save()` - Save config.json
- `on_config_load()` - Load config.json
- `on_window_close()` - Cleanup and close
- `on_tab_changed()` - Tab switch logic
- Coordinate between other controllers if needed

**source_controller.py**:
- `on_start_clicked()` - Start processing
- `on_source_changed()` - Source input validation
- `on_preview_clicked()` - Fetch video info
- `on_fetch_info()` - Get video metadata
- Progress callback handling

**subtitle_controller.py**:
- `on_cover_mode_changed()` - Update cover mode
- `on_preview_subtitle()` - Preview subtitle layout
- `on_blur_params_changed()` - Update blur params
- `on_preset_changed()` - Apply subtitle preset
- `on_subtitle_params_changed()` - Update font/margin

**tts_controller.py**:
- `on_dub_mode_changed()` - Switch TTS mode
- `on_voice_changed()` - Select voice
- `on_tts_preview()` - Preview TTS
- `on_ref_audio_browse()` - Browse reference audio
- `on_volume_changed()` - Update volumes

## Widget References Pattern

### Problem: Controllers Need Widget Access

Controllers need to:
- Read values from inputs
- Update labels/text areas
- Enable/disable buttons
- Show/hide widgets

### Solution: Widget Dictionary

**In main.py** (when creating tabs):
```python
# Create widgets
source_input = Input(parent, ...)
cover_mode_combo = ttk.Combobox(parent, ...)
log_area = TextArea(parent, ...)
start_button = Button(parent, ...)

# Collect widget references
source_widgets = {
    'source_input': source_input,
    'cover_mode': cover_mode_combo,
    'log_area': log_area,
    'start_button': start_button,
    # ... all widgets in source tab
}

# Create controller
source_ctrl = SourceController(source_widgets, config)

# Wire events
start_button.config(command=source_ctrl.on_start_clicked)
source_input.bind('<FocusOut>', lambda e: source_ctrl.on_source_changed())
```

**Benefits**:
- Controllers don't need to know widget hierarchy
- Easy to mock widgets for testing
- Clear contract: controller expects certain widget keys

## Migration Strategy

### Step-by-Step Approach

**Step 1: Create Controller Structure**
- Create `src/controllers/` directory
- Create `__init__.py` with exports
- Create empty controller files

**Step 2: Extract One Controller (Source)**
- Identify all source tab event handlers in main.py
- Copy handlers to `source_controller.py`
- Convert to methods of SourceController class
- Replace direct widget access with `self.widgets['name']`
- Test thoroughly

**Step 3: Wire Up Source Controller**
- In main.py, create SourceController instance
- Pass widget dict to controller
- Wire button commands to controller methods
- Test all source tab functionality

**Step 4: Repeat for Other Controllers**
- Extract subtitle controller
- Extract TTS controller
- Extract app controller
- Test after each extraction

**Step 5: Clean Up main.py**
- Remove extracted event handlers
- Keep only UI creation code
- Verify line count reduction

### Risk Mitigation

**Risks**:
1. Breaking event bindings
2. Widget reference errors
3. Callback signature mismatches
4. State management issues

**Mitigations**:
1. Extract one controller at a time
2. Test thoroughly after each extraction
3. Keep widget dict keys consistent
4. Document expected widget keys in controller docstrings

## Testing Strategy

### Manual Testing Checklist

**After Each Controller Extraction**:
- [ ] App launches without errors
- [ ] All buttons in extracted tab work
- [ ] All inputs in extracted tab work
- [ ] All dropdowns in extracted tab work
- [ ] Config save/load works
- [ ] Progress callbacks work
- [ ] Error messages display correctly

**Full Integration Test**:
- [ ] Run complete pipeline (source → dub)
- [ ] Verify all tabs functional
- [ ] Verify config persistence
- [ ] Verify no regressions

### Automated Testing (Future)

Controllers are easier to test than monolithic main.py:
```python
def test_source_controller_start_clicked():
    # Mock widgets
    widgets = {
        'source_input': Mock(get=lambda: 'test.mp4'),
        'log_area': Mock(append=Mock()),
    }
    
    # Create controller
    ctrl = SourceController(widgets, config)
    
    # Test
    ctrl.on_start_clicked()
    
    # Verify
    assert widgets['log_area'].append.called
```

## Expected Outcomes

### Before Extraction
- main.py: ~2800 lines (after Phase 1 cleanup)
- Event handlers: Mixed with UI code
- Testability: Difficult (need full Tkinter app)

### After Extraction
- main.py: ~2000 lines (800 lines moved to controllers)
- src/controllers/: ~800 lines total
  - app_controller.py: ~150 lines
  - source_controller.py: ~250 lines
  - subtitle_controller.py: ~250 lines
  - tts_controller.py: ~150 lines
- Event handlers: Separated from UI
- Testability: Easier (can mock widgets)

### Line Count Breakdown

**Moved to Controllers** (~800 lines):
- Event handler functions: ~600 lines
- Helper methods: ~100 lines
- Callback wrappers: ~100 lines

**Remaining in main.py** (~2000 lines):
- Imports: ~50 lines
- Constants/Presets: ~100 lines
- Helper functions (UI-specific): ~50 lines
- Tab creation (UI layout): ~1500 lines
- Controller wiring: ~200 lines
- Main app class: ~100 lines

## Constraints

### Must NOT Change
- Any functionality
- UI appearance or layout
- Config.json format
- User workflows
- Widget behavior

### Must Preserve
- All event handlers work
- All callbacks work
- Config save/load works
- Progress updates work
- Error handling works

## Success Criteria

- ✅ All event handlers moved to controllers
- ✅ main.py < 2000 lines (from ~2800)
- ✅ Controllers are thin (no business logic)
- ✅ All UI interactions still work
- ✅ No regressions in functionality
- ✅ Config save/load works
- ✅ Progress callbacks work

## References

- `.planning/research/refactoring-patterns.md` - MVC pattern details
- `.planning/codebase/ARCHITECTURE.md` - Current architecture
- `main.py` - Current monolithic implementation
- `src/components/` - Existing component library

## Conclusion

Phase 2 is medium-risk refactoring:
- Moving code, not changing logic
- Clear separation of concerns (MVC)
- Incremental approach (one controller at a time)
- Thorough testing after each step
- Easier to test and maintain after extraction

This phase prepares for Phase 3 (split main.py further) by reducing complexity and establishing clear boundaries.
