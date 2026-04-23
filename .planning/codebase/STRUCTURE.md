---
type: codebase-map
focus: structure
created: 2026-04-23
---

# Directory Structure

## Root Directory

```
dubbing-extractor/
├── main.py                    # GUI entry point (~3,000 lines)
├── requirements.txt           # Python dependencies
├── config.json               # Runtime configuration (user settings)
├── cookies.txt               # yt-dlp authentication cookies
├── .env                      # Environment variables (not in git)
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation (English)
├── HUONG_DAN_SU_DUNG.md     # User guide (Vietnamese)
├── DESIGN.md                 # Design documentation
├── CLAUDE.md                 # Claude Code context
├── AGENTS.md                 # Agent configuration
├── CHECKLIST.md              # Development checklist
├── patch.txt, patch2.txt     # Code patches
├── dummy_in.mp4, dummy_out.mp4  # Test videos
└── *_REPORT.txt              # Test reports
```

## Source Code (`src/`)

```
src/
├── __init__.py
├── config.py                 # Configuration loader/saver
├── components/               # Custom Tkinter UI components
│   ├── __init__.py
│   ├── theme.py             # Theme system (colors, fonts, spacing)
│   ├── examples.py          # Component usage examples
│   ├── README.md            # Component documentation
│   ├── ui/                  # UI widgets
│   │   ├── __init__.py
│   │   ├── inputs.py        # Input, TextArea, Checkbox
│   │   ├── widgets.py       # Button, Label
│   │   └── display.py       # Display components
│   ├── layout/              # Layout containers
│   │   ├── __init__.py
│   │   └── containers.py    # Card, Section, Row, Column
│   └── hooks/               # State management
│       ├── __init__.py
│       └── state.py         # use_tk_state() hook
├── modules/                 # Business logic modules
│   ├── __init__.py
│   ├── workflow.py          # Main pipeline orchestration (~600 lines)
│   ├── downloader/          # Video download
│   │   ├── __init__.py
│   │   ├── platform_detector.py
│   │   ├── url_resolver.py
│   │   └── ytdlp_wrapper.py
│   ├── transcription/       # Speech-to-text & translation
│   │   ├── __init__.py
│   │   ├── whisper_engine.py
│   │   ├── translator.py
│   │   └── srt_generator.py
│   ├── video_processing/    # Video manipulation
│   │   ├── __init__.py
│   │   ├── ffmpeg_wrapper.py
│   │   ├── subtitle_detector.py
│   │   ├── subtitle_burner.py
│   │   └── video_encoder.py
│   └── tts/                 # Text-to-speech
│       ├── __init__.py
│       ├── vieneu_engine.py
│       └── audio_dubber.py
├── utils/                   # Utility functions
│   ├── file_utils.py
│   ├── text_utils.py
│   ├── runtime_env.py
│   └── suppress_warnings.py
└── types/                   # Type definitions (if any)
```

## Scripts (`scripts/`)

```
scripts/
├── installer.py             # Auto-installer (venv, ffmpeg, PyTorch)
├── install.bat              # Windows installer wrapper
├── run.bat                  # Launch script
└── system_check.py          # Environment validation
```

## Binary Dependencies (`bin/`)

```
bin/
└── ffmpeg/
    └── ffmpeg.exe           # Bundled ffmpeg binary
```

## Output Directory (`output/`)

```
output/
├── _temp/                   # Temporary processing files
│   ├── audio_goc.mp3
│   └── downloaded_video.*
├── {title}_{timestamp}/     # Per-video output folders
│   ├── audio_goc.mp3        # Original audio
│   ├── video_sach.mp4       # Clean video (subtitles covered)
│   ├── video_phu_de.mp4     # Video with burned subtitles
│   ├── video_long_tieng.mp4 # Final dubbed video
│   ├── phu_de_goc.srt       # Original subtitles
│   ├── phu_de_viet.srt      # Vietnamese subtitles
│   ├── phu_de_song_ngu.srt  # Bilingual subtitles
│   ├── script_goc.txt       # Original transcript
│   ├── script_viet.txt      # Vietnamese transcript
│   └── script_song_ngu.txt  # Bilingual transcript
└── app_debug.log            # Application logs
```

## Cache Directories

```
.cache/
├── huggingface/             # Hugging Face model cache
│   └── hub/
│       ├── models--pnnbao-ump--VieNeu-TTS/
│       ├── models--pnnbao-ump--VieNeu-TTS-v2-Turbo/
│       ├── models--neuphonic--distill-neucodec/
│       └── models--ntu-spml--distilhubert/
└── pip/                     # pip cache

.tmp/                        # Temporary files
└── tmp*.txt
```

## Virtual Environment (`venv/`)

```
venv/
├── Scripts/
│   ├── python.exe           # Python interpreter
│   ├── pip.exe              # Package manager
│   └── activate             # Activation script
└── Lib/                     # Installed packages
```

## Documentation (`docs/`)

```
docs/
├── START_HERE.txt           # Quick start guide
└── SUMMARY.txt              # Project summary
```

## Tests (`tests/`)

```
tests/
├── __init__.py
└── test_whisper_engine.py   # Whisper integration test
```

## Claude Code Configuration (`.claude/`)

```
.claude/
├── agents/                  # GSD agent definitions
│   ├── gsd-codebase-mapper.md
│   ├── gsd-planner.md
│   ├── gsd-executor.md
│   └── ... (17 agent files)
├── get-shit-done/           # GSD workflows
│   └── workflows/
│       └── map-codebase.md
├── gsd-file-manifest.json   # File manifest
└── package.json             # Claude package config
```

## Planning Directory (`.planning/`)

```
.planning/
└── codebase/                # Codebase mapping (this document set)
    ├── STACK.md
    ├── INTEGRATIONS.md
    ├── ARCHITECTURE.md
    ├── STRUCTURE.md         # (this file)
    ├── CONVENTIONS.md
    ├── TESTING.md
    └── CONCERNS.md
```

## Key File Locations

### Configuration
- `config.json` - user settings (source URL, models, subtitle params)
- `cookies.txt` - yt-dlp cookies
- `.env` - environment variables

### Entry Points
- `main.py` - GUI application
- `scripts/run.bat` - launch script
- `scripts/installer.py` - setup script

### Core Logic
- `src/modules/workflow.py` - pipeline orchestration
- `src/modules/transcription/whisper_engine.py` - speech recognition
- `src/modules/tts/vieneu_engine.py` - Vietnamese TTS
- `src/modules/video_processing/ffmpeg_wrapper.py` - video processing

### UI Components
- `src/components/ui/` - input widgets
- `src/components/layout/` - layout containers
- `src/components/theme.py` - styling

### External Binaries
- `bin/ffmpeg/ffmpeg.exe` - video/audio processing

### Output
- `output/{title}_{timestamp}/` - per-video results
- `output/app_debug.log` - application logs

## Naming Conventions

### Directories
- Lowercase with underscores: `video_processing/`, `tts/`
- Module names match directory names

### Python Files
- Lowercase with underscores: `whisper_engine.py`, `subtitle_burner.py`
- Descriptive names indicating purpose

### Output Files
- Vietnamese names: `phu_de_goc.srt`, `video_long_tieng.mp4`
- Timestamp format: `YYYYMMDD_HHMM`

### Temporary Files
- Prefix with `_temp` or `tmp`
- Cleaned up after processing (mostly)
