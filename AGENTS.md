# AGENTS.md
> File nay duoc doc boi Codex CLI va cac AI agent khac.
> Mo ta cau truc, quy tac, va context de agent lam viec dung.

---

## Tong quan Project

**Dubbing Extractor v2** - Tool tu dong:
1. Tai video tu Douyin/Bilibili/YouTube
2. Transcribe audio bang Whisper
3. Dich sang tieng Viet
4. Che sub cu (neu co)
5. Ghi sub moi vao video

**Tech Stack**:
- Python 3.11+
- PyTorch (CUDA support)
- Whisper (OpenAI)
- FFmpeg (NVENC GPU encoding)
- yt-dlp
- Tkinter (GUI)

---

## Cau truc thu muc

```
dubbing-extractor-v2/
├── .env.example          # Template bien moi truong
├── .gitignore
├── AGENTS.md             # File nay
├── README.md
├── config.json           # App state (GUI settings)
├── cookies.txt           # Cookies cho yt-dlp
│
├── src/
│   ├── __init__.py
│   ├── main.py           # Entry point - GUI
│   ├── main_original.py  # Original monolithic file (reference)
│   ├── config.py         # Configuration management
│   │
│   ├── modules/
│   │   ├── downloader/
│   │   │   ├── platform_detector.py  # Detect platform from URL
│   │   │   ├── url_resolver.py       # Resolve short URLs
│   │   │   └── ytdlp_wrapper.py      # yt-dlp integration
│   │   │
│   │   ├── transcription/
│   │   │   ├── whisper_engine.py     # Whisper transcription
│   │   │   └── translator.py         # Google Translate
│   │   │
│   │   ├── video_processing/
│   │   │   ├── ffmpeg_wrapper.py     # FFmpeg operations
│   │   │   ├── subtitle_detector.py  # Detect old subs
│   │   │   ├── video_encoder.py      # NVENC encoding
│   │   │   └── subtitle_burner.py    # Burn subs to video
│   │   │
│   │   └── gui/
│   │       └── app_window.py         # Tkinter GUI
│   │
│   ├── utils/
│   │   ├── logger.py         # Logging utilities
│   │   ├── file_utils.py     # File operations
│   │   └── text_utils.py     # Text processing
│   │
│   └── types/
│       └── models.py         # Data classes
│
├── scripts/
│   ├── installer.py      # Setup dependencies
│   ├── install.bat       # Windows installer
│   ├── run.bat           # Run app
│   └── system_check.py   # Verify installation
│
├── tests/
│   └── (test files)
│
├── docs/
│   ├── README_GPU.md     # GPU optimization guide
│   ├── SUMMARY.txt       # Quick summary
│   └── START_HERE.txt    # Quick start guide
│
├── data/                 # Static data
├── output/               # Generated videos (gitignored)
├── bin/                  # FFmpeg binaries
└── venv/                 # Virtual environment (gitignored)
```

---

## Quy tac code

### General
- Khong hardcode secret, API key, password - dung .env
- Moi file chi lam 1 viec (Single Responsibility)
- Ham dai hon 50 dong -> can nhac tach nho
- Comment tieng Viet OK, nhung ten bien/ham PHAI tieng Anh

### Naming
- File: `snake_case.py`
- Class: `PascalCase`
- Function/variable: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Tranh ten mo ho: `data`, `info`, `stuff`, `temp`

### Error handling
- Khong dung bare `except:`
- Log loi du context: function name, input, error message
- Tra ve loi co cau truc nhat quan

### Import
- Group: stdlib -> third-party -> local (cach nhau 1 dong)
- Khong import wildcard: `from module import *`

---

## Files Agent KHONG duoc sua

```
.env
*.secret
config.json           # Chi doc, khong sua truc tiep
cookies.txt           # User-provided
venv/
bin/
output/
```

---

## Workflow chuan khi Agent lam task

1. **Doc file lien quan truoc** - khong doan mo
2. **Plan ro** - se sua file nao, them gi, xoa gi
3. **Code** - theo dung cau truc va naming
4. **Tu test** - chay lenh test hoac tu kiem tra logic
5. **Bao cao** - da lam gi, con van de gi khong

---

## Chay project

```bash
# Cai dependencies (lan dau)
scripts\install.bat

# Chay app
scripts\run.bat

# Kiem tra he thong
venv\Scripts\python.exe scripts\system_check.py
```

---

## Bien moi truong

Xem `.env.example` de biet can set gi. Copy va dien:
```bash
cp .env.example .env
```

Key quan trong:
```
WHISPER_MODEL=base      # tiny, base, small, medium, large
TARGET_LANGUAGE=vi      # Ngon ngu dich
OUTPUT_DIR=output       # Thu muc output
```

---

## Ghi chu cho Agent

### Project context
- **Muc dich**: Tu dong dubbing video tu Douyin/Bilibili sang tieng Viet
- **Doi tuong**: Content creator, translator
- **Phan phuc tap**: 
  - Whisper transcription (CPU only - RTX 5060 chua ho tro)
  - NVENC encoding (GPU - hoat dong tot)
  - yt-dlp cookies handling
  - Subtitle detection va removal

### Luu y quan trong
- **GPU**: RTX 5060 (sm_120) - PyTorch chua ho tro day du
- **Whisper**: Force CPU de tranh loi CUDA
- **NVENC**: Hoat dong tot, 3-5x nhanh hon CPU
- **Config**: Dung config.py thay vi hardcode

### Neu khong chac -> hoi truoc, dung tu doan

---

## Module Dependencies

```
src/main.py
  -> modules/gui/app_window.py
  -> modules/downloader/ytdlp_wrapper.py
  -> modules/transcription/whisper_engine.py
  -> modules/video_processing/video_encoder.py
  -> config.py
  -> utils/*
```

---

**Last updated**: 2026-04-22
**Refactored**: From monolithic main.py (2358 lines) to modular structure
