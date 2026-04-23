---
type: research
focus: refactoring-patterns
created: 2026-04-23
---

# Nghiên Cứu: Refactoring Patterns cho Python GUI Applications

## 1. Tkinter Architecture Patterns

### MVC/MVP Pattern cho Tkinter

**Model-View-Controller** là pattern phổ biến nhất cho GUI applications:

- **Model**: Business logic, data structures (`src/modules/`)
- **View**: UI components, layout (`src/components/`, parts of `main.py`)
- **Controller**: Event handlers, coordination (currently mixed in `main.py`)

**Áp dụng cho Dubbing Extractor**:
- ✅ Model đã tách tốt (`src/modules/workflow.py`, etc.)
- ✅ View components đã có (`src/components/`)
- ❌ Controller logic còn lẫn trong `main.py`

**Refactoring Strategy**:
1. Tạo `src/controllers/` directory
2. Tách event handlers thành controller classes
3. Controller gọi Model, cập nhật View
4. `main.py` chỉ còn app initialization và layout

### Application State Management

**Problem**: Tkinter không có built-in state management

**Solutions**:
1. **Observable Pattern**: State object với callbacks khi thay đổi
2. **Mediator Pattern**: Central coordinator giữa components
3. **Custom Hooks**: Pattern hiện tại (`use_tk_state()`) - đã tốt

**Recommendation**: Giữ hooks pattern hiện tại, thêm centralized app state

### File Organization

**Best Practice Structure**:
```
main.py                 # Entry point only (~100 lines)
src/
  app.py               # Application class
  controllers/         # Event handlers
    source_controller.py
    subtitle_controller.py
    tts_controller.py
  views/               # Complex view logic
    main_window.py
    tabs/
      source_tab.py
      subtitle_tab.py
  components/          # Reusable widgets (đã có)
  modules/             # Business logic (đã có)
```

## 2. Error Handling Best Practices

### Structured Error Handling

**Anti-pattern** (hiện tại):
```python
try:
    operation()
except Exception:
    pass  # Silent failure
```

**Best Practice**:
```python
try:
    operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # Inform user or retry
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise  # Re-raise if truly unexpected
```

### Error Categories

1. **Expected Errors**: User input, network, file not found
   - Handle gracefully, show user-friendly message
   - Log at INFO or WARNING level

2. **Unexpected Errors**: Programming bugs, system failures
   - Log at ERROR or CRITICAL level
   - Show generic error message to user
   - Include stack trace in logs

3. **Recoverable Errors**: Retry logic, fallbacks
   - Implement retry with exponential backoff
   - Log retry attempts

### Logging Strategy

**Levels**:
- `DEBUG`: Detailed diagnostic info (development only)
- `INFO`: Normal operations, progress updates
- `WARNING`: Unexpected but handled situations
- `ERROR`: Errors that need attention
- `CRITICAL`: System-breaking errors

**Best Practice**:
```python
import logging

logger = logging.getLogger(__name__)

# Structured logging
logger.info("Processing video", extra={
    "video_id": video_id,
    "duration": duration,
    "step": "transcribe"
})
```

### Resource Cleanup

**Context Managers** (with statement):
```python
class WhisperModel:
    def __enter__(self):
        self.model = load_model()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.model.cpu()
        del self.model
        gc.collect()
```

**Try-Finally**:
```python
resource = acquire()
try:
    use(resource)
finally:
    release(resource)  # Always runs
```

## 3. Code Cleanup Strategies

### Removing Dead Code

**Detection Methods**:
1. Search for unused imports: `pylint`, `flake8`
2. Search for unused functions: `vulture`
3. Manual review of commented code
4. Check git history for abandoned features

**Safe Removal Process**:
1. Identify dead code candidates
2. Verify with grep/search (no references)
3. Remove in small commits
4. Test after each removal
5. Keep backup before major deletions

### Removing WIP Features

**Dubbing Extractor WIP**:
- `step1_prepare()` through `step7_dub()` functions exist
- No UI buttons to call them
- `pipeline_state` dict declared but unused

**Removal Strategy**:
1. **Option A**: Complete the feature (if valuable)
2. **Option B**: Remove entirely (if not needed)
3. **Option C**: Keep functions, document as "programmatic API"

**Recommendation**: Option B - remove step functions, keep monolithic `process_video()` since UI doesn't support step-by-step execution

### Duplicate Code Elimination

**DRY Principle**: Don't Repeat Yourself

**Refactoring Techniques**:
1. **Extract Function**: Common code → new function
2. **Extract Class**: Related functions → class
3. **Parameterize**: Similar code with slight differences → parameters

**Example** (quick_dub_toggle duplicate):
```python
# Before: Two checkboxes for same setting
dub_checkbox_1 = Checkbox(...)  # Line 196
dub_checkbox_2 = Checkbox(...)  # Line 209

# After: One checkbox, referenced in multiple places
self.dub_checkbox = Checkbox(...)
# Reference it where needed
```

## 4. Documentation Improvements

### Type Hints

**Current State**: Partial type hints

**Best Practice**: Full type hints for public APIs
```python
from typing import Optional, Callable, List, Dict
from pathlib import Path

def process_video(
    source_input: str,
    cover_mode: str = "blur",
    log_cb: Optional[Callable[[str], None]] = None
) -> Dict[str, Path]:
    """Process video through full pipeline.
    
    Args:
        source_input: URL or local file path
        cover_mode: Subtitle covering mode (blur/blackbar/none)
        log_cb: Optional callback for progress logging
        
    Returns:
        Dict with output file paths (video, srt, scripts)
        
    Raises:
        ValueError: Invalid source_input or cover_mode
        RuntimeError: Processing failed
    """
    ...
```

### Docstring Standards

**Google Style** (recommended for Python):
```python
def function(arg1: str, arg2: int) -> bool:
    """Short summary.
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
    """
```

**Vietnamese Comments**: OK for implementation details, but docstrings should be English or bilingual for broader accessibility

### Documentation Updates

**Files to Update**:
1. `CLAUDE.md` - Fix line counts, update architecture
2. `README.md` - Update features, installation
3. `DESIGN.md` - Update if UI structure changes
4. Inline comments - Remove outdated, add for complex logic

## 5. Refactoring Process

### Safe Refactoring Steps

1. **Establish Baseline**
   - Document current behavior
   - Create backup
   - Run manual tests, note results

2. **Small, Incremental Changes**
   - One refactoring at a time
   - Test after each change
   - Commit frequently (atomic commits)

3. **Refactoring Techniques** (in order of safety)
   - Rename (safest)
   - Extract function/class
   - Move code between files
   - Change signatures (riskiest)

4. **Testing Strategy**
   - Manual testing after each change
   - Focus on changed areas
   - Regression testing for core features

### Refactoring Priorities

**High Priority** (high impact, low risk):
1. Remove dead code and WIP features
2. Extract event handlers from main.py
3. Improve error handling (add logging)
4. Fix documentation

**Medium Priority** (medium impact, medium risk):
5. Split main.py into multiple files
6. Add type hints
7. Improve resource cleanup

**Low Priority** (low impact or high risk):
8. Change architecture patterns
9. Add new abstractions
10. Rewrite large sections

## 6. Specific Recommendations for Dubbing Extractor

### Phase 1: Cleanup (Low Risk)
- Remove step1-7 functions (unused)
- Remove pipeline_state dict (unused)
- Remove duplicate quick_dub_toggle
- Remove commented code
- Fix imports (remove unused)
- Update CLAUDE.md line counts

### Phase 2: Extract Controllers (Medium Risk)
- Create `src/controllers/app_controller.py`
- Move event handlers from main.py
- Keep UI layout in main.py
- Controllers call workflow, update UI

### Phase 3: Split main.py (Higher Risk)
- Extract tab creation to separate files
- Create `src/views/main_window.py`
- Create `src/views/tabs/` for each tab
- main.py becomes ~100 lines (just app init)

### Phase 4: Improve Quality (Ongoing)
- Add structured logging
- Improve error handling
- Add type hints
- Add docstrings
- Update documentation

## 7. Tools & Automation

### Code Quality Tools

**Linting**:
- `pylint` - comprehensive linting
- `flake8` - style checking
- `mypy` - type checking

**Formatting**:
- `black` - opinionated formatter
- `isort` - import sorting

**Dead Code Detection**:
- `vulture` - find unused code
- Manual grep for TODOs, FIXMEs

### Pre-commit Hooks

**Not applicable** - no git repo, but could use manual checks

## Kết Luận

**Key Takeaways**:
1. Refactor incrementally, test frequently
2. Remove dead code first (safest)
3. Extract controllers before splitting files
4. Improve error handling throughout
5. Document as you go

**Success Metrics**:
- main.py < 1,500 lines
- No dead/WIP code
- Consistent error handling
- Full type hints on public APIs
- Accurate documentation
