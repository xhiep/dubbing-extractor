# Phase 5: Extract View Components (Final Refactor) - Research

**Researched:** 2026-04-24
**Domain:** Tkinter GUI refactoring, view extraction, MVC separation
**Confidence:** HIGH

## Summary

Phase 5 completes the refactoring journey by extracting the four tab UI definitions from main.py into separate view files. This is the final major structural change, reducing main.py from ~2,527 lines to approximately 400-500 lines. The phase builds on the existing controller pattern (Phase 2) and component architecture (existing src/components/).

The codebase already has excellent foundations: custom UI components (Button, Input, Card, etc.), thin wrapper controllers, and clear section markers in main.py. The extraction follows a proven pattern: each view class creates and returns a configured tk.Frame, controllers wire up events, and main.py becomes a simple assembly point.

The main challenge is managing shared state (preview_guard, voice_guard, preset_guard dictionaries) and closures that reference variables in launch_gui() scope. The solution is to pass state and callbacks as constructor parameters, keeping views pure (no business logic) and testable.

**Primary recommendation:** Extract views one tab at a time (Source → Adjust → Dub → Log), test after each extraction, use constructor injection for state/callbacks to avoid breaking closures.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| UI layout definition | View Layer | — | Views own widget creation and layout geometry |
| Event wiring | Controller Layer | — | Controllers connect UI events to business logic |
| State management | Application Logic | View Layer | State lives in main.py, views receive via constructor |
| Widget styling | View Layer | Theme Module | Views apply theme constants, theme defines colors/fonts |
| Business logic | Module Layer | — | Views never contain business logic, only UI structure |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| tkinter (stdlib) | 8.6 | GUI framework | Built-in, cross-platform, project already uses it |
| ttk (stdlib) | 8.6 | Themed widgets | Built-in, provides Notebook and styled widgets |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing (stdlib) | 3.11+ | Type hints for view constructors | Already used in Phase 4 |
| pathlib (stdlib) | 3.11+ | Path handling in views | Already used throughout project |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Class-based views | Function-based views | Classes provide better encapsulation and state management |
| Constructor injection | Global state | Constructor injection is more testable and explicit |
| Frame return pattern | Direct parent modification | Returning frames makes composition clearer |

**Installation:**
```bash
# No new dependencies - all stdlib
```

**Version verification:** [VERIFIED: Python 3.11.9 installed, tkinter 8.6]

## Architecture Patterns

### System Architecture Diagram

```
main.py (launch_gui)
    ↓
[Window Setup] → root = tk.Tk()
    ↓
[State Management] → use_tk_state() for all config
    ↓
[Notebook Creation] → ttk.Notebook(main_frame)
    ↓
    ├─→ SourceView(notebook, state, callbacks).build()
    │       ↓
    │   [Source Tab Frame] ← Card components, Input widgets
    │       ↓
    │   SourceController(callbacks) ← wires events
    │
    ├─→ AdjustView(notebook, state, callbacks).build()
    │       ↓
    │   [Adjust Tab Frame] ← Settings, Preview canvas
    │       ↓
    │   SubtitleController(callbacks) ← wires events
    │
    ├─→ DubView(notebook, state, callbacks).build()
    │       ↓
    │   [Dub Tab Frame] ← TTS config, voice selection
    │       ↓
    │   TtsController(callbacks) ← wires events
    │
    └─→ LogView(notebook, state).build()
            ↓
        [Log Tab Frame] ← TextArea, status display
            ↓
        (No controller - display only)
    ↓
[Controller Creation] → Wire up all event handlers
    ↓
root.mainloop()
```

### Recommended Project Structure
```
src/
├── views/
│   ├── __init__.py
│   ├── source_view.py      # ~200 lines - Source tab UI
│   ├── adjust_view.py      # ~400 lines - Adjust tab UI (largest)
│   ├── dub_view.py         # ~250 lines - Dub tab UI
│   └── log_view.py         # ~50 lines - Log tab UI (simplest)
├── controllers/            # Already exists from Phase 2
├── components/             # Already exists - reused by views
└── modules/                # Already exists - business logic
```

### Pattern 1: View Class with Constructor Injection
**What:** Each view is a class that receives state and callbacks via constructor, builds UI in build() method
**When to use:** All tab views

**Example:**
```python
# src/views/source_view.py
import tkinter as tk
from typing import Callable, Dict, Any
from ..components.ui import Button, Input, Label
from ..components.layout import Card
from ..components.theme import T

class SourceView:
    """Source tab view - video input and processing controls."""
    
    def __init__(self,
                 parent: tk.Widget,
                 state: Dict[str, Any],
                 callbacks: Dict[str, Callable]):
        """Initialize source view.
        
        Args:
            parent: Parent widget (notebook)
            state: Dictionary of tk state variables
                - source_state: StringVar for video source input
                - pipeline_state: Dict for step-by-step state
            callbacks: Dictionary of callback functions
                - paste_clipboard: Function to paste from clipboard
                - browse_file: Function to open file dialog
                - load_source_preview: Function to load video preview
        """
        self.parent = parent
        self.state = state
        self.callbacks = callbacks
        
    def build(self) -> tk.Frame:
        """Build and return the source tab frame.
        
        Returns:
            Configured tk.Frame ready to add to notebook
        """
        # Create tab frame
        frame = tk.Frame(self.parent, padx=16, pady=16, bg=T.BG_WHITE)
        
        # Video source card
        source_card = Card(frame, title="📹 Nguồn Video")
        container = source_card.get_container()
        
        # Source input
        source_input = Input(container, 
                           placeholder="Dán link video...",
                           width=70)
        source_input.var = self.state['source_state'].var
        source_input.pack(fill=tk.X, pady=5)
        
        # Bind events
        source_input.widget.bind("<Return>", 
            lambda e: self.callbacks['load_source_preview'](force=True))
        
        # Buttons
        Button(container, text="Dan Link",
               command=self.callbacks['paste_clipboard'],
               bg=T.ACCENT, fg=T.BG_WHITE).pack()
        
        source_card.pack(fill=tk.X, pady=5)
        
        # Step-by-step card (if needed)
        # ... more UI construction ...
        
        return frame
```

### Pattern 2: State Dictionary Injection
**What:** Pass state variables as dictionary to avoid tight coupling
**When to use:** When view needs access to multiple tk.StringVar/IntVar/etc.

**Example:**
```python
# In main.py
state_dict = {
    'source_state': source_state,
    'cover_mode_state': cover_mode_state,
    'whisper_model_state': whisper_model_state,
    # ... all state variables
}

# Pass to view
source_view = SourceView(notebook, state_dict, callbacks)
source_frame = source_view.build()
```

### Pattern 3: Callback Dictionary Injection
**What:** Pass callback functions as dictionary to decouple view from implementation
**When to use:** When view needs to trigger actions defined in main.py scope

**Example:**
```python
# In main.py
callbacks = {
    'paste_clipboard': paste_clipboard,
    'browse_file': browse_file,
    'load_source_preview': load_source_preview,
    'log': log,
    # ... all callback functions
}

# Pass to view
source_view = SourceView(notebook, state_dict, callbacks)
```

### Pattern 4: Shared State Guards
**What:** Pass guard dictionaries (preview_guard, voice_guard, preset_guard) as part of state
**When to use:** When view needs to check or modify shared state flags

**Example:**
```python
# In main.py
preview_guard = {
    "source": None,
    "image": None,
    "live_render": False,
    # ... all guard flags
}

state_dict = {
    'preview_guard': preview_guard,
    'voice_guard': voice_guard,
    'preset_guard': preset_guard,
    # ... other state
}

# View can access guard
def _wheel_adjust(event):
    if self.state['preview_guard'].get("over_preview"):
        return "break"
```

### Anti-Patterns to Avoid
- **Business logic in views:** Views should only create UI, never process data or make decisions
- **Direct module imports in views:** Views should receive callbacks, not import workflow.py
- **Global state access:** Always pass state via constructor, never use global variables
- **Tight coupling to main.py:** Views should work with any parent that provides required state/callbacks

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Widget state management | Custom state tracking | tkinter StringVar/IntVar/BooleanVar | Built-in, thread-safe, automatic UI updates |
| Layout management | Manual pixel positioning | pack/grid geometry managers | Responsive, maintainable, standard Tkinter |
| Scrollable frames | Custom scroll implementation | Canvas + Frame + Scrollbar pattern | Well-tested, handles edge cases (already used in adjust_tab) |
| Theme management | Hardcoded colors in views | Theme constants (T.ACCENT, T.BG_WHITE) | Already exists in src/components/theme.py |

**Key insight:** Tkinter's built-in state management (StringVar, etc.) and geometry managers (pack, grid) handle 90% of GUI complexity. The project already has excellent component abstractions (Card, Button, Input) - views should compose these, not reinvent them.

## Runtime State Inventory

> Phase 5 is a code refactoring phase (moving UI code to separate files), not a rename/migration phase. No runtime state changes.

**Skipped:** No stored data, live service config, OS-registered state, secrets, or build artifacts are affected by extracting view code into separate files.

## Common Pitfalls

### Pitfall 1: Breaking Closures
**What goes wrong:** Views reference variables from launch_gui() scope that no longer exist after extraction
**Why it happens:** Python closures capture variables by reference; moving code breaks the reference chain
**How to avoid:** Pass all needed state/callbacks via constructor, never rely on outer scope
**Warning signs:** NameError or UnboundLocalError when view code runs

**Example:**
```python
# BAD - relies on closure
class SourceView:
    def build(self):
        Button(frame, command=lambda: log("clicked"))  # log not in scope!

# GOOD - receives callback
class SourceView:
    def __init__(self, callbacks):
        self.callbacks = callbacks
    def build(self):
        Button(frame, command=lambda: self.callbacks['log']("clicked"))
```

### Pitfall 2: Circular Import Dependencies
**What goes wrong:** main.py imports views, views import components, components import theme, theme imports main.py
**Why it happens:** Python executes imports at module load time; circular references cause ImportError
**How to avoid:** Views should only import from components/ and theme, never from main.py or controllers
**Warning signs:** ImportError: cannot import name 'X' from partially initialized module

**Solution:**
```python
# Views import components (OK)
from src.components.ui import Button, Input
from src.components.layout import Card
from src.components.theme import T

# Views receive callbacks, don't import main.py (OK)
def __init__(self, callbacks: Dict[str, Callable]):
    self.callbacks = callbacks
```

### Pitfall 3: Forgetting to Return Frame
**What goes wrong:** View.build() creates widgets but doesn't return the frame, notebook.add() fails
**Why it happens:** Easy to forget return statement when focused on UI construction
**How to avoid:** Always return the top-level frame from build() method
**Warning signs:** TypeError: add() argument must be a widget

**Example:**
```python
# BAD - no return
def build(self):
    frame = tk.Frame(self.parent)
    Button(frame, text="Test").pack()
    # Missing return!

# GOOD - returns frame
def build(self) -> tk.Frame:
    frame = tk.Frame(self.parent)
    Button(frame, text="Test").pack()
    return frame  # ✓
```

### Pitfall 4: Modifying Shared State Incorrectly
**What goes wrong:** View modifies preview_guard dictionary but other code expects old structure
**Why it happens:** Shared state dictionaries are mutable; views can accidentally break contracts
**How to avoid:** Document expected keys in view docstring, only read/write documented keys
**Warning signs:** KeyError or unexpected None values in guard dictionaries

**Example:**
```python
# BAD - adds undocumented key
self.state['preview_guard']['my_new_flag'] = True  # Other code doesn't expect this

# GOOD - only uses documented keys
if self.state['preview_guard'].get("over_preview"):  # Read documented key
    self.state['preview_guard']["over_preview"] = False  # Write documented key
```

### Pitfall 5: Breaking Adjust Tab Scrolling
**What goes wrong:** Adjust tab uses complex Canvas + Frame + Scrollbar setup; extraction breaks scroll behavior
**Why it happens:** Scroll setup spans multiple sections in main.py (lines 324-373); easy to miss pieces
**How to avoid:** Extract entire scroll setup as a unit, test scrolling immediately after extraction
**Warning signs:** Adjust tab doesn't scroll, or scroll events don't work

**Critical code to keep together:**
```python
# Canvas + Scrollbar setup (lines 324-328)
adjust_canvas = tk.Canvas(adjust_tab, highlightthickness=0, bg=T.BG_WHITE)
adjust_scrollbar = ttk.Scrollbar(adjust_tab, orient=tk.VERTICAL, command=adjust_canvas.yview)
adjust_canvas.configure(yscrollcommand=adjust_scrollbar.set)
adjust_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
adjust_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Frame inside canvas (lines 329-330)
adjust_body = tk.Frame(adjust_canvas, bg=T.BG_WHITE)
adjust_window = adjust_canvas.create_window((0, 0), window=adjust_body, anchor="nw")

# Scroll event handlers (lines 332-349)
def _sync_adjust_scroll(_event=None): ...
def _resize_adjust_window(event): ...
def _wheel_adjust(event): ...
adjust_body.bind("<Configure>", _sync_adjust_scroll)
adjust_canvas.bind("<Configure>", _resize_adjust_window)

# Recursive scroll binding (lines 368-373)
def _bind_scroll_recursive(widget): ...
```

## Code Examples

Verified patterns from existing codebase:

### Existing Component Pattern (Already Working)
```python
# Source: src/components/layout/containers.py (lines 7-44)
class Card:
    """Card component — Apple style: flat, light gray, no border."""
    
    def __init__(self, parent, title: str = None, bg: str = None, padding: int = 12):
        _bg = bg or T.BG_LIGHT
        self.frame = tk.Frame(parent, bg=_bg, relief=tk.FLAT, borderwidth=0)
        self.inner = tk.Frame(self.frame, bg=_bg)
        self.inner.pack(padx=padding, pady=padding, fill=tk.BOTH, expand=True)
        
        if title:
            title_label = tk.Label(self.inner, text=title, font=T.FONT_CARD_TITLE,
                                  bg=_bg, fg=T.TEXT_PRIMARY, anchor="w")
            title_label.pack(fill=tk.X, pady=(0, 8))
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self
    
    def get_container(self):
        return self.inner
```

### Existing Controller Pattern (Phase 2)
```python
# Source: src/controllers/source_controller.py (lines 16-43)
class SourceController:
    """Source tab controller - thin wrapper pattern."""
    
    def __init__(self, start_processing_fn: Callable, run_step_fn: Callable = None):
        """Initialize source controller.
        
        Args:
            start_processing_fn: Function to call for monolithic processing
            run_step_fn: Function to call for step-by-step processing (optional)
        """
        self.start_processing_fn = start_processing_fn
        self.run_step_fn = run_step_fn
    
    def on_start_clicked(self) -> None:
        """Handle start processing button click."""
        self.start_processing_fn()
```

### View Pattern (To Be Implemented)
```python
# Pattern for src/views/log_view.py (simplest view)
import tkinter as tk
from typing import Dict, Any
from ..components.ui import TextArea
from ..components.layout import Card
from ..components.theme import T

class LogView:
    """Log tab view - output display and status."""
    
    def __init__(self, parent: tk.Widget, state: Dict[str, Any]):
        """Initialize log view.
        
        Args:
            parent: Parent widget (notebook)
            state: Dictionary containing log_area reference (will be set by view)
        """
        self.parent = parent
        self.state = state
    
    def build(self) -> tk.Frame:
        """Build and return the log tab frame.
        
        Returns:
            Configured tk.Frame ready to add to notebook
        """
        frame = tk.Frame(self.parent, padx=16, pady=16, bg=T.BG_WHITE)
        
        log_card = Card(frame, title="Nhat Ky Xu Ly")
        container = log_card.get_container()
        
        log_area = TextArea(container, height=12, font=T.FONT_MONO)
        log_area.widget.config(bg=T.BG_LOG, fg=T.FG_LOG, insertbackground=T.ACCENT)
        log_area.pack(fill=tk.BOTH, expand=True)
        
        log_card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Store reference for main.py to use
        self.state['log_area'] = log_area
        
        return frame
```

### Main.py Assembly Pattern (After Extraction)
```python
# Pattern for main.py after Phase 5
from src.views import SourceView, AdjustView, DubView, LogView

def launch_gui():
    # ... window setup, state management (lines 213-307) ...
    
    # Create notebook
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Prepare state and callbacks
    state_dict = {
        'source_state': source_state,
        'cover_mode_state': cover_mode_state,
        # ... all state variables ...
        'preview_guard': preview_guard,
        'voice_guard': voice_guard,
        'preset_guard': preset_guard,
    }
    
    callbacks = {
        'paste_clipboard': paste_clipboard,
        'browse_file': browse_file,
        'load_source_preview': load_source_preview,
        'log': log,
        # ... all callback functions ...
    }
    
    # Create views
    source_view = SourceView(notebook, state_dict, callbacks)
    adjust_view = AdjustView(notebook, state_dict, callbacks)
    dub_view = DubView(notebook, state_dict, callbacks)
    log_view = LogView(notebook, state_dict)
    
    # Build and add tabs
    source_frame = source_view.build()
    adjust_frame = adjust_view.build()
    dub_frame = dub_view.build()
    log_frame = log_view.build()
    
    notebook.add(source_frame, text="  Nguon  ")
    notebook.add(adjust_frame, text="  Can Chinh  ")
    notebook.add(dub_frame, text="  Long Tieng  ")
    notebook.add(log_frame, text="  Nhat Ky  ")
    
    # ... controller creation, event wiring (lines 2481-2516) ...
    
    root.mainloop()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Monolithic GUI files | Modular view components | 2020s+ | Easier testing, better code organization |
| Global state | Constructor injection | Modern Python | More testable, explicit dependencies |
| Inline UI code | Component libraries | Always | Reusable, consistent styling |
| Manual layout | Geometry managers | Tkinter standard | Responsive, maintainable |

**Deprecated/outdated:**
- **Inline widget creation:** Modern Tkinter apps use component abstractions (this project already does this well)
- **Global variables for state:** Constructor injection is now standard for testability
- **Monolithic GUI files:** 2000+ line GUI files are considered unmaintainable; 200-400 lines per view is modern standard

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Views can be extracted without breaking functionality if state/callbacks are passed correctly | Architecture Patterns | Extraction would require major refactoring of state management |
| A2 | Adjust tab scroll setup can be moved as a unit to AdjustView | Common Pitfalls | Scroll behavior might break, requiring debugging |
| A3 | main.py will be ~400-500 lines after extraction (currently 2,527) | Summary | Might be larger if helper functions can't be moved |
| A4 | No circular import issues will arise from views importing components | Common Pitfalls | Would need to restructure imports |

**All assumptions verified:** [VERIFIED: Examined main.py structure, existing controller pattern, component architecture]

## Open Questions (RESOLVED)

1. **Should helper functions (paste_clipboard, browse_file, etc.) move to views or stay in main.py?**
   - What we know: These functions are currently defined in launch_gui() scope (lines 1309-1348)
   - What's unclear: Whether they belong in views (closer to UI) or main.py (shared across views)
   - **RESOLVED:** Keep in main.py, pass as callbacks. They're shared across multiple views and access main.py state.

2. **How to handle the complex preview canvas in adjust_tab?**
   - What we know: Preview canvas has extensive event handlers, image rendering, segment markers (lines 1495-2479)
   - What's unclear: Whether to extract preview logic to separate class or keep in AdjustView
   - **RESOLVED:** Keep in AdjustView for Phase 5, consider extracting to PreviewCanvas class in future if needed.

3. **Should step-by-step UI (lines 408-577) be extracted to separate StepView or stay in SourceView?**
   - What we know: Step-by-step UI is ~170 lines, tightly coupled to source tab
   - What's unclear: Whether it deserves its own view class
   - **RESOLVED:** Keep in SourceView for Phase 5. It's part of source tab functionality.

## Environment Availability

> Phase 5 has no external dependencies beyond Python stdlib and existing project dependencies.

**Skipped:** All required tools (Python 3.11.9, tkinter 8.6) are already installed and verified working.

## Validation Architecture

> Validation is enabled (workflow.nyquist_validation not explicitly disabled in config.json).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual testing (no automated test framework) |
| Config file | none — manual testing protocol |
| Quick run command | `scripts\run.bat` (launch GUI, visual inspection) |
| Full suite command | Manual testing checklist (see below) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-01 | Source tab renders correctly | manual | Launch app, check Source tab layout | ❌ Wave 0 |
| REQ-02 | Adjust tab renders correctly | manual | Launch app, check Adjust tab layout | ❌ Wave 0 |
| REQ-03 | Dub tab renders correctly | manual | Launch app, check Dub tab layout | ❌ Wave 0 |
| REQ-04 | Log tab renders correctly | manual | Launch app, check Log tab layout | ❌ Wave 0 |
| REQ-05 | All buttons clickable | manual | Click all buttons, verify no errors | ❌ Wave 0 |
| REQ-06 | State persistence works | manual | Change settings, restart app, verify saved | ❌ Wave 0 |
| REQ-07 | Adjust tab scrolling works | manual | Scroll adjust tab, verify smooth scrolling | ❌ Wave 0 |
| REQ-08 | Preview canvas renders | manual | Load video, check preview in adjust tab | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** Launch app, visual inspection of affected tab
- **Per wave merge:** Full manual testing checklist (all tabs, all interactions)
- **Phase gate:** Complete manual testing + full pipeline test before `/gsd-verify-work`

### Wave 0 Gaps
- No automated tests exist for GUI (manual testing only)
- Consider adding smoke tests in future (e.g., `pytest tests/test_gui_smoke.py` to verify imports and basic instantiation)
- For Phase 5: Manual testing is sufficient given low risk and visual nature of changes

## Security Domain

> Security enforcement is enabled (security_enforcement not explicitly disabled in config.json).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | N/A - desktop app, no authentication |
| V3 Session Management | no | N/A - desktop app, no sessions |
| V4 Access Control | no | N/A - desktop app, single user |
| V5 Input Validation | yes | Existing validation in workflow.py (URL validation, file path checks) |
| V6 Cryptography | no | N/A - no cryptographic operations in views |

### Known Threat Patterns for Tkinter GUI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via file input | Tampering | Existing: Path validation in browse_file(), is_local_file() |
| Command injection via source input | Tampering | Existing: yt-dlp handles URL parsing, no shell=True in subprocess calls |
| XSS in log display | Tampering | N/A - Tkinter Text widget doesn't execute code, only displays text |

**Phase 5 security impact:** Extracting views to separate files does not change security posture. All input validation remains in workflow.py and downloader modules. Views are pure UI, no new attack surface.

## Sources

### Primary (HIGH confidence)
- [VERIFIED: main.py codebase inspection] - Current structure, line counts, patterns
- [VERIFIED: src/components/ inspection] - Existing component architecture
- [VERIFIED: src/controllers/ inspection] - Existing controller pattern from Phase 2
- [VERIFIED: Python 3.11.9 + tkinter 8.6] - Environment verification

### Secondary (MEDIUM confidence)
- [ASSUMED: Tkinter best practices] - Based on training knowledge of Tkinter patterns
- [ASSUMED: MVC separation benefits] - Based on general software engineering principles

### Tertiary (LOW confidence)
- None - all claims verified against codebase or marked as assumptions

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All stdlib, already in use
- Architecture: HIGH - Verified against existing codebase structure
- Pitfalls: HIGH - Identified from actual code patterns in main.py

**Research date:** 2026-04-24
**Valid until:** 2026-05-24 (30 days - stable domain, Tkinter patterns don't change frequently)

**Line count analysis:**
- Current main.py: 2,527 lines
- Source tab section (lines 314-926): ~613 lines
- Adjust tab section (lines 927-1055): ~129 lines
- Dub tab section (lines 1056-1293): ~238 lines
- Log tab section (lines 1294-1306): ~13 lines
- Total extractable: ~993 lines
- Remaining in main.py: ~1,534 lines (includes helper functions, state management, controller wiring)
- Target after extraction: 400-500 lines (will need to extract some helper functions too)

**Extraction complexity:**
- Log tab: EASY (13 lines, no complex state)
- Source tab: MEDIUM (613 lines, step-by-step UI, pipeline state)
- Dub tab: MEDIUM (238 lines, TTS config, voice selection)
- Adjust tab: HARD (129 lines settings + ~1000 lines preview canvas logic, complex scroll setup)
