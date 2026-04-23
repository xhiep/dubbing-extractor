# Changelog

All notable changes to the Dubbing Extractor project.

## [Refactoring v2.6] - 2026-04-23

Major codebase cleanup and quality improvements across 4 phases.

### Phase 1: Code Cleanup (Low Risk) - 2026-04-23

#### Changed
- Updated CLAUDE.md with accurate line counts and structure
- Verified all imports are used (no unused imports found)
- Confirmed no commented-out code blocks exist

#### Verified
- All step functions (step1-7) are actively used in step-by-step UI
- Pipeline state is used for step-by-step mode tracking
- No duplicate code found
- All features tested and working

### Phase 2: Extract Controllers (Medium Risk) - 2026-04-23

#### Added
- `src/controllers/` directory with MVC-like architecture
- `src/controllers/app_controller.py` - Config save/load, app-level coordination
- `src/controllers/source_controller.py` - Video source and processing controls
- `src/controllers/subtitle_controller.py` - Subtitle parameters and preview
- `src/controllers/tts_controller.py` - TTS mode, voice selection, preview

#### Changed
- Extracted event handlers from main.py to controller classes
- Used thin wrapper pattern (delegates to existing functions)
- Separated UI events from business logic
- main.py now wires controllers to UI widgets

#### Improved
- Code organization and separation of concerns
- Maintainability through clear controller responsibilities
- All features preserved and tested working

### Phase 3: Split main.py Further (Higher Risk) - 2026-04-23

#### Added
- `src/utils/ui_helpers.py` - Pure UI geometry helper functions
  - `expand_band_from_center()` - Expand subtitle band with padding
  - `shift_band()` - Shift subtitle band vertically

#### Changed
- Organized imports into 3 clear categories:
  - Standard Library (json, os, sys, datetime, pathlib)
  - Third-Party (tkinter, winsound)
  - Local Modules (utils, config, modules, components, controllers)
- Added 9 major section markers to `launch_gui()` for navigation:
  - Section 1: Window Setup
  - Section 2: Configuration & State Management
  - Section 3: UI Layout - Notebook & Tabs
  - Section 4: Source Tab - Video Input & Processing
  - Section 5: Adjust Tab - Subtitle Parameters
  - Section 6: Dub Tab - TTS Configuration
  - Section 7: Log Tab - Output & Status
  - Section 8: Controller Initialization & Event Wiring
  - Section 9: Start Application

#### Improved
- Code navigation significantly improved with section markers
- main.py structure: 2,516 → 2,522 lines (net +6: -26 extraction +32 organization)
- Pure functions extracted for better modularity
- All features verified working

### Phase 4: Quality Improvements (Ongoing) - 2026-04-23

#### Added
- **Structured Logging** (`src/utils/logger.py`)
  - RotatingFileHandler (10MB max, 3 backups)
  - Logs to `output/app.log` with timestamps and module names
  - Console output for ERROR level only
  - Integrated across all 9 modules

- **Type Hints** (100% public API coverage)
  - Added type hints to all public functions in modules and controllers
  - Created `mypy.ini` for incremental type checking
  - Used Python 3.11 syntax (`Path`, `Optional`, `Callable`, `Dict`, `List`)
  - 40+ functions annotated

- **Google-Style Docstrings**
  - Added comprehensive docstrings to 20+ public functions
  - Includes Args, Returns, and Raises sections
  - Consistent format across all modules

- **Resource Cleanup**
  - Implemented `managed_whisper_model()` context manager
  - Automatic cleanup even on exceptions
  - CPU migration, garbage collection, CUDA cache clearing

#### Changed
- **Error Handling Improvements**
  - Reduced bare `except Exception:` from 9+ to 2 (only in cleanup code)
  - Replaced with specific exception types:
    - Network: `urllib.error.URLError`, `ConnectionError`, `OSError`
    - Subprocess: `subprocess.SubprocessError`, `subprocess.CalledProcessError`
    - File I/O: `OSError`, `IOError`, `FileNotFoundError`
    - Parsing: `ValueError`, `TypeError`
    - Runtime: `AttributeError`, `RuntimeError`, `ImportError`
  - All errors logged with context

- **Documentation Updates**
  - Updated CLAUDE.md with Phase 4 improvements
  - Verified README.md and DESIGN.md accuracy
  - Added this CHANGELOG.md

#### Improved
- Code quality and maintainability
- Developer experience with better tooling support
- Error visibility and debugging capability
- Resource management and memory cleanup

## Summary of Refactoring

### Before Refactoring
- main.py: ~2,516 lines (monolithic)
- Error handling: Inconsistent, many silent failures
- Type hints: Partial coverage
- Documentation: Some inaccuracies
- Logging: Print statements and callbacks only

### After Refactoring
- main.py: ~2,522 lines (organized with section markers)
- Controllers: 4 controller classes for event handling
- Utilities: ui_helpers.py, logger.py
- Error handling: Consistent, specific exceptions, logged with context
- Type hints: 100% on public APIs (40+ functions)
- Documentation: Accurate and complete with docstrings
- Logging: Structured logging with rotation

### Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Code organization | Monolithic | Modular (MVC-like) | Clear separation |
| Error handling | Inconsistent | Consistent | Specific exceptions |
| Type hints | Partial | 100% public API | Full coverage |
| Docstrings | Minimal | Comprehensive | Google-style |
| Logging | Print/callback | Structured | RotatingFileHandler |
| Resource cleanup | Manual | Context managers | Automatic |

### All Features Preserved
- ✅ Video download (YouTube, Bilibili)
- ✅ Whisper transcription
- ✅ Google Translate
- ✅ Subtitle detection & covering
- ✅ SRT export
- ✅ Subtitle burning
- ✅ VieNeu-TTS dubbing
- ✅ All UI controls
- ✅ Config persistence

## Development

### Tools Added
- mypy - Static type checking
- Python logging module - Structured logging

### Backup
- GitHub: https://github.com/xhiep/dubbing-extractor
- Local: C:\Users\xhiep\Downloads\dubbing-extractor-backup-20260423_1630

## Contributors

- xhiep - Project owner
- Claude Sonnet 4 - Refactoring assistance

---

**Quick Start**: `scripts\install.bat` → `scripts\run.bat`

**Documentation**: See `docs/` folder and `CLAUDE.md`
