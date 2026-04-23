---
project: Dubbing Extractor - Code Cleanup & Refactoring
created: 2026-04-23
status: draft
---

# Requirements - Dọn Dẹp & Tái Cấu Trúc Codebase

## Mục Tiêu Tổng Quan

Dọn dẹp và tái cấu trúc codebase Dubbing Extractor để cải thiện maintainability, code quality, và developer experience mà không thay đổi tính năng hoặc UI/UX hiện tại.

## Functional Requirements

### FR1: Giữ Nguyên Tất Cả Tính Năng

**Priority**: CRITICAL

**Description**: Tất cả tính năng hiện tại phải hoạt động giống hệt như trước khi refactor.

**Acceptance Criteria**:
- ✅ Download video từ URL (YouTube, Bilibili) hoạt động
- ✅ Load video từ file local hoạt động
- ✅ Whisper transcription hoạt động
- ✅ Google Translate dịch sang tiếng Việt hoạt động
- ✅ Subtitle detection và covering (blur/blackbar/none) hoạt động
- ✅ SRT export (gốc, Việt, song ngữ) hoạt động
- ✅ Subtitle burning vào video hoạt động
- ✅ VieNeu-TTS dubbing hoạt động
- ✅ Tất cả UI controls hoạt động như cũ
- ✅ Config save/load hoạt động
- ✅ Preview subtitle hoạt động

**Testing**: Manual testing toàn bộ pipeline với video mẫu

### FR2: Giữ Nguyên UI/UX

**Priority**: CRITICAL

**Description**: Không thay đổi giao diện, layout, hoặc user experience.

**Acceptance Criteria**:
- ✅ Tất cả tabs vẫn ở vị trí cũ
- ✅ Tất cả buttons, inputs, labels giống hệt
- ✅ Theme và colors không đổi
- ✅ Keyboard shortcuts (nếu có) không đổi
- ✅ Window size và layout không đổi

**Testing**: Visual comparison trước/sau refactor

### FR3: Giữ Nguyên Config Format

**Priority**: CRITICAL

**Description**: `config.json` format không thay đổi, user settings được bảo toàn.

**Acceptance Criteria**:
- ✅ Tất cả keys trong config.json vẫn hoạt động
- ✅ Không thêm required keys mới
- ✅ Backward compatible với config cũ
- ✅ User không mất settings sau khi update

**Testing**: Load config.json cũ vào version mới

## Non-Functional Requirements

### NFR1: Code Size Reduction

**Priority**: HIGH

**Target**: Giảm main.py từ ~3,000 dòng xuống < 1,500 dòng (50%)

**Approach**:
- Extract event handlers ra controllers
- Extract tab creation ra separate files
- Extract helper functions ra utilities
- Remove dead code

**Measurement**: `wc -l main.py` trước và sau

### NFR2: Remove Dead Code

**Priority**: HIGH

**Scope**:
- ❌ Remove `step1_prepare()` through `step7_dub()` functions (unused)
- ❌ Remove `pipeline_state` dict (declared but unused)
- ❌ Remove duplicate `quick_dub_toggle` checkbox (lines 196-209)
- ❌ Remove commented-out code
- ❌ Remove unused imports
- ❌ Remove unused variables

**Acceptance Criteria**:
- ✅ No functions defined but never called
- ✅ No variables declared but never used
- ✅ No commented-out code blocks
- ✅ No unused imports (verified by linter)

**Testing**: `vulture` or manual grep for unused code

### NFR3: Consistent Error Handling

**Priority**: HIGH

**Current Issues**:
- Many `except Exception: pass` (silent failures)
- Inconsistent error logging
- No user feedback on errors
- Unicode errors handled ad-hoc

**Requirements**:
- ✅ No silent failures (`except: pass` only for truly ignorable errors)
- ✅ All errors logged with appropriate level (ERROR, WARNING, INFO)
- ✅ User-facing errors show in GUI (messagebox or status)
- ✅ Include context in error messages (what operation failed)
- ✅ Use specific exception types (not bare `Exception`)

**Pattern**:
```python
try:
    operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    show_error_to_user(f"Không thể thực hiện: {e}")
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    show_error_to_user("Lỗi không mong đợi. Xem log để biết chi tiết.")
```

### NFR4: Improved Logging

**Priority**: MEDIUM

**Requirements**:
- ✅ Use Python `logging` module (not just print/callback)
- ✅ Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ Log to file: `output/app.log` (rotating)
- ✅ Include timestamps, module names, line numbers
- ✅ Structured logging for important events

**Configuration**:
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('output/app.log', maxBytes=10MB, backupCount=3),
        StreamHandler()  # Console output
    ]
)
```

### NFR5: Type Hints Coverage

**Priority**: MEDIUM

**Target**: 100% type hints for public APIs

**Scope**:
- ✅ All public functions in `src/modules/`
- ✅ All public functions in `src/components/`
- ✅ All controller methods (after extraction)
- ⚠️ Private functions: optional (use judgment)
- ⚠️ main.py: optional (will be mostly UI code)

**Example**:
```python
from typing import Optional, Callable, Dict, List
from pathlib import Path

def process_video(
    source_input: str,
    cover_mode: str = "blur",
    log_cb: Optional[Callable[[str], None]] = None
) -> Dict[str, Path]:
    ...
```

**Verification**: Run `mypy src/` (no errors on public APIs)

### NFR6: Documentation Accuracy

**Priority**: MEDIUM

**Updates Required**:
- ✅ `CLAUDE.md` - Fix line counts, update architecture description
- ✅ `README.md` - Update if structure changes
- ✅ Inline comments - Remove outdated, add for complex logic
- ✅ Docstrings - Add for public functions (Google style)

**Acceptance Criteria**:
- ✅ No incorrect line counts or file references
- ✅ Architecture description matches actual code
- ✅ All public functions have docstrings
- ✅ Complex algorithms have explanatory comments

### NFR7: Resource Cleanup

**Priority**: MEDIUM

**Requirements**:
- ✅ Explicit cleanup for Whisper model (already exists: `release_model()`)
- ✅ Explicit cleanup for TTS resources (already exists: `release_tts_resources()`)
- ✅ CUDA memory cleared after GPU operations
- ✅ File handles closed properly (use context managers)
- ✅ Temp files cleaned up after processing

**Pattern**:
```python
# Context manager for resources
with open(file, 'r') as f:
    data = f.read()
# File automatically closed

# Explicit cleanup
try:
    model = load_model()
    result = model.process()
finally:
    model.cleanup()
    gc.collect()
```

## Architecture Requirements

### AR1: Separation of Concerns

**Priority**: HIGH

**Current State**: main.py mixes UI, event handling, and some business logic

**Target State**:
```
main.py              # App initialization, window setup (~100-200 lines)
src/
  controllers/       # Event handlers, coordination
    app_controller.py
    source_controller.py
    subtitle_controller.py
    tts_controller.py
  views/             # Complex view logic (optional, if needed)
    main_window.py
  components/        # Reusable UI widgets (already good)
  modules/           # Business logic (already good)
```

**Acceptance Criteria**:
- ✅ main.py chỉ chứa app initialization và layout
- ✅ Event handlers tách ra controllers
- ✅ Business logic vẫn ở `src/modules/` (không di chuyển)
- ✅ UI components vẫn ở `src/components/` (không di chuyển)

### AR2: File Organization

**Priority**: MEDIUM

**New Structure**:
```
src/
  controllers/
    __init__.py
    app_controller.py      # Main app coordination
    source_controller.py   # Source tab event handlers
    subtitle_controller.py # Subtitle tab event handlers
    tts_controller.py      # TTS tab event handlers
```

**Each Controller**:
- Handles events for one tab or feature area
- Calls `src/modules/` for business logic
- Updates UI via callbacks or direct widget access
- No business logic in controllers (thin layer)

### AR3: Backward Compatibility

**Priority**: CRITICAL

**Requirements**:
- ✅ Existing `config.json` works without changes
- ✅ Existing `cookies.txt` works without changes
- ✅ Output file formats unchanged
- ✅ No new required dependencies
- ✅ Python 3.11 compatibility maintained

## Constraints

### C1: No Breaking Changes

**Must NOT**:
- Change any user-facing behavior
- Change config.json format
- Change output file formats
- Break existing workflows
- Require user to reconfigure

### C2: No New Dependencies

**Must NOT**:
- Add new packages to requirements.txt (unless absolutely necessary)
- Change Python version requirement
- Add external services or APIs

**Exception**: Development tools OK (linters, formatters) if not in requirements.txt

### C3: Preserve Performance

**Must NOT**:
- Slow down video processing
- Increase memory usage significantly
- Increase startup time noticeably

**Acceptable**: Slight overhead from better error handling/logging

### C4: No Git Repository

**Context**: Project is not a git repo

**Implications**:
- Cannot use git commits for atomic changes
- Use file backups instead
- Document changes in CHANGELOG or similar

## Success Criteria

### Quantitative Metrics

1. **Code Size**: main.py < 1,500 lines (currently ~3,000)
2. **Dead Code**: 0 unused functions/variables (verified by vulture)
3. **Type Hints**: 100% coverage on public APIs (verified by mypy)
4. **Error Handling**: 0 bare `except Exception: pass` (except justified cases)
5. **Documentation**: 0 incorrect line counts or file references

### Qualitative Metrics

1. **Maintainability**: New developer can understand structure in < 30 minutes
2. **Debuggability**: Errors are logged with enough context to diagnose
3. **Testability**: Code structure makes it easier to add tests later
4. **Readability**: Code follows consistent patterns and conventions

### Testing Checklist

**Manual Testing** (must pass):
- [ ] Download video từ YouTube
- [ ] Download video từ Bilibili
- [ ] Load video từ file local
- [ ] Transcribe với Whisper (CPU)
- [ ] Translate sang tiếng Việt
- [ ] Detect và cover subtitles (blur mode)
- [ ] Detect và cover subtitles (blackbar mode)
- [ ] Export SRT files (3 loại)
- [ ] Burn subtitles vào video
- [ ] TTS dubbing với VieNeu
- [ ] Preview subtitle
- [ ] Save/load config
- [ ] Tất cả UI controls hoạt động

**Code Quality Checks**:
- [ ] No unused imports (flake8)
- [ ] No unused code (vulture)
- [ ] Type hints on public APIs (mypy)
- [ ] No silent failures (manual review)
- [ ] Documentation accurate (manual review)

## Out of Scope

**Explicitly NOT included**:
- ❌ Adding new features
- ❌ Changing UI/UX design
- ❌ Adding threading/async (future work)
- ❌ Adding automated tests (future work)
- ❌ Performance optimization (unless regression)
- ❌ Completing step-by-step UI (removing instead)
- ❌ Refactoring business logic in `src/modules/` (already good)

## Risks & Mitigations

### Risk 1: Breaking Existing Functionality

**Likelihood**: MEDIUM  
**Impact**: HIGH

**Mitigation**:
- Refactor incrementally (small changes)
- Test after each change
- Keep backup before major changes
- Focus on low-risk refactorings first (remove dead code)

### Risk 2: Introducing New Bugs

**Likelihood**: MEDIUM  
**Impact**: MEDIUM

**Mitigation**:
- Manual testing checklist
- Code review (if possible)
- Incremental changes with testing

### Risk 3: Scope Creep

**Likelihood**: MEDIUM  
**Impact**: MEDIUM

**Mitigation**:
- Strict scope definition (this document)
- Resist temptation to add features
- Focus on cleanup, not enhancement

## Dependencies

**Required Before Starting**:
- ✅ Codebase map complete (`.planning/codebase/`)
- ✅ Backup exists (`dubbing-extractor-backup-20260423_1630`)
- ✅ Manual testing baseline (know current behavior)

**No External Dependencies**: All work can be done with existing tools

## Timeline Estimate

**Phase 1: Cleanup** (Low Risk) - 2-3 hours
- Remove dead code
- Fix documentation
- Remove duplicates

**Phase 2: Extract Controllers** (Medium Risk) - 3-4 hours
- Create controller structure
- Move event handlers
- Test thoroughly

**Phase 3: Split main.py** (Higher Risk) - 2-3 hours
- Extract tab creation
- Reorganize imports
- Final testing

**Phase 4: Quality Improvements** (Ongoing) - 2-3 hours
- Add type hints
- Improve error handling
- Add logging
- Final documentation

**Total**: 9-13 hours of focused work

## Approval

**Ready to Proceed When**:
- ✅ Requirements reviewed and approved
- ✅ Backup confirmed
- ✅ Manual testing baseline established
- ✅ Roadmap created with phases
