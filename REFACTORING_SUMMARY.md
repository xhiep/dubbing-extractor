# Refactoring Summary - main.py

## Trạng thái
- **File gốc**: main.py (2060 dòng) - **GIỮ NGUYÊN, HOẠT ĐỘNG TỐT**
- **Các helper modules**: Đã tạo sẵn để sử dụng cho tính năng mới hoặc refactor dần

## Lý do giữ nguyên main.py
- File main.py hiện tại hoạt động ổn định
- Refactor toàn bộ cùng lúc có nguy cơ gây lỗi
- Các helper modules đã tạo sẵn để sử dụng khi cần

## Các module helper đã tạo (sẵn sàng sử dụng)

### 1. `src/helpers/preview_helpers.py` (320 dòng)
Chứa các hàm xử lý preview và rendering:
- `format_duration()` - Format thời gian
- `wrap_preview_text()` - Wrap text phụ đề
- `load_render_meta()` - Load metadata render
- `extract_local_preview_frame()` - Extract frame từ video local
- `write_preview_srt()` - Ghi SRT tạm
- `escape_sub_path()` - Escape path cho ffmpeg
- `render_local_preview_composite()` - Render preview với overlay
- `extract_remote_preview_frame()` - Extract frame từ URL
- `parse_srt_segments()` - Parse file SRT
- `resolve_latest_srt_output()` - Tìm output SRT mới nhất

### 2. `src/helpers/pipeline_helpers.py` (130 dòng)
Quản lý pipeline workflow:
- `collect_params()` - Thu thập params từ UI state
- `PipelineManager` class:
  - `set_status()` - Set status message
  - `update_step_buttons()` - Update màu nút bước
  - `mark_step_error()` - Đánh dấu lỗi
  - `enable_srt_editor()` - Enable editor SRT
  - `disable_srt_editor()` - Disable editor SRT
  - `reset()` - Reset pipeline

### 3. `src/helpers/event_handlers.py` (220 dòng)
Xử lý UI events:
- `UIEventHandlers` class:
  - `paste_clipboard()` - Paste từ clipboard
  - `browse_file()` - Browse file video
  - `browse_ref_audio()` - Browse audio mẫu
  - `open_srt_external()` - Mở SRT bên ngoài
  - `reload_srt_from_file()` - Reload SRT
  - `save_srt_to_file()` - Lưu SRT
  - `open_render_folder()` - Mở thư mục output

- `TTSEventHandlers` class:
  - `refresh_voice_list()` - Refresh danh sách giọng
  - `sync_dub_mode()` - Sync UI theo dub mode
  - `stop_preview_audio()` - Dừng audio preview
  - `play_tts_preview()` - Phát TTS preview

- `PreviewEventHandlers` class:
  - `load_source_preview()` - Load preview từ source

### 4. `src/helpers/state_helpers.py` (50 dòng)
Quản lý state và presets:
- `PresetManager` class:
  - `mark_custom()` - Đánh dấu preset custom
  - `apply_selected()` - Apply preset đã chọn
- `setup_state_traces()` - Setup state traces

## Lợi ích của helper modules

1. **Sẵn sàng sử dụng**: Các helper đã được tạo và có thể import khi cần
2. **Dễ test**: Có thể test từng helper function độc lập
3. **Tái sử dụng**: Các helper có thể dùng ở nơi khác trong dự án
4. **Giảm độ phức tạp**: Mỗi module có trách nhiệm rõ ràng
5. **Refactor dần**: Có thể thay thế từng phần trong main.py khi cần

## Cách sử dụng helper modules

Khi cần refactor một phần của main.py, chỉ cần import và sử dụng:

```python
from src.helpers.preview_helpers import format_duration, wrap_preview_text
from src.helpers.pipeline_helpers import PipelineManager

# Sử dụng trong code
duration_text = format_duration(120.5)  # "2:00"
wrapped = wrap_preview_text("Long text...", 45)
```

## Kế hoạch refactor tiếp theo (tùy chọn)

1. Thay thế các hàm `_format_duration()` trong main.py bằng `format_duration()` từ helper
2. Thay thế các hàm `_wrap_preview_text()` bằng `wrap_preview_text()` từ helper
3. Dùng `PipelineManager` để quản lý pipeline state
4. Dùng các `EventHandlers` classes cho UI callbacks

## Trạng thái hiện tại

- ✅ Helper modules đã tạo và sẵn sàng
- ✅ main.py gốc hoạt động tốt (2060 dòng)
- ⏳ Chưa áp dụng helpers vào main.py (để tránh rủi ro)
- 📝 Có thể refactor dần khi cần bảo trì
