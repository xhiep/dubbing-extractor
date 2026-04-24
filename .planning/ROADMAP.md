---
project: Dubbing Extractor - Code Cleanup & Refactoring
created: 2026-04-23
status: draft
---

# Roadmap - Dọn Dẹp & Tái Cấu Trúc

## Tổng Quan

Roadmap gồm 5 phases, thực hiện tuần tự từ low-risk đến higher-risk. Mỗi phase kết thúc với manual testing để đảm bảo không có regression.

**Total Estimate**: 11-16 giờ làm việc tập trung (Phases 1-4 hoàn thành, Phase 5 còn lại)

## Phase 1: Code Cleanup (Low Risk)

**Goal**: Xóa code thừa, dở dang, và cập nhật documentation

**Duration**: 2-3 giờ

**Risk Level**: LOW - Chỉ xóa code không dùng, không thay đổi logic

### Tasks

#### 1.1: Remove WIP Step Functions
- **File**: `src/modules/workflow.py`
- **Action**: Xóa `step1_prepare()` through `step7_dub()` (7 functions)
- **Reason**: Functions tồn tại nhưng không có UI để gọi, không được dùng
- **Keep**: `process_video()` function (main pipeline)
- **Lines Saved**: ~200-300 lines

#### 1.2: Remove Pipeline State Dict
- **File**: `main.py`
- **Action**: Xóa `pipeline_state` dict declaration và references
- **Reason**: Declared but never used
- **Lines Saved**: ~10-20 lines

#### 1.3: Remove Duplicate TTS Checkbox
- **File**: `main.py` (lines 196-209)
- **Action**: Xóa duplicate `quick_dub_toggle` checkbox
- **Reason**: Duplicate control for same setting
- **Keep**: One checkbox, remove the other
- **Lines Saved**: ~15 lines

#### 1.4: Remove Commented Code
- **Files**: All `.py` files
- **Action**: Search and remove commented-out code blocks
- **Command**: `grep -r "^#.*def \|^#.*class " src/ main.py`
- **Exception**: Keep commented explanations, remove commented code

#### 1.5: Remove Unused Imports
- **Files**: All `.py` files
- **Action**: Remove imports that are never used
- **Tool**: `flake8` or manual review
- **Common culprits**: `import sys`, `import os` when not used

#### 1.6: Update CLAUDE.md
- **File**: `CLAUDE.md`
- **Action**: 
  - Fix line count: main.py ~3000 lines (not ~1760)
  - Update architecture description if needed
  - Update "Việc đang làm" section (remove step-by-step UI mention)

#### 1.7: Update Documentation Line Counts
- **Files**: `README.md`, `DESIGN.md`
- **Action**: Verify and update any line counts or file references
- **Check**: All file paths are correct

### Success Criteria
- ✅ No unused functions remain
- ✅ No commented-out code blocks
- ✅ No unused imports (flake8 clean)
- ✅ Documentation accurate
- ✅ All features still work (manual test)

### Testing
- Run app: `scripts\run.bat`
- Quick smoke test: Load video, check all tabs open
- Full test: Run one complete pipeline (download → dub)

### Deliverables
- Cleaned `src/modules/workflow.py` (step functions removed)
- Cleaned `main.py` (duplicates removed, ~200 lines saved)
- Updated `CLAUDE.md`
- Testing report: "Phase 1 complete, all features working"

---

## Phase 2: Extract Controllers (Medium Risk)

**Goal**: Tách event handlers ra khỏi main.py vào controller classes

**Duration**: 3-4 giờ

**Risk Level**: MEDIUM - Di chuyển code, có thể break event handling

### Tasks

#### 2.1: Create Controller Structure
- **Action**: Tạo `src/controllers/` directory
- **Files**:
  ```
  src/controllers/
    __init__.py
    app_controller.py
    source_controller.py
    subtitle_controller.py
    tts_controller.py
  ```

#### 2.2: Design Controller Pattern
- **Pattern**: Controller nhận widget references, gọi modules, update UI
- **Example**:
  ```python
  class SourceController:
      def __init__(self, widgets, config):
          self.widgets = widgets
          self.config = config
      
      def on_start_clicked(self):
          source = self.widgets.source_input.get()
          # Call business logic
          result = process_video(source, ...)
          # Update UI
          self.widgets.log_area.append(result)
  ```

#### 2.3: Extract Source Tab Handlers
- **File**: `src/controllers/source_controller.py`
- **Move from main.py**:
  - `on_start_clicked()` - Start processing button
  - `on_source_changed()` - Source input change handler
  - `on_preview_clicked()` - Preview button
  - Related helper functions

#### 2.4: Extract Subtitle Tab Handlers
- **File**: `src/controllers/subtitle_controller.py`
- **Move from main.py**:
  - `on_cover_mode_changed()` - Cover mode selection
  - `on_preview_subtitle()` - Subtitle preview
  - `on_blur_params_changed()` - Blur parameter adjustments
  - Related helper functions

#### 2.5: Extract TTS Tab Handlers
- **File**: `src/controllers/tts_controller.py`
- **Move from main.py**:
  - `on_dub_mode_changed()` - TTS mode selection
  - `on_voice_changed()` - Voice selection
  - `on_tts_preview()` - TTS preview
  - Related helper functions

#### 2.6: Create App Controller
- **File**: `src/controllers/app_controller.py`
- **Purpose**: Coordinate between controllers, handle app-level events
- **Responsibilities**:
  - Config save/load
  - Window close handler
  - Cross-tab coordination

#### 2.7: Update main.py
- **Action**: Import controllers, wire up event handlers
- **Pattern**:
  ```python
  from src.controllers import SourceController, SubtitleController, TtsController
  
  # Create controllers
  source_ctrl = SourceController(source_widgets, config)
  subtitle_ctrl = SubtitleController(subtitle_widgets, config)
  tts_ctrl = TtsController(tts_widgets, config)
  
  # Wire up events
  start_button.config(command=source_ctrl.on_start_clicked)
  ```

### Success Criteria
- ✅ All event handlers moved to controllers
- ✅ main.py < 2000 lines (from ~3000)
- ✅ Controllers are thin (no business logic)
- ✅ All UI interactions still work
- ✅ No regressions in functionality

### Testing
- **Full Manual Test**: Run complete pipeline
- **UI Test**: Click every button, change every input
- **Config Test**: Save/load config, verify persistence
- **Error Test**: Try invalid inputs, verify error handling

### Deliverables
- `src/controllers/` with 4 controller files
- Updated `main.py` (~2000 lines, down from ~3000)
- Testing report: "Phase 2 complete, all features working"

---

## Phase 3: Split main.py Further (Higher Risk)

**Goal**: Extract pure helper functions and reorganize main.py with clear section markers

**Duration**: 2-3 giờ

**Risk Level**: MEDIUM - Code organization, minimal risk of breaking functionality

**Plans**: 3 plans in 3 waves

Plans:
- [ ] 03-01-PLAN.md — Extract pure helper functions to ui_helpers.py
- [ ] 03-02-PLAN.md — Organize imports and add section markers
- [ ] 03-03-PLAN.md — Final verification and documentation update

### Wave Structure

| Wave | Plans | Autonomous |
|------|-------|------------|
| 1 | 03-01 | yes |
| 2 | 03-02 | yes |
| 3 | 03-03 | no (has checkpoint) |

### Success Criteria
- ✅ Pure helper functions extracted to src/utils/ui_helpers.py
- ✅ Imports organized into 3 categories (stdlib, third-party, local)
- ✅ 9 major section markers added to launch_gui()
- ✅ CLAUDE.md updated with accurate line counts
- ✅ All features work identically
- ✅ Code navigation significantly improved

### Testing
- **Automated**: Syntax checks, import verification, organization checks
- **Manual**: Full application testing (all tabs, processing, config persistence)

### Deliverables
- `src/utils/ui_helpers.py` with 2 pure functions
- Reorganized `main.py` with clear sections (~2,517 lines)
- Updated `CLAUDE.md`
- Testing report: "Phase 3 complete, all features working"
---

## Phase 4: Quality Improvements (Ongoing)

**Goal**: Improve error handling, logging, type hints, and documentation

**Duration**: 2-3 giờ

**Risk Level**: LOW-MEDIUM - Improvements, not restructuring

**Plans:** 4 plans

Plans:
- [ ] 04-01-PLAN.md — Structured logging and error handling improvements
- [ ] 04-02-PLAN.md — Add type hints to all public APIs
- [ ] 04-03-PLAN.md — Add docstrings and improve resource cleanup
- [ ] 04-04-PLAN.md — Update documentation and create CHANGELOG

### Wave Structure

| Wave | Plans | Autonomous |
|------|-------|------------|
| 1 | 04-01 | yes |
| 2 | 04-02 | yes |
| 3 | 04-03 | yes |
| 4 | 04-04 | no (has checkpoint) |

### Success Criteria
- ✅ No `except Exception: pass` without justification
- ✅ Structured logging in place
- ✅ Type hints on all public APIs (mypy clean)
- ✅ Docstrings on all public functions
- ✅ Documentation accurate and complete
- ✅ CHANGELOG created

### Testing
- **Mypy Check**: `mypy src/` (no errors on public APIs)
- **Flake8 Check**: `flake8 src/ main.py` (clean)
- **Manual Test**: Full pipeline one more time
- **Log Review**: Check `output/app.log` for proper logging

### Deliverables
- Improved error handling across all modules
- `src/utils/logger.py` with structured logging
- Type hints on all public APIs
- Docstrings on all public functions
- Updated documentation
- `CHANGELOG.md`
- Final testing report: "Phase 4 complete, all quality improvements done"

---

---

## Phase 5: Extract View Components (Final Refactor)

**Goal**: Tách 4 tabs UI ra thành view files riêng, giảm main.py xuống ~400 dòng

**Duration**: 2-3 giờ

**Risk Level**: MEDIUM - Di chuyển UI code, có thể break layout

**Plans:** 5 plans

Plans:
- [ ] 05-01-PLAN.md — Create views module and extract Log tab (simplest)
- [ ] 05-02-PLAN.md — Extract Dub tab to DubView
- [ ] 05-03-PLAN.md — Extract Source tab to SourceView
- [ ] 05-04-PLAN.md — Extract Adjust tab to AdjustView (most complex, includes scroll setup)
- [ ] 05-05-PLAN.md — Integration testing and documentation update

### Wave Structure

| Wave | Plans | Autonomous |
|------|-------|------------|
| 1 | 05-01 | yes |
| 2 | 05-02 | yes |
| 3 | 05-03 | yes |
| 4 | 05-04 | yes |
| 5 | 05-05 | no (has checkpoint) |

### Success Criteria
- [ ] All 4 tabs extracted to separate view files
- [ ] main.py < 500 dòng (từ ~2,527)
- [ ] Views are pure UI (no business logic)
- [ ] All tabs render correctly
- [ ] No regressions in functionality

### Testing
- **Automated**: Syntax checks, import verification, organization checks
- **Manual**: Full application testing (all tabs, processing, config persistence)

### Deliverables
- `src/views/` với 4 view files
- Updated `main.py` (~400 dòng, giảm từ ~2,527)
- Updated `CLAUDE.md` với Phase 5 info
- Updated `CHANGELOG.md`
- Testing report: "Phase 5 complete, all features working"
---

## Summary

### Before Refactoring
- main.py: ~3,000 lines
- Dead code: step1-7 functions, pipeline_state, duplicates
- Error handling: Inconsistent, many silent failures
- Type hints: Partial
- Documentation: Some inaccuracies

### After Refactoring (Phase 4)
- main.py: ~2,527 lines (organized with section markers)
- Dead code: None
- Error handling: Consistent, proper logging
- Type hints: 100% on public APIs
- Documentation: Accurate and complete
- Structure: Clear separation (controllers, modules, components)

### After Phase 5 (Target)
- main.py: ~400 lines (84% reduction from original)
- Views: 4 separate view files in src/views/
- Structure: Complete MVC separation (views, controllers, modules)

### Metrics

| Metric | Before | After Phase 4 | After Phase 5 (Target) | Total Improvement |
|--------|--------|---------------|------------------------|-------------------|
| main.py lines | ~3,000 | ~2,527 | ~400 | 87% reduction |
| Dead code | Yes | None | None | 100% removed |
| Type hints | Partial | 100% public | 100% public | Full coverage |
| Error handling | Inconsistent | Consistent | Consistent | Standardized |
| Documentation | Some errors | Accurate | Accurate | Updated |
| Structure | Monolithic | Controllers added | Full MVC | Complete separation |

### Risk Mitigation

**Backup Strategy**:
- Existing backup: `C:\Users\xhiep\Downloads\dubbing-extractor-backup-20260423_1630`
- Create new backup before each phase
- Keep incremental backups

**Testing Strategy**:
- Manual testing after each phase
- Full pipeline test after each phase
- Visual comparison for UI changes
- Config compatibility test

**Rollback Plan**:
- If phase fails: restore from backup
- If bug found: fix immediately or rollback
- Document any issues encountered

---

## Next Steps

**After Roadmap Approval**:
1. Review and approve this roadmap
2. Create backup before starting
3. Run `/gsd-plan-phase 1` to start Phase 1
4. Execute phases sequentially
5. Test thoroughly after each phase
6. Document any deviations or issues

**Future Work** (Out of Scope):
- Add threading/async for long operations
- Add automated tests (unit, integration)
- Complete step-by-step UI (if desired)
- Performance optimization
- Add more features
