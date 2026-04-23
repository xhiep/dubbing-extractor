---
type: codebase-map
focus: architecture
created: 2026-04-23
---

# Architecture

## Pattern: Modular Pipeline with GUI Frontend

The application follows a **modular pipeline architecture** with clear separation between:
- GUI layer (Tkinter)
- Business logic (workflow orchestration)
- Domain modules (transcription, translation, video processing, TTS)
- Utilities (file handling, configuration)

## Layers

### 1. Presentation Layer

**main.py** (~3,000 lines)
- Tkinter GUI application
- Component-based UI using custom widgets
- State management via hooks pattern
- Event handlers for user interactions
- Progress callbacks to workflow layer

**Custom Component Library** (`src/components/`)
- `src/components/ui/` - Button, Input, Label, TextArea, Checkbox
- `src/components/layout/` - Card, Section, Row, Column
- `src/components/theme.py` - Theme system (colors, fonts, spacing)
- `src/components/hooks/state.py` - React-like state management for Tkinter

### 2. Workflow Orchestration Layer

**src/modules/workflow.py** (~600 lines)
- Main entry point: `process_video()` - full pipeline
- Step functions (new, partially implemented):
  - `step1_prepare()` - download/load video, extract audio
  - `step2_transcribe()` - Whisper transcription
  - `step3_translate()` - Google Translate
  - `step4_cover()` - detect and cover original subtitles
  - `step5_export()` - generate SRT files and scripts
  - `step6_burn()` - burn Vietnamese subtitles into video
  - `step7_dub()` - VieNeu-TTS dubbing
- Pipeline state management (in progress)
- Memory monitoring and cleanup
- Progress logging via callbacks

### 3. Domain Module Layer

**Downloader Module** (`src/modules/downloader/`)
- `platform_detector.py` - detect video platform (YouTube, Bilibili, etc.)
- `url_resolver.py` - resolve video URLs
- `ytdlp_wrapper.py` - yt-dlp integration, cookie handling

**Transcription Module** (`src/modules/transcription/`)
- `whisper_engine.py` - OpenAI Whisper integration (CPU-only)
- `translator.py` - Google Translate via deep-translator
- `srt_generator.py` - SRT file parsing and generation

**Video Processing Module** (`src/modules/video_processing/`)
- `ffmpeg_wrapper.py` - ffmpeg command builder, audio extraction, video probing
- `subtitle_detector.py` - OpenCV-based subtitle region detection
- `subtitle_burner.py` - burn subtitles into video with layout calculation
- `video_encoder.py` - render clean video with subtitle covering (blur/blackbar)

**TTS Module** (`src/modules/tts/`)
- `vieneu_engine.py` - VieNeu-TTS integration (GPU/CPU backends)
- `audio_dubber.py` - mix TTS audio with original video, volume control

### 4. Utility Layer

**Configuration** (`src/config.py`)
- Load/save `config.json`
- Global config object

**File Utilities** (`src/utils/file_utils.py`)
- Local file detection
- Directory creation

**Text Utilities** (`src/utils/text_utils.py`)
- Filename sanitization

**Runtime Environment** (`src/utils/runtime_env.py`)
- Environment setup and validation

**Warning Suppression** (`src/utils/suppress_warnings.py`)
- Filter stderr noise from dependencies

## Data Flow

```
User Input (GUI)
    ↓
main.py event handlers
    ↓
workflow.process_video() or step1-7 functions
    ↓
Domain modules (downloader, transcription, video_processing, tts)
    ↓
External tools (yt-dlp, ffmpeg, Whisper, VieNeu-TTS)
    ↓
Output files (video, audio, SRT, scripts)
    ↓
GUI updates (progress callbacks, log display)
```

## Pipeline Steps (7-Step Workflow)

1. **Prepare**: Download video (yt-dlp) or load local file → extract audio (ffmpeg)
2. **Transcribe**: Run Whisper on audio → get English segments with timestamps
3. **Translate**: Google Translate English → Vietnamese → apply timing adjustments
4. **Cover**: Detect original subtitle regions (OpenCV) → render video with blur/blackbar
5. **Export**: Generate SRT files (original, translated, bilingual) + text scripts
6. **Burn**: Burn Vietnamese subtitles into video (ffmpeg)
7. **Dub**: Synthesize Vietnamese speech (VieNeu-TTS) → mix with video audio

## Abstractions

### Callback Pattern
- All workflow functions accept `log_cb: Optional[Callable]` for progress updates
- GUI passes callback to display logs in real-time
- Enables decoupling of business logic from presentation

### Configuration Object
- Global `config` dict loaded from `config.json`
- Accessed throughout codebase via `from src.config import config`
- Saved on GUI changes

### Path Handling
- `pathlib.Path` used throughout
- Temp files in `output/_temp/`
- Final outputs in `output/{title}_{timestamp}/`

### Resource Management
- Explicit cleanup: `release_tts_resources()` after TTS
- Memory logging: `_log_runtime_memory()` tracks RAM and CUDA usage
- Garbage collection: `gc.collect()` after heavy operations

## Entry Points

**GUI Application**
- `main.py` - Tkinter GUI (primary entry point)
- Run via: `venv\Scripts\python.exe main.py` or `scripts\run.bat`

**CLI/Scripting** (potential, not implemented)
- `workflow.process_video()` can be called programmatically
- No CLI interface currently exists

## State Management

**GUI State**
- Tkinter variables (StringVar, BooleanVar, etc.)
- Custom hooks: `use_tk_state()` for React-like state management
- Config persistence via `config.json`

**Pipeline State** (in progress)
- `pipeline_state` dict to store intermediate results between steps
- Allows resuming from any step
- Not yet fully implemented

## Error Handling

- Try/except blocks in critical sections
- Fallback to ASCII encoding for Unicode errors in logs
- Graceful degradation (e.g., skip TTS if unavailable)
- User-facing error messages in GUI

## Concurrency

- Single-threaded (Tkinter main loop)
- Long-running operations block GUI (no threading/async yet)
- Progress updates via callbacks during blocking operations

## Testing

- Minimal test coverage
- `tests/test_whisper_engine.py` - Whisper integration test
- `test_suppress.py` - warning suppression test
- No unit tests for most modules
