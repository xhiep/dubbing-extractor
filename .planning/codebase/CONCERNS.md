---
type: codebase-map
focus: concerns
created: 2026-04-23
---

# Technical Debt & Concerns

## Work In Progress

### Step-by-Step Pipeline UI (Incomplete)

**Status**: Partially implemented, not yet functional

**What's Done**:
- Step functions created in `src/modules/workflow.py`:
  - `step1_prepare()` - download/extract audio ✅
  - `step2_transcribe()` - Whisper transcription ✅
  - `step3_translate()` - translation ✅
  - `step4_cover()` - subtitle covering ✅
  - `step5_export()` - SRT/script export ✅
  - `step6_burn()` - burn subtitles ✅
  - `step7_dub()` - TTS dubbing ✅

**What's Missing**:
- UI buttons in `main.py` for step-by-step execution (Bước 1-7)
- SRT editor widget after step 3 (edit translated subtitles)
- `pipeline_state` dict to persist state between steps
- Button to open SRT in external editor
- Save edited SRT back to pipeline
- Remove duplicate TTS checkbox (`quick_dub_toggle` lines 196-209 in main.py)

**Context**: 
- Backup exists at `C:\Users\xhiep\Downloads\dubbing-extractor-backup-20260423_1630`
- User wants to run pipeline incrementally, edit SRT mid-process, then continue

**Risk**: Medium - feature half-implemented, may confuse users if exposed

## Hardware Limitations

### RTX 5060 (Blackwell sm_120) Compatibility

**Issue**: PyTorch stable doesn't support sm_120 architecture yet

**Impact**:
- Whisper transcription runs on CPU only (slow)
- TTS can use GPU (works with nightly PyTorch)
- NVENC video encoding works fine

**Workaround**: 
- PyTorch nightly installed via `scripts/installer.py`
- CPU transcription acceptable for now
- User aware of limitation (documented in CLAUDE.md)

**Risk**: Low - documented, workaround in place

## ffmpeg Path Handling

### Non-Standard ffmpeg Location

**Issue**: ffmpeg not in system PATH, bundled at `bin/ffmpeg/ffmpeg.exe`

**Workaround**: PowerShell wrapper for every ffmpeg call
```python
powershell.exe -Command "& 'C:\Users\xhiep\Downloads\dubbing-extractor\bin\ffmpeg\ffmpeg.exe' ..."
```

**Concerns**:
- Verbose command construction
- PowerShell overhead on every call
- Harder to debug ffmpeg errors
- Path hardcoded in multiple places

**Risk**: Low - works reliably, but inelegant

## GUI Architecture

### Monolithic main.py

**Issue**: `main.py` is ~3,000 lines, contains entire GUI

**Concerns**:
- Hard to navigate
- Mixing presentation and business logic
- Event handlers tightly coupled to UI
- Difficult to test
- Long file load time

**Mitigation**:
- Custom component library helps (`src/components/`)
- Business logic extracted to `src/modules/`
- But GUI code still monolithic

**Risk**: Medium - maintainability issue, refactoring would be large effort

### No Threading/Async

**Issue**: Long operations block GUI (Tkinter main loop)

**Impact**:
- GUI freezes during transcription (minutes)
- GUI freezes during video encoding
- No cancel button during operations
- Poor user experience

**Workaround**: Progress callbacks update GUI during blocking operations

**Risk**: Medium - UX issue, but functional

## Test Coverage

### Minimal Testing

**Issue**: Only 2 unit tests, no integration tests

**Coverage**:
- ✅ Whisper engine (2 tests)
- ❌ Workflow pipeline (0 tests)
- ❌ Video processing (0 tests)
- ❌ TTS (0 tests)
- ❌ GUI (0 tests)
- ❌ Downloader (0 tests)

**Risk**: High - regressions likely, refactoring dangerous

**Mitigation**: Manual testing via GUI

## External Dependencies

### Google Translate Reliability

**Issue**: Using unofficial Google Translate endpoint via `deep-translator`

**Concerns**:
- No API key, may break if Google changes endpoint
- Rate limiting possible
- No error handling for translation failures
- No fallback translation service

**Risk**: Medium - translation is core feature, no backup plan

### yt-dlp Platform Support

**Issue**: Relies on yt-dlp for video downloads

**Concerns**:
- Platforms change APIs frequently (YouTube, Bilibili)
- yt-dlp needs regular updates
- Cookie authentication may break
- No fallback downloader

**Risk**: Medium - download is first step, failure blocks entire pipeline

## Memory Management

### Model Loading

**Issue**: Whisper and VieNeu models loaded into RAM/VRAM

**Concerns**:
- Large models (Whisper large ~3GB, VieNeu ~1GB)
- No model unloading between operations (except explicit cleanup)
- Memory leaks possible with repeated operations
- CUDA memory not always freed

**Mitigation**:
- `release_tts_resources()` after TTS
- `gc.collect()` after heavy operations
- Memory logging: `_log_runtime_memory()`

**Risk**: Low - cleanup exists, but could be more aggressive

## Configuration Management

### config.json Persistence

**Issue**: All settings in single JSON file

**Concerns**:
- No schema validation
- Manual editing can break app
- No migration strategy for config changes
- Sensitive data (API keys) in plain text

**Risk**: Low - simple app, but could improve

## Error Handling

### Inconsistent Error Handling

**Issue**: Mix of try/except patterns, some errors silently swallowed

**Examples**:
- Log rotation errors: `except Exception: pass`
- Unicode errors: fallback to ASCII
- Some operations have no error handling

**Concerns**:
- Silent failures hard to debug
- User may not know operation failed
- No error reporting/telemetry

**Risk**: Medium - debugging difficult, user confusion

## Code Quality

### Mixed Language Comments

**Issue**: Comments in Vietnamese, code in English

**Impact**:
- Non-Vietnamese speakers can't read comments
- AI tools may struggle with Vietnamese
- Inconsistent with international open source norms

**Mitigation**: Code names are English, so logic is readable

**Risk**: Low - documented convention, user preference

### No Type Checking

**Issue**: Type hints present but not enforced

**Concerns**:
- No mypy or pyright in workflow
- Type errors only caught at runtime
- Refactoring riskier without type safety

**Risk**: Low - Python norm, but could improve

## Security

### Cookie Storage

**Issue**: `cookies.txt` in plain text

**Concerns**:
- Contains authentication cookies for YouTube/Bilibili
- Stored unencrypted
- Committed to git if user not careful (in .gitignore, but risky)

**Risk**: Low - local app, but user should be aware

### No Input Validation

**Issue**: User inputs not validated before processing

**Examples**:
- URL validation minimal
- File path validation minimal
- Numeric inputs not range-checked in GUI

**Risk**: Low - crashes possible but not security critical

## Performance

### CPU-Only Whisper

**Issue**: Whisper on CPU is slow (minutes for long videos)

**Impact**:
- Poor UX for long videos
- No progress indication during transcription
- Users may think app crashed

**Mitigation**: Progress callbacks show activity

**Risk**: Medium - UX issue, hardware limitation

### No Caching

**Issue**: No caching of intermediate results

**Examples**:
- Re-transcribe if user re-runs pipeline
- Re-download if user re-runs with same URL
- No subtitle detection cache

**Risk**: Low - not a common use case

## Documentation

### Outdated Line Counts

**Issue**: CLAUDE.md says `main.py` is ~1760 lines, actually ~3,000 lines

**Risk**: Very Low - documentation drift, easy to fix

### No API Documentation

**Issue**: No docstring documentation for public APIs

**Concerns**:
- Hard for new developers to understand
- No auto-generated docs (Sphinx, etc.)

**Risk**: Low - small project, code is readable

## Deployment

### No Installer

**Issue**: `scripts/installer.py` exists but requires manual setup

**Concerns**:
- User must have Python 3.11 installed
- User must run installer script
- No single-click installer (exe, msi)
- No auto-update mechanism

**Risk**: Low - target users are technical

## Known Bugs

### None Reported

- CHECKLIST.md shows all critical bugs fixed as of 2026-04-22
- No open bug reports in documentation
- No GitHub issues (not a GitHub project)

## Technical Debt Summary

### High Priority
1. Complete step-by-step pipeline UI (work in progress)
2. Add integration tests for full pipeline
3. Improve error handling and user feedback

### Medium Priority
4. Add threading/async for long operations
5. Refactor monolithic `main.py`
6. Add input validation
7. Improve memory management

### Low Priority
8. Add type checking (mypy)
9. Generate API documentation
10. Add caching for intermediate results
11. Create single-click installer

## Fragile Areas

### Subtitle Detection (OpenCV)

**Location**: `src/modules/video_processing/subtitle_detector.py`

**Concerns**:
- Heuristic-based detection (edge detection, contours)
- May fail on unusual subtitle styles
- No machine learning, just image processing
- Sensitive to video quality

**Risk**: Medium - core feature, but works for common cases

### Timing Adjustments

**Location**: `src/modules/workflow.py` - `_apply_subtitle_timing()`

**Concerns**:
- Complex math: `effective_scale = scale / speed`
- Easy to introduce off-by-one errors
- No unit tests for timing logic

**Risk**: Medium - subtle bugs hard to detect

### ffmpeg Command Construction

**Location**: `src/modules/video_processing/ffmpeg_wrapper.py`

**Concerns**:
- String concatenation for commands
- Shell injection possible if inputs not sanitized
- Complex filter graphs hard to debug

**Risk**: Low - inputs controlled by app, not user

## Dependencies at Risk

### Outdated Soon
- PyTorch nightly (unstable, frequent changes)
- yt-dlp (needs frequent updates for platform changes)
- Whisper (OpenAI may deprecate local version)

### Stable
- Tkinter (stdlib, very stable)
- ffmpeg (mature, stable)
- Most other dependencies

## Maintenance Burden

**Overall**: Low to Medium
- Small codebase (~5,000 lines)
- Few external dependencies
- No database, no server
- Local-only app

**Risks**:
- Platform API changes (YouTube, Bilibili)
- PyTorch compatibility issues
- Whisper model updates
