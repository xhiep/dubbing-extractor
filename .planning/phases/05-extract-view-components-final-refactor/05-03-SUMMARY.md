---
phase: 05-extract-view-components-final-refactor
plan: 03
status: complete
completed_at: 2026-04-24T04:33:58Z
---

# Plan 05-03 Summary: Extract Source Tab to SourceView

## Objective
Extract the Source tab (video input and processing controls) to SourceView class, reducing main.py by ~154 lines.

## Changes Made

### Files Created
- **src/views/source_view.py** (262 lines)
  - Created SourceView class following DubView pattern
  - Handles video source input UI (YouTube, Bilibili, Douyin, local files)
  - Implements step-by-step processing UI (5 step buttons)
  - Includes SRT editor section with controls (open, reload, save)
  - Stores widget references for controller access
  - Returns configured tk.Frame from build() method

### Files Modified
- **src/views/__init__.py**
  - Added SourceView to exports
  - Updated __all__ list to include SourceView

- **main.py** (reduced from 2409 to 2254 lines, -155 lines)
  - Updated import: `from src.views import LogView, DubView, SourceView`
  - Removed source_tab frame creation from SECTION 3
  - Replaced SECTION 4 UI code (lines 376-577) with SourceView instantiation
  - Kept all pipeline helper functions in main.py (business logic)
  - Added notebook.insert() call after source_tab is built
  - Extracted widget references from source_widgets dict for use in helper functions

## Implementation Details

### SourceView Structure
```python
class SourceView:
    def __init__(self, parent, state, callbacks)
    def build(self) -> tk.Frame
    def get_widgets(self) -> Dict[str, Any]
```

### State Variables Passed
- source_state: StringVar for video source input
- whisper_model_state: StringVar for Whisper model selection
- pipeline_state: Dict for step-by-step processing state
- preview_guard: Dict for preview state management

### Callbacks Passed
- paste_clipboard: Paste from clipboard
- browse_file: Open file dialog
- load_source_preview: Load video preview
- log: Log messages

### Widget References Stored
- source_input: Input widget for video source
- step_btn_widgets: List of 5 step buttons
- pipeline_status_var: StringVar for status text
- pipeline_status_label: Label widget for status display
- reset_pipeline_btn: Reset button
- open_srt_btn: Open SRT file externally
- reload_srt_btn: Reload SRT from file
- save_srt_btn: Save SRT changes
- srt_file_label_var: StringVar for SRT filename
- srt_editor: Text widget for SRT editing
- STEP_COLOR_* constants: Color codes for button states

### Business Logic Kept in main.py
All pipeline helper functions remain in main.py:
- _set_pipeline_status()
- _update_step_buttons()
- _mark_step_error()
- _enable_srt_editor()
- _disable_srt_editor()
- open_srt_external()
- reload_srt_from_file()
- save_srt_to_file()
- reset_pipeline()
- _collect_params()
- run_up_to_step()

These functions reference many state variables and other functions not passed to SourceView, so they must remain in main.py.

## Verification Results

### Syntax Checks
✓ `python -m py_compile src/views/source_view.py` - PASSED
✓ `python -m py_compile main.py` - PASSED
✓ `from src.views import SourceView` - PASSED

### Line Count Reduction
- Before: 2409 lines
- After: 2254 lines
- Reduction: 155 lines (~6.4%)

### File Sizes
- src/views/source_view.py: 262 lines
- Net reduction in main.py: 155 lines (some lines added for SourceView instantiation)

## Acceptance Criteria Status

✓ File src/views/source_view.py exists with SourceView class
✓ SourceView.__init__ has type hints for parent, state, callbacks
✓ SourceView.build() returns tk.Frame
✓ SourceView.build() creates video source input card
✓ SourceView.build() creates step-by-step processing card with 5 buttons
✓ SourceView.build() creates SRT editor section
✓ SourceView.get_widgets() returns dictionary of widget references
✓ src/views/__init__.py exports SourceView
✓ main.py imports SourceView
✓ main.py SECTION 4 uses SourceView instead of inline code
✓ main.py line count reduced by ~155 lines
✓ All source controls accessible via source_widgets dict
✓ Step-by-step buttons accessible to pipeline functions

## Notes

### Design Decision: Business Logic Placement
The pipeline helper functions (_set_pipeline_status, run_up_to_step, etc.) remain in main.py because they:
1. Reference many state variables not passed to SourceView (cover_mode_state, burn_sub_state, dub settings, etc.)
2. Call workflow step functions (step1_prepare, step2_transcribe, etc.)
3. Interact with other tabs (notebook.select(adjust_tab), notebook.select(dub_tab))
4. Access global functions (save_app_config, load_preview_segments)

This separation maintains clean boundaries: SourceView handles pure UI rendering, main.py handles business logic and orchestration.

### Tab Order
Used `notebook.insert(0, source_tab, ...)` to ensure Source tab appears first in the notebook, maintaining the original tab order.

## Next Steps
- Plan 05-04: Extract Adjust tab to AdjustView (most complex tab with preview canvas)
- Manual testing: Launch app and verify Source tab renders correctly
- Test step-by-step processing workflow
- Test SRT editor functionality

## Risk Assessment
- Low risk: Pure UI extraction following established DubView pattern
- All business logic remains in main.py
- Widget references properly exposed via get_widgets()
- No changes to functionality, only code organization
