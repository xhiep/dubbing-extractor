# Dubbing Extractor v2

Tu dong tai video, transcribe, dich, che sub cu, ghi phu de va long tieng tieng Viet.

## Tinh nang

- Tai video tu Douyin, Bilibili, YouTube
- Transcribe audio bang Whisper (OpenAI)
- Dich sang tieng Viet tu dong
- Phat hien va che sub cu
- Ghi sub moi vao video
- Long tieng tieng Viet bang VieNeu-TTS
- Clone giong tu file audio mau va nghe thu truc tiep trong UI
- GPU acceleration (NVENC encoding)

## Cai dat

### Yeu cau

- Windows 10/11
- Python 3.11+
- NVIDIA GPU (optional, cho NVENC encoding)
- 8GB RAM (16GB recommended cho Whisper large)

### Cai dat nhanh

```bash
# Chay installer
scripts\install.bat
```

Installer se:
1. Tao virtual environment trong `venv/`
2. Tai FFmpeg static build
3. Cai cac package Python (yt-dlp, whisper, deep-translator, vieneu)
4. Cai PyTorch voi CUDA support (~2.5GB)
5. Giu pip cache, HuggingFace cache, torch cache va temp trong ngay thu muc project

## Su dung

### Chay app

```bash
scripts\run.bat
```

### Kiem tra he thong

```bash
venv\Scripts\python.exe scripts\system_check.py
```

## Cau truc Project

```
dubbing-extractor-v2/
├── src/                  # Source code (modular structure)
├── scripts/              # Installation and run scripts
├── docs/                # Documentation
├── tests/               # Test files
├── venv/                # Virtual environment (auto-created)
├── bin/                 # FFmpeg binaries (auto-downloaded)
├── output/              # Generated videos
├── config.json          # App configuration
└── cookies.txt          # yt-dlp cookies
```

Xem [AGENTS.md](AGENTS.md) de biet chi tiet cau truc.

## Cau hinh

### Bien moi truong (.env)

Copy `.env.example` thanh `.env` va chinh sua:

```bash
WHISPER_MODEL=base      # tiny, base, small, medium, large
TARGET_LANGUAGE=vi      # Ngon ngu dich
OUTPUT_DIR=output       # Thu muc output
DUB_MODE=preset         # preset | clone
DUB_SOURCE_VOLUME=0.18  # Muc am thanh goc khi long tieng
DUB_MIX_MODE=nen_nho    # nen_nho | tat_goc
```

### Whisper Models

| Model  | Size | Speed | Quality |
|--------|------|-------|----------|
| tiny   | 39M  | ~10x  | Low     |
| base   | 74M  | ~5x   | Good    |
| small  | 244M | ~2x   | Better  |
| medium | 769M | ~1x   | Great   |
| large  | 1.5G | ~0.5x | Best    |

## GPU Support

### NVENC Encoding

- **Supported**: NVIDIA GPU voi NVENC
- **Performance**: 3-5x nhanh hon CPU encoding
- **Auto fallback**: Tu dong chuyen sang CPU neu NVENC loi

### Whisper Transcription

- **Current**: Chay tren CPU
- **Reason**: RTX 5060 (sm_120) chua duoc PyTorch ho tro day du
- **Performance**: Van rat nhanh tren CPU

Xem [docs/README_GPU.md](docs/README_GPU.md) de biet chi tiet.

## Troubleshooting

### Whisper qua cham

Giam model size trong config.json:
- `large` -> `medium` (nhanh 2x)
- `medium` -> `small` (nhanh 2x)
- `small` -> `base` (nhanh 2x)

### NVENC encoding loi

App tu dong fallback ve CPU encoding (libx264).

### Loi tai video

Kiem tra cookies.txt:
1. Dang nhap vao website (Douyin/Bilibili)
2. Export cookies bang extension (EditThisCookie)
3. Luu vao `cookies.txt`

## Development

### Cau truc Code

Project dang duoc refactor tu monolithic (2358 lines) sang modular structure:

- `src/modules/downloader/` - Video download
- `src/modules/transcription/` - Whisper + translation
- `src/modules/video_processing/` - FFmpeg operations
- `src/modules/tts/` - VieNeu-TTS + ghep audio long tieng
- `src/utils/` - Utilities
- `src/config.py` - Configuration management

Xem [AGENTS.md](AGENTS.md) de biet quy tac code.

### Chay Tests

```bash
venv\Scripts\python.exe -m pytest tests/
```

## Credits

- **Whisper**: OpenAI
- **yt-dlp**: yt-dlp team
- **FFmpeg**: FFmpeg team
- **Deep Translator**: deep-translator
- **VieNeu-TTS**: pnnbao97 / VieNeu

## License

MIT License

## Changelog

### v2.4 (2026-04-22)

- Refactored to modular structure
- Added GPU optimization (NVENC)
- Added virtual environment support
- Improved configuration management
- Updated documentation

### v2.5 (2026-04-22)

- Added VieNeu-TTS integration for Vietnamese dubbing
- Added preset voice and clone-from-audio workflow
- Added TTS preview controls in UI
- Blur timing now follows subtitle timing after translation
- Preview now reads render metadata to better match output subtitle position

### v2.3

- Removed TTS features
- Added smart subtitle covering
- Improved UI

---

**Quick Start**: `scripts\install.bat` -> `scripts\run.bat`

**Documentation**: See `docs/` folder

**Support**: Check [docs/START_HERE.txt](docs/START_HERE.txt)
