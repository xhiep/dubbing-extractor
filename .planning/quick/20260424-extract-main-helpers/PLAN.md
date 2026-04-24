---
task: Extract helper functions from main.py
slug: extract-main-helpers
date: 2026-04-24
status: ready
estimated_lines_reduction: 800-900
target_main_lines: 1000-1200
---

# Plan: Extract Helper Functions from main.py

## Goal
Reduce main.py from ~2,060 lines to ~1,000-1,200 lines by extracting helper functions into organized modules.

## Strategy
Extract functions in 4 waves by feature domain, using pure functions with explicit parameters.

---

## Wave 1: SRT Helpers (~100 lines)

**File:** `src/helpers/srt_helpers.py`

**Functions to extract:**
1. `_enable_srt_editor(srt_path, srt_editor, open_btn, reload_btn, save_btn, label_var)`
2. `_disable_srt_editor(srt_editor, open_btn, reload_btn, save_btn, label_var)`
3. `open_srt_external(pipeline_state, status_callback)`
4. `reload_srt_from_file(pipeline_state, srt_editor, status_callback)`
5. `save_srt_to_file(pipeline_state, srt_editor, status_callback)`

**Changes in main.py:**
- Import: `from src.helpers.srt_helpers import *`
- Update function calls to use imported versions
- Remove original definitions

**Testing:**
- Open SRT in external editor
- Reload SRT content
- Save SRT changes
- Verify all buttons work

---

## Wave 2: Pipeline Helpers (~200 lines)

**File:** `src/helpers/pipeline_helpers.py`

**Functions to extract:**
1. `set_pipeline_status(msg, color, status_var, status_label)`
2. `update_step_buttons(pipeline_state, step_btn_widgets, colors, running_step=-1)`
3. `mark_step_error(step_num, step_btn_widgets, error_color)`
4. `reset_pipeline(pipeline_state, srt_editor, buttons, labels, status_callback)`
5. `run_up_to_step(step_num, pipeline_state, source_state, config, widgets, callbacks)`

**Changes in main.py:**
- Import: `from src.helpers.pipeline_helpers import *`
- Update all `_set_pipeline_status()` calls
- Update step button command bindings
- Remove original definitions

**Testing:**
- Run each step individually
- Reset pipeline
- Verify status updates
- Check step button colors

---

## Wave 3: UI Callbacks (~150 lines)

**File:** `src/helpers/ui_callbacks.py`

**Functions to extract:**
1. `paste_clipboard(root, source_state, preview_callback)`
2. `browse_file(source_state, preview_callback)`
3. `browse_ref_audio(ref_audio_state)`
4. `open_render_folder(last_output_var, status_var)`
5. `mark_preset_custom(preset_guard, preset_state)`
6. `apply_selected_preset(preset_state, preset_guard, presets, state_vars, update_callback)`

**Changes in main.py:**
- Import: `from src.helpers.ui_callbacks import *`
- Update callback dictionaries in view instantiation
- Remove original definitions

**Testing:**
- Paste clipboard
- Browse file
- Browse reference audio
- Open render folder
- Apply presets

---

## Wave 4: Preview Helpers (~300 lines)

**File:** `src/helpers/preview_helpers.py`

**Functions to extract:**
1. `load_source_preview(source, preview_guard, widgets, callbacks, force=False)`
2. `update_preview(preview_guard, state_vars, widgets, callbacks)`
3. `render_preview_frame(preview_guard, canvas, info_var, status_var)`
4. `draw_subtitle_band(canvas, band, color, tag)`
5. `on_preview_drag_start(event, preview_guard, canvas)`
6. `on_preview_drag_motion(event, preview_guard, canvas, callbacks)`
7. `on_preview_drag_release(event, preview_guard, callbacks)`

**Changes in main.py:**
- Import: `from src.helpers.preview_helpers import *`
- Update preview-related callbacks
- Update canvas event bindings
- Remove original definitions

**Testing:**
- Load video preview
- Drag subtitle bands
- Update preview parameters
- Verify canvas rendering

---

## Wave 5: Integration & Cleanup

**Tasks:**
1. Remove any duplicate function definitions
2. Add comprehensive docstrings to all helpers
3. Add type hints to all function signatures
4. Update CLAUDE.md with new structure
5. Run full test suite
6. Manual testing of all features

**Files to update:**
- `CLAUDE.md` - Document new helper modules
- `CHANGELOG.md` - Add entry for this refactoring
- `.planning/quick/20260424-extract-main-helpers/SUMMARY.md` - Final report

---

## Dependencies

**Each helper module needs:**
- Type hints: `from typing import Dict, Any, Callable, Optional`
- Tkinter: `import tkinter as tk`
- Path: `from pathlib import Path`
- Logging: `from src.utils.logger import logger`

**main.py imports after extraction:**
```python
from src.helpers.srt_helpers import (
    enable_srt_editor, disable_srt_editor,
    open_srt_external, reload_srt_from_file, save_srt_to_file
)
from src.helpers.pipeline_helpers import (
    set_pipeline_status, update_step_buttons, mark_step_error,
    reset_pipeline, run_up_to_step
)
from src.helpers.ui_callbacks import (
    paste_clipboard, browse_file, browse_ref_audio,
    open_render_folder, mark_preset_custom, apply_selected_preset
)
from src.helpers.preview_helpers import (
    load_source_preview, update_preview, render_preview_frame,
    draw_subtitle_band, on_preview_drag_start,
    on_preview_drag_motion, on_preview_drag_release
)
```

---

## Commit Strategy

Each wave gets one atomic commit:
1. `refactor: Extract SRT helper functions to src/helpers/srt_helpers.py`
2. `refactor: Extract pipeline helper functions to src/helpers/pipeline_helpers.py`
3. `refactor: Extract UI callback functions to src/helpers/ui_callbacks.py`
4. `refactor: Extract preview helper functions to src/helpers/preview_helpers.py`
5. `docs: Update documentation for helper modules extraction`

---

## Success Metrics

- ✅ main.py: 2,060 → ~1,100 lines (46% reduction)
- ✅ 4 new helper modules created (~750 lines total)
- ✅ All functionality preserved
- ✅ App runs without errors
- ✅ All manual tests pass
- ✅ Code is more maintainable

---

## Risks & Mitigation

**Risk 1:** Breaking callback references
- **Mitigation:** Test after each wave, use search/replace carefully

**Risk 2:** State management complexity
- **Mitigation:** Pass state dicts explicitly, document parameters

**Risk 3:** Circular dependencies
- **Mitigation:** Keep helpers independent, avoid cross-imports

**Risk 4:** Testing overhead
- **Mitigation:** Focus on integration testing, manual verification

---

## Execution Order

1. Wave 1: SRT Helpers (30 min)
2. Wave 2: Pipeline Helpers (45 min)
3. Wave 3: UI Callbacks (40 min)
4. Wave 4: Preview Helpers (60 min)
5. Wave 5: Integration (30 min)

**Total estimated time:** ~3.5 hours
