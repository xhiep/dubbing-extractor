---
task: Extract helper functions from main.py
date: 2026-04-24
status: planning
target_lines: 1000-1200
---

# Quick Task: Extract Helper Functions from main.py

## Current State
- main.py: ~2,060 lines
- After Phase 5: Views extracted, but still contains many helper functions

## Goal
Reduce main.py to ~1,000-1,200 lines by extracting:
1. Pipeline helper functions (step execution, status updates)
2. SRT editor functions (open, reload, save)
3. Preview functions (load, update, render)
4. UI helper functions (callbacks, event handlers)
5. Application logic functions

## Target Structure
```
main.py (~1,000-1,200 lines)
├── Window setup
├── State initialization
├── View assembly (4 views)
└── Controller wiring

src/helpers/
├── pipeline_helpers.py - Step execution, status updates
├── srt_helpers.py - SRT editor operations
├── preview_helpers.py - Preview loading and rendering
└── ui_callbacks.py - UI event callbacks
```

## Discussion Points

### 1. What functions should be extracted?
**Pipeline helpers (~200 lines):**
- `_set_pipeline_status()`
- `_update_step_buttons()`
- `_mark_step_error()`
- `run_up_to_step()`
- `reset_pipeline()`

**SRT helpers (~100 lines):**
- `_enable_srt_editor()`
- `_disable_srt_editor()`
- `open_srt_external()`
- `reload_srt_from_file()`
- `save_srt_to_file()`

**Preview helpers (~300 lines):**
- `load_source_preview()`
- `update_preview()`
- `render_preview_frame()`
- `_draw_subtitle_band()`
- `_on_preview_drag_start()`
- `_on_preview_drag_motion()`
- `_on_preview_drag_release()`

**UI callbacks (~150 lines):**
- `paste_clipboard()`
- `browse_file()`
- `browse_ref_audio()`
- `open_render_folder()`
- Various preset and state change handlers

### 2. How to handle state dependencies?
Many functions depend on:
- `pipeline_state` dict
- `preview_guard` dict
- Widget references (buttons, labels, canvas)
- Tkinter root window

**Options:**
A. Pass all dependencies as parameters (pure functions)
B. Create helper classes that hold state
C. Use a context object that bundles state + widgets

**Recommendation:** Option A (pure functions) for simplicity and testability

### 3. How to organize the extracted code?
**Option A: By feature domain**
- `src/helpers/pipeline_helpers.py`
- `src/helpers/srt_helpers.py`
- `src/helpers/preview_helpers.py`
- `src/helpers/ui_callbacks.py`

**Option B: By layer**
- `src/helpers/state_helpers.py` (all state manipulation)
- `src/helpers/ui_helpers.py` (all UI updates)
- `src/helpers/business_logic.py` (all business logic)

**Recommendation:** Option A (by feature domain) - easier to navigate

### 4. What stays in main.py?
- Window setup and configuration
- State dict initialization
- View instantiation and assembly
- Controller instantiation and wiring
- Main event loop
- Top-level function definitions that call helpers

### 5. Testing strategy?
- Extract functions as pure functions (no side effects where possible)
- Add unit tests for extracted helpers
- Verify app still runs after each extraction
- Test all UI interactions manually

## Risks
1. **Breaking callbacks:** Functions are referenced in callbacks, need to update imports
2. **Circular dependencies:** Helpers might reference each other
3. **State management:** Need to pass state dicts correctly
4. **Testing overhead:** More files = more testing needed

## Mitigation
1. Extract in small batches, test after each
2. Use clear naming conventions for helper modules
3. Document all function signatures with type hints
4. Keep git commits atomic (one feature domain per commit)

## Execution Plan (Draft)

### Wave 1: SRT Helpers (Low Risk)
- Extract 6 SRT functions to `src/helpers/srt_helpers.py`
- Update imports in main.py
- Test SRT editor functionality

### Wave 2: Pipeline Helpers (Medium Risk)
- Extract 5 pipeline functions to `src/helpers/pipeline_helpers.py`
- Update step button callbacks
- Test step-by-step mode

### Wave 3: UI Callbacks (Medium Risk)
- Extract 8 callback functions to `src/helpers/ui_callbacks.py`
- Update view callback dictionaries
- Test all buttons and inputs

### Wave 4: Preview Helpers (High Risk)
- Extract 7 preview functions to `src/helpers/preview_helpers.py`
- Handle canvas and image state carefully
- Test preview loading and rendering

### Wave 5: Integration & Cleanup
- Remove any remaining duplicates
- Add docstrings to all helpers
- Update CLAUDE.md with new structure
- Final testing

## Success Criteria
- ✅ main.py reduced to ~1,000-1,200 lines
- ✅ All functionality preserved
- ✅ App runs without errors
- ✅ All tests pass
- ✅ Code is more maintainable and modular
