---
type: codebase-map
focus: conventions
created: 2026-04-23
---

# Code Conventions

## Language

**Comments**: Vietnamese
- All code comments in Vietnamese
- Docstrings in Vietnamese or English
- User-facing strings in Vietnamese

**Code**: English
- Variable names: English
- Function names: English
- Class names: English
- Module names: English

**Example**:
```python
def step1_prepare(source_input: str, log_cb: Optional[Callable] = None) -> dict:
    """Bước 1: Tải video hoặc dùng file local, trích xuất audio."""
    _log = _make_log(log_cb)
    _log("\n" + "="*52 + "\n  BƯỚC 1: TẢI VIDEO & AUDIO\n" + "="*52)
    # Tải video từ URL hoặc file local
    if is_local_file(source_input):
        raw_video = Path(source_input)
```

## Naming Conventions

### Files and Directories
- Lowercase with underscores: `whisper_engine.py`, `video_processing/`
- Descriptive names: `subtitle_burner.py`, `ytdlp_wrapper.py`

### Functions
- Lowercase with underscores: `process_video()`, `extract_audio_local()`
- Verb-noun pattern: `write_srt()`, `detect_sub_events()`
- Private functions prefixed with `_`: `_make_log()`, `_apply_subtitle_timing()`

### Variables
- Lowercase with underscores: `raw_video`, `segs_vi`, `out_dir`
- Descriptive names: `subtitle_timing_scale`, `blur_padding_px`
- Abbreviations: `segs` (segments), `cb` (callback), `px` (pixels)

### Constants
- Uppercase with underscores: `APP_LOG_FILE`, `APP_LOG_MAX_BYTES`
- Defined at module level

### Classes
- PascalCase: `Button`, `Card`, `Section`
- Descriptive names: `WhisperEngine`, `SubtitleBurner`

### Type Hints
- Used throughout: `Optional[Callable]`, `List[Dict]`, `Path`
- Return types specified: `-> dict`, `-> list`, `-> None`

## Code Style

### Imports
- Standard library first
- Third-party packages second
- Local imports last
- Grouped with blank lines between groups

**Example**:
```python
import os
import sys
from pathlib import Path
from typing import Optional, Callable

from .downloader.platform_detector import detect_platform
from .transcription.whisper_engine import transcribe
from ..config import config
```

### Line Length
- No strict limit, but generally ~100-120 characters
- Long strings broken with parentheses or backslashes

### Indentation
- 4 spaces (no tabs)
- Consistent throughout

### Whitespace
- Blank line between functions
- Two blank lines between classes
- Space after commas: `func(a, b, c)`
- No space before colons in dicts: `{"key": "value"}`

### String Formatting
- f-strings preferred: `f"Output: {out_dir}"`
- `.format()` for complex cases
- `%` formatting avoided

### Docstrings
- Triple quotes: `"""Docstring."""`
- First line summary
- Optional detailed description
- Args/Returns sections for complex functions

**Example**:
```python
def step1_prepare(
    source_input: str,
    log_cb: Optional[Callable] = None,
) -> dict:
    """Bước 1: Tải video hoặc dùng file local, trích xuất audio.

    Returns:
        dict với keys: raw_video, raw_audio, title, out_dir, temp_dir
    """
```

## Error Handling

### Try-Except Blocks
- Used for I/O operations
- Used for external tool calls (ffmpeg, yt-dlp)
- Specific exceptions caught when possible
- Bare `except:` used for logging/cleanup only

**Example**:
```python
try:
    if not APP_LOG_FILE.exists() or APP_LOG_FILE.stat().st_size < APP_LOG_MAX_BYTES:
        return
    if APP_LOG_BACKUP_FILE.exists():
        APP_LOG_BACKUP_FILE.unlink()
    APP_LOG_FILE.replace(APP_LOG_BACKUP_FILE)
except Exception:
    pass
```

### Fallback Behavior
- Unicode errors: fallback to ASCII
- Missing resources: graceful degradation
- User-facing errors: Vietnamese messages in GUI

**Example**:
```python
try:
    log_cb(msg)
except UnicodeEncodeError:
    fallback = str(msg).encode("ascii", "replace").decode("ascii")
    log_cb(fallback)
```

## Patterns

### Callback Pattern
- Functions accept `log_cb: Optional[Callable]` for progress updates
- Wrapper function `_make_log()` handles None case
- Used throughout workflow and modules

**Example**:
```python
def _make_log(log_cb: Optional[Callable]):
    def _log(msg):
        if log_cb:
            try:
                log_cb(msg)
            except UnicodeEncodeError:
                fallback = str(msg).encode("ascii", "replace").decode("ascii")
                log_cb(fallback)
    return _log
```

### Path Handling
- `pathlib.Path` preferred over `os.path`
- String conversion when needed: `str(path)`
- Forward slashes work on Windows (Git Bash)

### Configuration Access
- Global `config` dict imported from `src.config`
- Accessed via `config.get("key", default)`
- Saved via `save_app_config()`

### Resource Cleanup
- Explicit cleanup functions: `release_tts_resources()`
- Garbage collection: `gc.collect()` after heavy operations
- Memory logging: `_log_runtime_memory(stage)`

## UI Component Patterns

### Theme System
- Design tokens in `src/components/theme.py`
- Class `T` with constants: `T.BG_DARK`, `T.FONT_BODY`, `T.SPACE_MD`
- Apple-inspired design (SF Pro → Segoe UI fallback)

### Component Structure
- Custom Tkinter widgets in `src/components/ui/`
- Layout containers in `src/components/layout/`
- Props passed as constructor arguments
- Consistent API across components

**Example**:
```python
Button(
    parent,
    text="Bắt Đầu",
    command=on_start,
    style="primary"
)
```

### State Management
- React-like hooks: `use_tk_state()`
- Tkinter variables: `StringVar`, `BooleanVar`
- Config persistence via `config.json`

## File Organization

### Module Structure
- `__init__.py` exports public API
- Private functions prefixed with `_`
- Related functions grouped together
- Imports at top

### Output Files
- Vietnamese names: `phu_de_goc.srt`, `video_long_tieng.mp4`
- Timestamp format: `YYYYMMDD_HHMM`
- Organized in per-video directories

## Comments

### When to Comment
- Complex algorithms: subtitle timing adjustments
- Non-obvious behavior: ffmpeg PowerShell wrapper
- Workarounds: RTX 5060 CPU-only Whisper
- Section headers: `# ── Colors ──────────────────────`

### When NOT to Comment
- Obvious code: `# Load config`
- Redundant docstrings
- Commented-out code (delete instead)

## Type Hints

### Usage
- Function signatures: parameters and return types
- Complex types: `List[Dict]`, `Optional[Callable]`
- Path types: `Path` from `pathlib`

### Not Used
- Variable annotations (rare)
- Full type coverage (pragmatic approach)

## Testing

### Current State
- Minimal test coverage
- Manual testing via GUI
- Integration tests only: `tests/test_whisper_engine.py`

### No Conventions Yet
- No unit test structure
- No mocking patterns
- No CI/CD integration

## Documentation

### Code Documentation
- Docstrings for public functions
- Inline comments for complex logic
- Vietnamese comments OK

### Project Documentation
- README.md (English)
- HUONG_DAN_SU_DUNG.md (Vietnamese user guide)
- DESIGN.md (design system)
- CLAUDE.md (AI context)

## Version Control

### Not Tracked
- `venv/` - virtual environment
- `output/` - generated files
- `.cache/` - model cache
- `config.json` - user settings
- `cookies.txt` - authentication
- `.env` - secrets

### Tracked
- Source code (`src/`, `main.py`)
- Scripts (`scripts/`)
- Documentation (`*.md`)
- Requirements (`requirements.txt`)
- Templates (`.env.example`)
