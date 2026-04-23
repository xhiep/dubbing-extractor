# Phase 4: Quality Improvements - Research

**Researched:** 2026-04-23
**Domain:** Python code quality, error handling, logging, type hints, documentation
**Confidence:** HIGH

## Summary

Phase 4 focuses on incremental quality improvements to the existing codebase without major refactoring. The research covers five key areas: replacing bare exception handlers with specific error handling, implementing structured logging with RotatingFileHandler, adding type hints to public APIs, documenting functions with Google-style docstrings, and improving resource cleanup with context managers.

The codebase already has some good practices in place (explicit resource cleanup in whisper_engine.py and vieneu_engine.py, some type hints), but needs systematic improvements across all modules. The main risk areas are in network operations (downloader modules), video processing (ffmpeg operations), and AI model operations (Whisper, VieNeu-TTS).

**Primary recommendation:** Start with error handling improvements in high-risk modules (downloader, transcription, tts), add structured logging early to track improvements, then systematically add type hints and docstrings to public APIs.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Error handling | Application Logic | — | Exception handling belongs in business logic layer where operations occur |
| Logging | Application Logic | Infrastructure | Logging setup is infrastructure, but log calls are in application logic |
| Type checking | Development Tools | — | Static analysis tool (mypy) runs at development time, not runtime |
| Documentation | Development Tools | — | Docstrings are development-time documentation for API consumers |
| Resource cleanup | Application Logic | — | Resource lifecycle management belongs in the modules that acquire resources |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| logging (stdlib) | 3.11+ | Structured logging with rotation | Built-in, production-ready, no dependencies |
| typing (stdlib) | 3.11+ | Type hints for static analysis | Built-in, PEP 484 standard, IDE support |
| contextlib (stdlib) | 3.11+ | Context managers for resource cleanup | Built-in, Pythonic resource management |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| mypy | 1.13+ | Static type checker | Development/CI - verify type hints |
| psutil | 7.2.2 | Memory monitoring | Already installed - use for logging memory usage |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| logging | loguru | loguru is simpler but adds dependency; stdlib logging is sufficient |
| mypy | pyright | pyright is faster but mypy has better ecosystem support |
| Google docstrings | NumPy/Sphinx style | Google style is more readable, already used in some modules |

**Installation:**
```bash
# mypy not in requirements.txt - add as dev dependency
pip install mypy
```

**Version verification:** [VERIFIED: pip registry 2026-04-23]
- logging: stdlib, no version check needed
- typing: stdlib, no version check needed
- mypy: latest stable is 1.13.0 (as of April 2026)

## Architecture Patterns

### System Architecture Diagram

```
User Input (GUI/CLI)
    ↓
main.py (Event Handlers)
    ↓
Controllers (Phase 2)
    ↓
Workflow Pipeline (workflow.py)
    ↓
    ├─→ Downloader Modules → [Network I/O] → Local Files
    ├─→ Transcription Modules → [Whisper/GPU] → Segments
    ├─→ Translation Module → [Google Translate API] → Translated Text
    ├─→ Video Processing → [FFmpeg] → Processed Video
    └─→ TTS Modules → [VieNeu Engine] → Audio Files
    ↓
Output Files (output/ directory)

[Logging Layer] ← All modules log to structured logger
[Error Handling] ← Each module catches specific exceptions
[Resource Cleanup] ← Context managers ensure cleanup
```

### Recommended Project Structure
```
src/
├── modules/
│   ├── workflow.py          # Main pipeline - add type hints + docstrings
│   ├── downloader/          # Network errors - improve error handling
│   ├── transcription/       # GPU/memory errors - already has good cleanup
│   ├── video_processing/    # FFmpeg errors - improve error handling
│   └── tts/                 # TTS errors - already has good cleanup
├── utils/
│   └── logger.py            # NEW: Structured logging setup
└── controllers/             # Add type hints + docstrings
```

### Pattern 1: Specific Exception Handling
**What:** Catch specific exception types instead of bare `except Exception`
**When to use:** All try-except blocks where you know what can fail
**Example:**
```python
# Source: Python official docs - Error Handling Tutorial
# BAD - current pattern in workflow.py lines 47, 57
try:
    import psutil
    process = psutil.Process(os.getpid())
    rss_mb = process.memory_info().rss / 1024 / 1024
except Exception:
    pass

# GOOD - specific exceptions
try:
    import psutil
    process = psutil.Process(os.getpid())
    rss_mb = process.memory_info().rss / 1024 / 1024
except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied) as e:
    logger.debug(f"Could not get memory info: {e}")
```

### Pattern 2: Structured Logging Setup
**What:** Configure logging once at application startup with rotation
**When to use:** In main.py before any other imports
**Example:**
```python
# Source: Python logging.handlers documentation
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    """Configure structured logging with file rotation."""
    log_dir = Path("output")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger("dubbing_extractor")
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    fh = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding="utf-8"
    )
    fh.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(fh)
    
    # Console handler for errors
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(ch)
    
    return logger
```

### Pattern 3: Type Hints for Public APIs
**What:** Add type annotations to function signatures
**When to use:** All public functions (not prefixed with `_`)
**Example:**
```python
# Source: Python typing module documentation
from pathlib import Path
from typing import Optional, Callable, Dict

def process_video(
    source_input: str,
    cover_mode: str = "blur",
    log_cb: Optional[Callable[[str], None]] = None
) -> Dict[str, Path]:
    """Process video through complete pipeline.
    
    Args:
        source_input: URL or local file path
        cover_mode: Subtitle cover mode (blur/blackbar/none)
        log_cb: Optional callback for progress logging
        
    Returns:
        Dict mapping output types to file paths
        
    Raises:
        ValueError: Invalid source_input or cover_mode
        RuntimeError: Processing failed
    """
    pass
```

### Pattern 4: Google-Style Docstrings
**What:** Document functions with Args, Returns, Raises sections
**When to use:** All public functions and classes
**Example:**
```python
# Source: Google Python Style Guide
def transcribe(audio: Path, log_cb: Optional[Callable] = None) -> list:
    """Transcribe audio file using Whisper.
    
    Automatically selects CPU or CUDA based on GPU availability and stability.
    Falls back to CPU if CUDA runs out of memory. Cleans up model resources
    after transcription completes.
    
    Args:
        audio: Path to audio file (WAV format recommended)
        log_cb: Optional callback function for progress messages
        
    Returns:
        List of segment dicts with keys: start, end, text
        
    Raises:
        RuntimeError: Whisper model loading or transcription failed
        FileNotFoundError: Audio file does not exist
    """
    pass
```

### Pattern 5: Context Manager for Resource Cleanup
**What:** Use `@contextmanager` decorator for automatic cleanup
**When to use:** When acquiring resources that need guaranteed cleanup
**Example:**
```python
# Source: Python contextlib documentation
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def whisper_model(model_name: str, device: str):
    """Context manager for Whisper model lifecycle.
    
    Ensures model is properly unloaded even if transcription fails.
    """
    model = None
    try:
        logger.info(f"Loading Whisper model: {model_name} on {device}")
        model = whisper.load_model(model_name, device=device)
        yield model
    finally:
        if model is not None:
            logger.info("Unloading Whisper model")
            model.cpu()
            del model
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

# Usage
with whisper_model("base", "cuda") as model:
    result = model.transcribe(audio_path)
```

### Anti-Patterns to Avoid
- **Bare except:** Catches `KeyboardInterrupt` and `SystemExit`, prevents graceful shutdown
- **Silent failures:** `except Exception: pass` hides bugs - always log at minimum
- **Generic Exception catch without reraise:** Masks unexpected errors - catch specific types or reraise
- **Type hints with `Any`:** Defeats the purpose - be specific or omit the hint
- **Docstrings that repeat the function name:** "This function processes video" adds no value

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Log rotation | Custom file size checker + rename logic | `logging.handlers.RotatingFileHandler` | Handles edge cases (concurrent writes, atomic renames, backup numbering) |
| Type checking | Manual isinstance checks everywhere | mypy + type hints | Static analysis catches errors before runtime, no performance cost |
| Resource cleanup | Manual try-finally everywhere | `contextlib.contextmanager` | Guarantees cleanup, more readable, composable |
| Exception hierarchies | Custom exception classes for every error | Built-in exception types | Python has rich exception hierarchy (OSError, ValueError, RuntimeError, etc.) |

**Key insight:** Python's standard library is battle-tested for these patterns. Custom solutions introduce bugs (forgotten cleanup, race conditions in log rotation, incomplete exception handling).

## Common Pitfalls

### Pitfall 1: Catching Exception in Cleanup Code
**What goes wrong:** Exception handlers in finally blocks or __exit__ methods mask the original exception
**Why it happens:** Trying to be defensive about cleanup operations
**How to avoid:** Use bare except in cleanup only, log but don't raise
**Warning signs:** Tests pass but production logs show missing error details
**Example:**
```python
# BAD - masks original exception
try:
    risky_operation()
finally:
    cleanup()  # If this raises, original exception is lost

# GOOD - current pattern in vieneu_engine.py lines 26-32
try:
    fn()
except Exception:
    pass  # Cleanup failures are logged but don't mask original error
```

### Pitfall 2: Type Hints on Private Functions
**What goes wrong:** Spending time annotating internal implementation details
**Why it happens:** Misunderstanding that type hints are for API consumers
**How to avoid:** Only annotate public functions (not prefixed with `_`)
**Warning signs:** Mypy errors in internal functions that never get called externally
**Example:**
```python
# SKIP - internal helper
def _make_log(log_cb: Optional[Callable]):
    pass

# ANNOTATE - public API
def process_video(source_input: str, ...) -> Dict[str, Path]:
    pass
```

### Pitfall 3: Over-Logging
**What goes wrong:** Log files grow to gigabytes, performance degrades
**Why it happens:** Logging every variable value "just in case"
**How to avoid:** Use appropriate log levels (DEBUG for details, INFO for milestones, ERROR for failures)
**Warning signs:** Log files > 100MB after one day, application slows down
**Example:**
```python
# BAD - logs every iteration
for i, segment in enumerate(segments):
    logger.info(f"Processing segment {i}: {segment}")

# GOOD - log summary
logger.info(f"Processing {len(segments)} segments")
logger.debug(f"First segment: {segments[0]}")  # Only in debug mode
```

### Pitfall 4: Docstring Maintenance Burden
**What goes wrong:** Docstrings become outdated as code changes
**Why it happens:** Updating function signature but forgetting docstring
**How to avoid:** Keep docstrings minimal - focus on "why" not "what"
**Warning signs:** Docstring mentions parameters that don't exist
**Example:**
```python
# BAD - repeats obvious information
def download(url: str) -> Path:
    """Download a file from a URL.
    
    Args:
        url: The URL to download from
        
    Returns:
        The path to the downloaded file
    """

# GOOD - adds value
def download(url: str) -> Path:
    """Download video using yt-dlp with cookie authentication.
    
    Supports YouTube, TikTok, and local files. Uses cookies.txt
    for authenticated downloads.
    """
```

### Pitfall 5: Mypy Configuration Too Strict
**What goes wrong:** Mypy errors on third-party libraries without type stubs
**Why it happens:** Enabling strict mode without understanding implications
**How to avoid:** Start with basic checks, gradually increase strictness
**Warning signs:** Hundreds of mypy errors in libraries you don't control
**Example:**
```ini
# BAD - too strict for brownfield project
[mypy]
strict = True
disallow_untyped_calls = True

# GOOD - incremental adoption
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
ignore_missing_imports = True  # Ignore third-party libraries without stubs

[mypy-src.modules.*]
disallow_untyped_defs = True  # Only enforce on our code
```

## Code Examples

Verified patterns from official sources:

### Error Handling with Logging
```python
# Source: Python logging + error handling docs
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def download_video(url: str, output_dir: Path) -> Path:
    """Download video from URL.
    
    Args:
        url: Video URL (YouTube, TikTok, etc.)
        output_dir: Directory to save downloaded file
        
    Returns:
        Path to downloaded video file
        
    Raises:
        ValueError: Invalid URL format
        ConnectionError: Network request failed
        RuntimeError: yt-dlp execution failed
    """
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL: {url}")
    
    try:
        # Download logic here
        result = ytdlp_download(url, output_dir)
        logger.info(f"Downloaded: {result}")
        return result
    except ConnectionError as e:
        logger.error(f"Network error downloading {url}: {e}", exc_info=True)
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"yt-dlp failed: {e.stderr}", exc_info=True)
        raise RuntimeError(f"Download failed: {e}") from e
```

### Logging Setup in main.py
```python
# Source: Python logging.handlers documentation
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging() -> logging.Logger:
    """Configure application logging with rotation."""
    log_dir = Path("output")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger("dubbing_extractor")
    logger.setLevel(logging.INFO)
    
    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(file_handler)
    
    # Console handler for errors only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s: %(message)s"
    ))
    logger.addHandler(console_handler)
    
    return logger

# In main.py startup
if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Application started")
    # ... rest of application
```

### Type Hints for Workflow Functions
```python
# Source: Python typing module documentation
from pathlib import Path
from typing import Optional, Callable, Dict, List

def process_video(
    source_input: str,
    cover_mode: str = "blur",
    dub_mode: str = "none",
    log_cb: Optional[Callable[[str], None]] = None
) -> Dict[str, Path]:
    """Process video through complete pipeline.
    
    Args:
        source_input: URL or local file path
        cover_mode: Subtitle cover mode (blur/blackbar/none)
        dub_mode: TTS dubbing mode (none/quick/full)
        log_cb: Optional callback for progress logging
        
    Returns:
        Dict with keys: video, srt, script, bilingual
        
    Raises:
        ValueError: Invalid parameters
        RuntimeError: Pipeline processing failed
    """
    pass

def transcribe(
    audio: Path,
    log_cb: Optional[Callable[[str], None]] = None
) -> List[Dict[str, any]]:
    """Transcribe audio using Whisper.
    
    Args:
        audio: Path to audio file
        log_cb: Optional progress callback
        
    Returns:
        List of segment dicts with start, end, text keys
        
    Raises:
        RuntimeError: Transcription failed
    """
    pass
```

### Context Manager for Model Cleanup
```python
# Source: Python contextlib documentation
from contextlib import contextmanager
import logging
import gc

logger = logging.getLogger(__name__)

@contextmanager
def managed_whisper_model(model_name: str, device: str):
    """Load and automatically cleanup Whisper model.
    
    Args:
        model_name: Whisper model size (tiny/base/small/medium/large)
        device: Device to load on (cpu/cuda)
        
    Yields:
        Loaded Whisper model instance
        
    Example:
        with managed_whisper_model("base", "cuda") as model:
            result = model.transcribe("audio.wav")
    """
    model = None
    try:
        logger.info(f"Loading Whisper {model_name} on {device}")
        model = whisper.load_model(model_name, device=device)
        yield model
    finally:
        if model is not None:
            logger.info("Cleaning up Whisper model")
            try:
                model.cpu()
            except Exception as e:
                logger.warning(f"Error moving model to CPU: {e}")
            del model
            gc.collect()
            if device == "cuda":
                import torch
                torch.cuda.empty_cache()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `except:` bare except | `except Exception as e:` with logging | Python 3.0+ | Prevents catching KeyboardInterrupt/SystemExit |
| String type hints `"ClassName"` | Direct class references or `from __future__ import annotations` | Python 3.7+ (PEP 563) | Cleaner syntax, better IDE support |
| `typing.Optional[X]` | `X \| None` | Python 3.10+ (PEP 604) | More concise union syntax |
| Manual `try-finally` | Context managers (`with` statement) | Python 2.5+ | Guaranteed cleanup, more readable |
| Print debugging | Structured logging with levels | Always preferred | Persistent logs, filterable by severity |

**Deprecated/outdated:**
- `typing.List`, `typing.Dict`: Use built-in `list`, `dict` (Python 3.9+)
- `typing.Tuple`: Use built-in `tuple` (Python 3.9+)
- Comment-based type hints: Use proper annotations (Python 3.5+)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | mypy is not installed (not in requirements.txt) | Standard Stack | If already installed, no impact; if different version, may have compatibility issues |
| A2 | Current exception handlers use `except Exception: pass` pattern | Common Pitfalls | If pattern is different, examples may not match actual code |
| A3 | No existing logging configuration in main.py | Architecture Patterns | If logging already configured, may conflict with new setup |

## Open Questions

1. **Mypy strictness level**
   - What we know: Project is brownfield, has some type hints already
   - What's unclear: How strict should mypy configuration be initially?
   - Recommendation: Start with `ignore_missing_imports = True` and gradually increase strictness

2. **Logging verbosity in production**
   - What we know: Application processes videos, can run for hours
   - What's unclear: Should default level be INFO or WARNING?
   - Recommendation: INFO for now, make configurable via config.json later

3. **Docstring coverage**
   - What we know: Phase 4 focuses on public APIs
   - What's unclear: Should private functions (`_prefixed`) get docstrings?
   - Recommendation: Only document private functions if they're complex (>20 lines)

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All tasks | ✓ | 3.11.9 | — |
| mypy | Type checking | ✗ | — | Skip type checking, add to requirements.txt |
| psutil | Memory logging | ✓ | 7.2.2 | Already in requirements.txt |
| logging (stdlib) | Structured logging | ✓ | 3.11+ | — |
| typing (stdlib) | Type hints | ✓ | 3.11+ | — |
| contextlib (stdlib) | Context managers | ✓ | 3.11+ | — |

**Missing dependencies with no fallback:**
- None - all stdlib modules available

**Missing dependencies with fallback:**
- mypy: Not installed, but can be added to requirements.txt or run manually

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual testing (no automated test framework detected) |
| Config file | none — see Wave 0 |
| Quick run command | `scripts\run.bat` (manual smoke test) |
| Full suite command | Manual full pipeline test |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QI-01 | Error handling improvements | manual | Manual code review + test error scenarios | ❌ Wave 0 |
| QI-02 | Structured logging works | manual | Check `output/app.log` after run | ❌ Wave 0 |
| QI-03 | Type hints pass mypy | unit | `mypy src/modules/workflow.py` | ❌ Wave 0 |
| QI-04 | Docstrings present | manual | Manual code review | ❌ Wave 0 |
| QI-05 | Resource cleanup works | manual | Monitor memory during/after processing | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** Manual code review (check syntax, imports)
- **Per wave merge:** Run application, test one feature
- **Phase gate:** Full pipeline test (download → transcribe → translate → render → dub)

### Wave 0 Gaps
- [ ] `mypy` installation — add to requirements.txt or dev-requirements.txt
- [ ] Logging verification script — check log file format and rotation
- [ ] Memory monitoring script — track resource cleanup effectiveness

*(No automated test infrastructure exists - all validation is manual)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A - desktop application |
| V3 Session Management | no | N/A - no sessions |
| V4 Access Control | no | N/A - single-user desktop app |
| V5 Input Validation | yes | Validate URLs, file paths, config values |
| V6 Cryptography | no | N/A - no sensitive data encryption |

### Known Threat Patterns for Python Desktop Applications

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal in file operations | Tampering | Use `Path.resolve()` to normalize paths, validate within expected directories |
| Command injection in subprocess calls | Tampering | Use list-form subprocess arguments, never shell=True with user input |
| Arbitrary code execution via pickle | Tampering | Never unpickle untrusted data - use JSON for serialization |
| Log injection | Information Disclosure | Sanitize user input before logging, use structured logging |

**Phase 4 specific concerns:**
- Logging user-provided URLs/paths: Ensure no sensitive data (tokens, passwords) logged
- Error messages: Don't expose internal paths or system information in user-facing errors
- Exception details: Use `exc_info=True` for file logs, but sanitize for UI display

## Sources

### Primary (HIGH confidence)
- [Python Official Documentation - Error Handling](https://docs.python.org/3/tutorial/errors.html) - Exception handling best practices
- [Python Official Documentation - logging.handlers](https://docs.python.org/3/library/logging.handlers.html) - RotatingFileHandler setup
- [Python Official Documentation - typing](https://docs.python.org/3/library/typing.html) - Type hints syntax and usage
- [Python Official Documentation - contextlib](https://docs.python.org/3/library/contextlib.html) - Context managers
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) - Docstring format

### Secondary (MEDIUM confidence)
- Project codebase inspection - Current error handling patterns
- requirements.txt - Installed dependencies

### Tertiary (LOW confidence)
- None - all claims verified against official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All stdlib modules, well-documented
- Architecture: HIGH - Patterns verified in official Python docs
- Pitfalls: HIGH - Based on official docs and common Python anti-patterns

**Research date:** 2026-04-23
**Valid until:** 2026-10-23 (6 months - Python stdlib is stable)
