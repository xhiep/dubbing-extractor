# Dubbing Extractor v2 — Claude Context

## Khởi động Claude
```
cd C:\Users\xhiep\Downloads\dubbing-extractor
claude --dangerously-skip-permissions
```

## Chạy app
```
scripts\run.bat
# hoặc trực tiếp:
venv\Scripts\python.exe main.py
```

## ffmpeg
- Không có ffmpeg trong PATH hệ thống
- ffmpeg nằm tại: `C:\Users\xhiep\Downloads\dubbing-extractor\bin\ffmpeg\ffmpeg.exe`
- Dùng PowerShell để gọi: `powershell.exe -Command "& 'C:\Users\xhiep\Downloads\dubbing-extractor\bin\ffmpeg\ffmpeg.exe' ..."`

## Cấu trúc chính
- `main.py` — entry point + toàn bộ GUI (Tkinter, ~2,522 dòng, organized with section markers)
- `src/modules/workflow.py` — pipeline xử lý video (download → transcribe → translate → render, ~567 dòng)
- `src/modules/tts/` — VieNeu-TTS lồng tiếng tiếng Việt
- `src/components/` — custom UI components (Card, Button, Input, TextArea...)
- `src/controllers/` — event handlers (Phase 2 extraction)
- `src/utils/ui_helpers.py` — pure UI geometry helper functions (Phase 3 extraction)
- `src/utils/logger.py` — structured logging with rotation (Phase 4)

## Pipeline workflow (process_video)
Bước 1: Tải video (yt-dlp) hoặc dùng file local
Bước 2: Transcribe (Whisper, chạy CPU — RTX 5060 chưa được PyTorch hỗ trợ)
Bước 3: Dịch sang tiếng Việt (Google Translate)
Bước 4: Che phụ đề gốc (blur/blackbar/none)
Bước 5: Xuất SRT, script, song ngữ
Bước 6: Burn sub vào video (optional)
Bước 7: Lồng tiếng VieNeu-TTS (optional)

## Code Quality Improvements (Phase 4)

**Logging:**
- Structured logging với RotatingFileHandler
- Log file: `output/app.log` (10MB max, 3 backups)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Error Handling:**
- Specific exception types thay vì bare `except Exception:`
- Logging với context cho tất cả errors
- Network errors, FFmpeg errors, GPU errors được handle riêng

**Type Hints:**
- Type hints đầy đủ cho tất cả public APIs
- mypy configuration cho static type checking
- IDE autocomplete và documentation cải thiện

**Documentation:**
- Google-style docstrings cho tất cả public functions
- Args, Returns, Raises sections đầy đủ
- Context managers cho resource cleanup

## Tính năng hiện tại

**Hai chế độ xử lý video:**
1. **Monolithic mode** (nút "Bắt Đầu Xử Lý"): Chạy toàn bộ pipeline một lần
2. **Step-by-step mode** (7 nút "Bước 1-7"): Chạy từng bước riêng, có thể edit SRT giữa chừng

Cả hai mode đều sử dụng các step functions (step1-7) trong `workflow.py`.
Step-by-step UI đã hoàn chỉnh với pipeline_state tracking và SRT editor.

Backup đã có tại: `C:\Users\xhiep\Downloads\dubbing-extractor-backup-20260423_1630`

## Lưu ý code
- Comment tiếng Việt OK, nhưng tên biến/hàm phải tiếng Anh
- Không sửa trực tiếp `config.json`, `cookies.txt`, thư mục `venv/`, `bin/`, `output/`
- GPU: RTX 5060 (sm_120) — Whisper dùng CPU, NVENC encoding hoạt động tốt
