---
type: codebase-map
focus: testing
created: 2026-04-23
---

# Testing

## Test Coverage

**Minimal** - Only 1 test file with 2 test cases.

### Existing Tests

**tests/test_whisper_engine.py** (64 lines)
- Unit tests for Whisper transcription engine
- Uses `unittest` framework with mocking
- Tests:
  1. `test_transcribe_releases_model_after_success` - verifies model cleanup after transcription
  2. `test_transcribe_falls_back_to_cpu_on_cuda_oom` - verifies CPU fallback when CUDA OOM occurs

**test_suppress.py** (root directory)
- Tests warning suppression utility
- Not in `tests/` directory

## Test Framework

**unittest** (Python stdlib)
- Standard library testing framework
- No pytest or other third-party test frameworks
- `unittest.mock.patch` for mocking

## Test Structure

### Mocking Patterns

**Mock Objects**
- Custom mock classes: `_DummyModel` simulates Whisper model
- `unittest.mock.patch` for patching module-level objects
- Nested `with` statements for multiple patches

**Example**:
```python
class _DummyModel:
    def __init__(self, result):
        self.result = result
        self.moved_to_cpu = False

    def cpu(self):
        self.moved_to_cpu = True

    def transcribe(self, *_args, **_kwargs):
        return self.result
```

### Test Assertions
- `assertEqual()` - value comparison
- `assertIsNone()` - null checks
- `assertTrue()` - boolean checks

## Test Execution

**Manual**
- Run via: `python -m unittest tests.test_whisper_engine`
- No CI/CD integration
- No automated test runs

**No Test Runner Configuration**
- No pytest.ini
- No tox.ini
- No test discovery configuration

## Coverage Gaps

### Untested Modules

**Workflow** (`src/modules/workflow.py`)
- No tests for pipeline orchestration
- No tests for step functions (step1-7)
- No tests for timing adjustments
- No tests for memory management

**Downloader** (`src/modules/downloader/`)
- No tests for yt-dlp wrapper
- No tests for platform detection
- No tests for URL resolution

**Transcription** (`src/modules/transcription/`)
- ✅ Whisper engine has tests
- ❌ Translator has no tests
- ❌ SRT generator has no tests

**Video Processing** (`src/modules/video_processing/`)
- No tests for ffmpeg wrapper
- No tests for subtitle detection
- No tests for subtitle burning
- No tests for video encoding

**TTS** (`src/modules/tts/`)
- No tests for VieNeu engine
- No tests for audio dubbing

**UI Components** (`src/components/`)
- No tests for custom widgets
- No tests for layout containers
- No tests for theme system
- No tests for state hooks

**Utilities** (`src/utils/`)
- No tests for file utilities
- No tests for text utilities
- No tests for runtime environment

**Main Application** (`main.py`)
- No tests for GUI
- No tests for event handlers
- No tests for configuration

## Test Data

**No Test Fixtures**
- No sample videos
- No sample audio files
- No sample SRT files
- Tests use mocks instead of real data

**Dummy Files in Root**
- `dummy_in.mp4` (7.5 KB) - test input video
- `dummy_out.mp4` (41 KB) - test output video
- Not used by automated tests

## Integration Testing

**Manual Only**
- Full pipeline tested via GUI
- No automated integration tests
- No end-to-end test suite

**Test Reports** (manual testing artifacts)
- `TESTING_REPORT.txt` - manual test results
- `COMPREHENSIVE_TEST_REPORT.txt` - detailed manual test results

## Performance Testing

**None**
- No benchmarks
- No performance regression tests
- Memory monitoring in production code only (`_log_runtime_memory()`)

## Test Isolation

**Good Practices**
- Mocking external dependencies (Whisper model, CUDA)
- No file system writes in tests
- No network calls in tests

**Areas for Improvement**
- No test database/fixtures
- No cleanup/teardown patterns
- No test isolation for GUI components

## CI/CD

**None**
- No GitHub Actions
- No Jenkins
- No automated test runs on commit/PR
- No code coverage reporting

## Test Documentation

**Minimal**
- Test names are descriptive
- No docstrings in test methods
- No test plan documentation

## Mocking Strategy

### What Gets Mocked

**External Tools**
- Whisper model loading: `_load_model()`
- CUDA availability: `torch.cuda.is_available()`
- ffmpeg path: `LOCAL_FFMPEG`

**System Resources**
- GPU device: `torch.cuda.get_device_name()`
- CUDA cache: `torch.cuda.empty_cache()`

### What Doesn't Get Mocked

**Core Logic**
- Transcription result processing
- Model cleanup logic
- Error handling paths

## Test Maintenance

**Low Maintenance Burden**
- Only 2 test cases to maintain
- Tests are stable (no flaky tests reported)
- Mocks are simple and focused

**Risk**
- Low test coverage means bugs can slip through
- Refactoring is risky without safety net
- No regression detection

## Testing Philosophy

**Pragmatic Approach**
- Tests exist for critical path (Whisper transcription)
- Manual testing for GUI and integration
- Focus on shipping features over test coverage

**Trade-offs**
- Fast development velocity
- Higher risk of regressions
- Relies on manual QA

## Recommendations for Future

### High Priority
1. Add integration tests for full pipeline
2. Add tests for SRT generation (critical for output quality)
3. Add tests for subtitle timing adjustments (complex logic)

### Medium Priority
4. Add tests for ffmpeg wrapper (external dependency)
5. Add tests for translator (external API)
6. Add tests for video processing (complex operations)

### Low Priority
7. Add UI component tests (harder to test, lower risk)
8. Add performance benchmarks
9. Set up CI/CD pipeline

## Test Commands

**Run all tests**:
```bash
python -m unittest discover tests/
```

**Run specific test**:
```bash
python -m unittest tests.test_whisper_engine
```

**Run with verbose output**:
```bash
python -m unittest tests.test_whisper_engine -v
```

## Test Dependencies

**No Additional Test Dependencies**
- Uses stdlib `unittest`
- No pytest
- No coverage.py
- No test fixtures library
- No factory_boy or faker
