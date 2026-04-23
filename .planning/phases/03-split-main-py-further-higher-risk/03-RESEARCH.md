# Phase 3: Split main.py Further (Higher Risk) - Research

**Researched:** 2026-04-23
**Domain:** Python Tkinter GUI refactoring, code organization
**Confidence:** HIGH

## Summary

Phase 3 focuses on further reducing main.py from 2,516 lines to under 1,500 lines by extracting helper functions and reorganizing the monolithic `launch_gui()` function (2,283 lines). After Phase 2, controllers have been extracted using a thin wrapper pattern, but the main.py file still contains 72 nested functions, 160+ local variables, and complex UI creation code all within a single function scope.

The primary challenge is that `launch_gui()` is a massive closure with extensive variable sharing between nested functions. Extracting tab creation or helper functions requires careful handling of variable dependencies to avoid breaking the application.

**Primary recommendation:** Use Option A (safer) - reorganize main.py with clear sections and extract only stateless helper functions to `src/utils/ui_helpers.py`. Avoid creating separate tab files which would require extensive refactoring of closures and state management.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| UI Layout Creation | Frontend (main.py) | — | Tkinter widgets must be created in single scope for event binding |
| Helper Functions (geometry) | Utility Layer | — | Pure functions with no state dependencies can be extracted |
| Event Handling | Controller Layer | — | Already extracted in Phase 2 |
| State Management | Frontend (main.py) | — | Tkinter state variables (use_tk_state) must remain in launch_gui scope |
| Tab Organization | Frontend (main.py) | — | Tab creation deeply coupled with state variables |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.9 | Runtime | Already in use, type hints support |
| tkinter | built-in | GUI framework | Standard library, already used |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| isort | 5.13.2 | Import sorting | Optional - for organizing imports |
| autopep8 | 2.0.4 | Code formatting | Optional - for consistent style |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual reorganization | black formatter | black is opinionated, may conflict with existing style |
| Keep in main.py | Extract to views/ | High risk - breaks closures and state sharing |

**Installation:**
```bash
pip install isort autopep8
```

**Version verification:** Not required - these are optional development tools.

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Imports (55 lines)                                     │ │
│  │  - stdlib, tkinter, third-party, local modules          │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Module-level Constants & Helpers (150 lines)          │ │
│  │  - LOG_DIR, APP_LOG_FILE                               │ │
│  │  - _rotate_app_log_if_needed()                         │ │
│  │  - _write_app_log_line()                               │ │
│  │  - SUBTITLE_PRESETS dict                               │ │
│  │  - _apply_ttk_theme()                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  launch_gui() - Main Application (2,283 lines)         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Setup (100 lines)                                │  │ │
│  │  │  - Create root window                             │  │ │
│  │  │  - Load config                                    │  │ │
│  │  │  - Initialize state variables (30+)              │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Tab Creation (1,800 lines)                       │  │ │
│  │  │  - Source tab (500 lines)                         │  │ │
│  │  │  - Adjust tab (800 lines)                         │  │ │
│  │  │  - Dub tab (300 lines)                            │  │ │
│  │  │  - Log tab (200 lines)                            │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Nested Helper Functions (72 functions)           │  │ │
│  │  │  - _sync_adjust_scroll()                          │  │ │
│  │  │  - _wheel_adjust()                                │  │ │
│  │  │  - paste_clipboard()                              │  │ │
│  │  │  - browse_file()                                  │  │ │
│  │  │  - load_source_preview()                          │  │ │
│  │  │  - update_preview()                               │  │ │
│  │  │  - ... (66 more)                                  │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Event Wiring (200 lines)                         │  │ │
│  │  │  - Button commands                                │  │ │
│  │  │  - State traces                                   │  │ │
│  │  │  - Canvas bindings                                │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Controller Initialization (100 lines)            │  │ │
│  │  │  - Create controllers                             │  │ │
│  │  │  - Wire to UI                                     │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  root.mainloop()                                  │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Entry Point (2 lines)                                 │ │
│  │  if __name__ == "__main__": launch_gui()              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Extractable to src/utils/ui_helpers.py:
┌────────────────────────────────────┐
│  _expand_band_from_center()        │  Pure function - no state deps
│  _shift_band()                     │  Pure function - no state deps
└────────────────────────────────────┘
```

### Recommended Project Structure

Current structure is already good:
```
src/
├── controllers/        # Event handlers (Phase 2 complete)
├── components/         # Reusable UI widgets
├── modules/            # Business logic
└── utils/              # Helper functions
    ├── file_utils.py
    ├── logger.py
    ├── runtime_env.py
    ├── suppress_warnings.py
    ├── text_utils.py
    └── ui_helpers.py   # NEW - extract geometry helpers
```

**Do NOT create** `src/views/` - unnecessary complexity for this codebase.

### Pattern 1: Extract Pure Helper Functions

**What:** Move stateless helper functions from main.py to `src/utils/ui_helpers.py`

**When to use:** Function has no dependencies on closure variables (state, widgets, callbacks)

**Example:**
```python
# src/utils/ui_helpers.py
def expand_band_from_center(
    top_y: int | None, 
    bottom_y: int | None, 
    frame_height: int, 
    padding_px: int
) -> tuple[int | None, int | None]:
    """Expand subtitle band from center by padding.
    
    Pure function - no state dependencies.
    """
    if top_y is None or bottom_y is None or frame_height <= 0:
        return None, None
    center_y = (int(top_y) + int(bottom_y)) / 2.0
    base_height = max(2, int(bottom_y) - int(top_y) + 1)
    half_height = base_height / 2.0 + max(0, int(padding_px or 0))
    new_top = max(0, int(round(center_y - half_height)))
    new_bottom = min(frame_height - 1, int(round(center_y + half_height)))
    if new_bottom <= new_top:
        new_bottom = min(frame_height - 1, new_top + 1)
    return new_top, new_bottom

# main.py - import and use
from src.utils.ui_helpers import expand_band_from_center, shift_band
```

### Pattern 2: Reorganize launch_gui() with Clear Sections

**What:** Add section comments and group related code

**When to use:** When code is too large but cannot be extracted due to closure dependencies

**Example:**
```python
def launch_gui():
    """Launch main GUI application."""
    # ═══════════════════════════════════════════════════════════
    # SECTION 1: Window Setup
    # ═══════════════════════════════════════════════════════════
    root = tk.Tk()
    root.title("Dubbing Extractor v2.5")
    root.geometry("1120x800")
    # ... window setup code ...
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 2: State Management
    # ═══════════════════════════════════════════════════════════
    app_config = load_app_config()
    source_state = use_tk_state("string", app_config.get("source_input", ""))
    # ... 30+ state variables ...
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 3: Helper Functions (Closures)
    # ═══════════════════════════════════════════════════════════
    def paste_clipboard():
        # ... uses source_state ...
    
    def browse_file():
        # ... uses source_state ...
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 4: Tab Creation - Source Tab
    # ═══════════════════════════════════════════════════════════
    source_tab = tk.Frame(notebook, padx=16, pady=16, bg=T.BG_WHITE)
    # ... source tab widgets ...
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 5: Tab Creation - Adjust Tab
    # ═══════════════════════════════════════════════════════════
    adjust_tab = tk.Frame(notebook, padx=16, pady=16, bg=T.BG_WHITE)
    # ... adjust tab widgets ...
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 6: Event Wiring
    # ═══════════════════════════════════════════════════════════
    start_btn.config(command=source_ctrl.on_start_clicked)
    # ... all event bindings ...
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 7: Controller Initialization
    # ═══════════════════════════════════════════════════════════
    source_ctrl = SourceController(...)
    # ... controller setup ...
    
    root.mainloop()
```

### Pattern 3: Organize Imports by Category

**What:** Group imports into stdlib, third-party, and local sections

**When to use:** Always - improves readability

**Example:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dubbing Extractor v2 - Main Entry Point."""

# ── Standard Library ──────────────────────────────────────────
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# ── Third-Party ───────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk
import winsound

# ── Local Modules ─────────────────────────────────────────────
from src.config import config, load_app_config, save_app_config
from src.modules.workflow import process_video
from src.components.ui import Button, Input, Label
from src.controllers import SourceController
from src.utils.ui_helpers import expand_band_from_center
```

### Anti-Patterns to Avoid

- **Extracting tab creation to separate files:** Breaks closure dependencies, requires passing 30+ state variables as parameters
- **Creating a views/ directory:** Unnecessary abstraction for a single-window application
- **Splitting launch_gui() into multiple functions:** Requires extensive parameter passing or global state
- **Using global variables:** Makes testing harder, violates encapsulation

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Import sorting | Manual organization | isort (optional) | Handles edge cases, consistent style |
| Code formatting | Manual spacing | autopep8 (optional) | PEP 8 compliance, saves time |
| Function extraction | Manual copy-paste | IDE refactoring tools | Handles references automatically |

**Key insight:** For Tkinter applications with extensive closure-based state management, aggressive extraction often creates more problems than it solves. Focus on organization over extraction.

## Runtime State Inventory

> Phase 3 is code reorganization only - no runtime state changes.

Not applicable - this phase does not rename, refactor, or migrate any runtime state.

## Common Pitfalls

### Pitfall 1: Breaking Closure Dependencies

**What goes wrong:** Extracting nested functions that reference closure variables causes NameError or requires passing many parameters

**Why it happens:** launch_gui() has 72 nested functions sharing 160+ local variables through closure scope

**How to avoid:** Only extract pure functions with no closure dependencies. Keep closure-dependent functions in launch_gui()

**Warning signs:** Function references variables not in its parameter list

**Example:**
```python
# BAD - This function references closure variables
def paste_clipboard():
    text = root.clipboard_get()  # Uses 'root' from closure
    source_state.set(text)       # Uses 'source_state' from closure
    load_source_preview(force=True)  # Calls closure function

# Extracting this requires passing root, source_state, and load_source_preview
# Result: More complex than keeping it nested

# GOOD - Pure function, safe to extract
def _expand_band_from_center(top_y, bottom_y, frame_height, padding_px):
    # No closure dependencies - only uses parameters
    if top_y is None or bottom_y is None:
        return None, None
    # ... pure calculation ...
    return new_top, new_bottom
```

### Pitfall 2: Over-Engineering with Views Layer

**What goes wrong:** Creating `src/views/tabs/` structure adds complexity without benefit

**Why it happens:** Applying MVC pattern too rigidly to a single-window Tkinter app

**How to avoid:** Recognize that Tkinter's widget tree IS the view layer. Don't create redundant abstractions.

**Warning signs:** Passing 10+ parameters to tab creation functions, creating "view classes" that just wrap widget creation

### Pitfall 3: Breaking Event Bindings

**What goes wrong:** Moving widget creation code breaks event bindings that reference those widgets

**Why it happens:** Event bindings are set up after widget creation, often hundreds of lines later

**How to avoid:** Keep widget creation and event binding in the same scope. Use clear section markers to show relationships.

**Warning signs:** AttributeError when accessing widgets, events not firing

### Pitfall 4: Import Circular Dependencies

**What goes wrong:** Extracting code to new modules creates circular imports

**Why it happens:** main.py imports from modules that now need to import from extracted code

**How to avoid:** Only extract to utility modules that don't import from main.py. Never create bidirectional dependencies.

**Warning signs:** ImportError: cannot import name 'X' from partially initialized module

## Code Examples

### Example 1: Extract Pure Helper Function

```python
# Before - in main.py
def _expand_band_from_center(top_y: int | None, bottom_y: int | None, 
                             frame_height: int, padding_px: int) -> tuple[int | None, int | None]:
    if top_y is None or bottom_y is None or frame_height <= 0:
        return None, None
    center_y = (int(top_y) + int(bottom_y)) / 2.0
    base_height = max(2, int(bottom_y) - int(top_y) + 1)
    half_height = base_height / 2.0 + max(0, int(padding_px or 0))
    new_top = max(0, int(round(center_y - half_height)))
    new_bottom = min(frame_height - 1, int(round(center_y + half_height)))
    if new_bottom <= new_top:
        new_bottom = min(frame_height - 1, new_top + 1)
    return new_top, new_bottom

# After - extracted to src/utils/ui_helpers.py
# main.py
from src.utils.ui_helpers import expand_band_from_center

# In launch_gui():
new_top, new_bottom = expand_band_from_center(top_y, bottom_y, height, padding)
```

### Example 2: Organize Imports

```python
# Before - mixed order
import os
from src.config import config
import tkinter as tk
import sys
from src.modules.workflow import process_video
from pathlib import Path
import json

# After - organized by category
# ── Standard Library ──────────────────────────────────────────
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Third-Party ───────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk

# ── Local Modules ─────────────────────────────────────────────
from src.config import config, load_app_config
from src.modules.workflow import process_video
```

### Example 3: Add Section Markers

```python
def launch_gui():
    """Launch main GUI application."""
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 1: Window Setup
    # ═══════════════════════════════════════════════════════════
    root = tk.Tk()
    root.title("Dubbing Extractor v2.5")
    root.geometry("1120x800")
    root.minsize(1000, 720)
    
    style = ttk.Style()
    _apply_ttk_theme(style)
    root.configure(bg=T.BG_LIGHT)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 2: Configuration & State Management
    # ═══════════════════════════════════════════════════════════
    app_config = load_app_config()
    
    # Legacy preset migration
    legacy_presets = {...}
    if app_config.get("subtitle_preset") in legacy_presets:
        app_config["subtitle_preset"] = legacy_presets[app_config["subtitle_preset"]]
    
    # State variables (30+ variables)
    source_state = use_tk_state("string", app_config.get("source_input", ""))
    cover_mode_state = use_tk_state("string", app_config.get("cover_mode", "blur"))
    # ... more state ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single monolithic file | MVC with controllers | 2020s | Better separation of concerns |
| Global variables | Closure-based state | Modern Python | Encapsulation without classes |
| Manual import sorting | isort tool | 2015+ | Consistent style |
| Nested functions everywhere | Extract pure functions | Always | Testability, reusability |

**Deprecated/outdated:**
- Creating separate view classes for each tab in Tkinter - modern approach uses functional composition with closures
- Using global variables for state - use closure scope or class attributes instead

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | launch_gui() has 72 nested functions | Summary | Count may be slightly off, but order of magnitude correct |
| A2 | Extracting tab creation breaks closures | Architecture Patterns | If wrong, could extract more aggressively |
| A3 | isort and autopep8 are optional | Standard Stack | If required, need to add to requirements.txt |

## Open Questions

1. **Should we create src/utils/ui_helpers.py or keep helpers in main.py?**
   - What we know: Only 2 functions (_expand_band_from_center, _shift_band) are pure
   - What's unclear: Is creating a new file worth it for 2 functions?
   - Recommendation: Create the file - establishes pattern for future extractions

2. **Should we use isort to organize imports?**
   - What we know: isort not currently installed, imports are somewhat organized
   - What's unclear: Does user want to add dev dependencies?
   - Recommendation: Manual organization is sufficient, mention isort as optional

3. **How aggressively should we add section markers?**
   - What we know: File has some section markers (# ── style)
   - What's unclear: User preference for marker style
   - Recommendation: Use existing style (# ── with box drawing chars) for consistency

## Environment Availability

> Phase 3 has no external dependencies beyond Python and existing packages.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Code execution | ✓ | 3.11.9 | — |
| isort | Import sorting | ✗ | — | Manual organization |
| autopep8 | Code formatting | ✗ | — | Manual formatting |

**Missing dependencies with no fallback:**
- None - all work can be done manually

**Missing dependencies with fallback:**
- isort - use manual import organization
- autopep8 - use manual formatting

## Validation Architecture

> Validation is not explicitly configured. Assuming enabled per default.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual testing (no automated test framework) |
| Config file | none |
| Quick run command | Manual UI testing |
| Full suite command | Full pipeline test with sample video |

### Phase Requirements → Test Map

Phase 3 has no explicit requirement IDs provided. Testing focuses on ensuring no functionality breaks.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REF-01 | All UI elements render correctly | manual | Visual inspection | N/A |
| REF-02 | All buttons and inputs work | manual | Click through all tabs | N/A |
| REF-03 | Full pipeline processes video | manual | Run complete workflow | N/A |
| REF-04 | Config save/load works | manual | Save config, restart, verify loaded | N/A |

### Sampling Rate
- **Per task commit:** Visual inspection of UI (< 1 minute)
- **Per wave merge:** Full tab navigation test (< 2 minutes)
- **Phase gate:** Complete pipeline test with sample video (5-10 minutes)

### Wave 0 Gaps
- No automated tests exist for GUI
- Manual testing is the only validation method
- Consider adding smoke tests in future phases (out of scope for Phase 3)

## Security Domain

> Security enforcement not explicitly configured. Assuming enabled per default.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A - desktop app, no auth |
| V3 Session Management | no | N/A - desktop app, no sessions |
| V4 Access Control | no | N/A - desktop app, single user |
| V5 Input Validation | yes | Existing validation in workflow.py |
| V6 Cryptography | no | N/A - no crypto operations |

### Known Threat Patterns for Tkinter Desktop Apps

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal in file selection | Tampering | Use tkinter.filedialog (already used) |
| Command injection in subprocess | Tampering | Use subprocess with list args (already used) |
| Arbitrary code execution via config | Tampering | Use json.load, not eval (already used) |

**Phase 3 Impact:** Code reorganization does not change security posture. All existing mitigations remain in place.

## Sources

### Primary (HIGH confidence)
- Direct codebase analysis: C:/Users/xhiep/Downloads/dubbing-extractor/main.py (2,516 lines verified)
- Phase 2 research: .planning/phases/02-extract-controllers-medium-risk/02-RESEARCH.md
- Project requirements: .planning/REQUIREMENTS.md
- Project state: .planning/STATE.md

### Secondary (MEDIUM confidence)
- Python documentation: tkinter module (built-in, well-documented)
- PEP 8 style guide: import organization conventions

### Tertiary (LOW confidence)
- None - all findings verified against actual codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - verified against existing codebase and Python version
- Architecture: HIGH - analyzed actual code structure, counted functions and lines
- Pitfalls: HIGH - based on common Tkinter refactoring issues and closure analysis

**Research date:** 2026-04-23
**Valid until:** 2026-05-23 (30 days - stable domain, Python/Tkinter patterns don't change rapidly)
