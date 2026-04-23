---
project: Dubbing Extractor - Code Cleanup & Refactoring
created: 2026-04-23
status: planning
type: brownfield
---

# Dubbing Extractor - Dọn Dẹp & Tái Cấu Trúc

## Tổng Quan

Dự án video dubbing tool với pipeline 7 bước: download → transcribe → translate → cover subtitles → export → burn → dub. Hiện tại codebase hoạt động tốt nhưng cần dọn dẹp và cải thiện chất lượng code.

## Mục Tiêu Chính

**Dọn dẹp và tái cấu trúc codebase** để cải thiện maintainability, code quality, và developer experience.

### Phạm Vi Cụ Thể

1. **Refactor main.py** (~3,000 dòng)
   - Tách GUI logic thành các module nhỏ hơn
   - Tách event handlers ra khỏi UI code
   - Cải thiện separation of concerns

2. **Xóa code thừa/dở dang**
   - Xóa step-by-step UI chưa hoàn thiện (step1-7 functions tồn tại nhưng UI chưa có)
   - Xóa duplicate code (ví dụ: quick_dub_toggle dòng 196-209)
   - Xóa commented code, unused imports
   - Xóa pipeline_state dict chưa dùng

3. **Cải thiện code quality**
   - Cải thiện error handling (hiện tại nhiều `except Exception: pass`)
   - Cải thiện logging và debugging
   - Cải thiện resource cleanup (memory, CUDA, file handles)
   - Thêm input validation

4. **Cải thiện documentation**
   - Thêm type hints đầy đủ hơn
   - Thêm docstrings cho public APIs
   - Cải thiện inline comments
   - Cập nhật documentation (CLAUDE.md có line count cũ)

## Bối Cảnh Kỹ Thuật

### Stack Hiện Tại
- **Language**: Python 3.11
- **GUI**: Tkinter với custom component library
- **AI/ML**: Whisper (transcription), VieNeu-TTS (dubbing), Google Translate
- **Video**: ffmpeg (bundled), yt-dlp (download), OpenCV (subtitle detection)
- **Architecture**: Modular pipeline với workflow orchestration

### Codebase Stats
- **Total**: ~5,000 lines Python
- **main.py**: ~3,000 lines (monolithic GUI)
- **src/modules/**: ~2,000 lines (business logic)
- **Test coverage**: Minimal (2 unit tests)

### Điểm Mạnh
- Pipeline hoạt động tốt
- Custom UI components đẹp (Apple-inspired design)
- Modular architecture ở business logic layer
- Clear separation: src/modules/ vs src/components/

### Điểm Yếu (Cần Dọn Dẹp)
- main.py quá lớn, khó maintain
- Code dở dang (step-by-step UI)
- Error handling không nhất quán
- Thiếu tests
- Documentation lỗi thời

## Ràng Buộc

### Phải Giữ Nguyên
- Tất cả tính năng hiện tại phải hoạt động như cũ
- Không thay đổi UI/UX (chỉ refactor code)
- Không thay đổi config.json format (user settings)
- Không thay đổi output file format
- Comments tiếng Việt OK, code tiếng Anh

### Không Được Sửa
- `config.json` (user settings)
- `cookies.txt` (user cookies)
- `venv/` (virtual environment)
- `bin/` (ffmpeg binary)
- `output/` (user outputs)
- `.cache/` (model cache)

### Môi Trường
- Windows 10 Pro
- Python 3.11.9
- RTX 5060 (Whisper chạy CPU, TTS chạy GPU)
- ffmpeg tại `bin/ffmpeg/ffmpeg.exe` (không trong PATH)
- Bash shell (Git Bash)

## Thành Công Khi

1. **main.py < 1,500 dòng** (giảm 50%)
2. **Không còn code dở dang** (step functions, pipeline_state)
3. **Error handling nhất quán** (không còn silent failures)
4. **Type hints đầy đủ** cho public APIs
5. **Documentation chính xác** (line counts, architecture)
6. **Tất cả tính năng vẫn hoạt động** (manual testing pass)

## Không Thành Công Nếu

- Tính năng bị break
- UI/UX thay đổi
- Performance giảm
- User settings bị mất
- Thêm dependencies mới không cần thiết

## Tài Liệu Tham Khảo

### Codebase Map
- `.planning/codebase/STACK.md` - Tech stack
- `.planning/codebase/ARCHITECTURE.md` - Architecture overview
- `.planning/codebase/STRUCTURE.md` - Directory structure
- `.planning/codebase/CONVENTIONS.md` - Code conventions
- `.planning/codebase/CONCERNS.md` - Technical debt

### Project Docs
- `CLAUDE.md` - Claude context (cần cập nhật)
- `DESIGN.md` - UI design system
- `README.md` - Project overview
- `HUONG_DAN_SU_DUNG.md` - User guide (Vietnamese)

## Ghi Chú

- Backup tồn tại tại: `C:\Users\xhiep\Downloads\dubbing-extractor-backup-20260423_1630`
- Không phải git repo (không có .git)
- Commit style: atomic (nhưng không có git, sẽ dùng file snapshots)
