# HƯỚNG DẪN SỬ DỤNG NHANH

## Tổng quan

Dubbing Extractor v2 - Tool tự động:
- Tải video từ Douyin/Bilibili/YouTube hoặc dùng file local
- Nhận dạng giọng nói bằng Whisper AI
- Dịch sang tiếng Việt
- Che phủ đề cũ (blur/blackbar)
- Ghi phụ đề mới vào video
- Lồng tiếng tiếng Việt bằng VieNeu-TTS
- Clone giọng từ file audio mẫu và nghe thử ngay trong app

## Cài đặt

### Lần đầu sử dụng:

```bash
scripts\install.bat
```

Script sẽ tự động:
- Tạo virtual environment
- Tải FFmpeg
- Cài đặt Python packages, gồm cả VieNeu-TTS
- Cài PyTorch với CUDA support
- Giữ cache/model/temp trong thư mục project

### Kiểm tra hệ thống:

```bash
venv\Scripts\python.exe scripts\system_check.py
```

## Sử dụng

### Chạy app:

```bash
scripts\run.bat
```

Hoặc:

```bash
python main.py
```

### Giao diện:

1. **Video Source**
   - Paste URL video (Douyin/Bilibili/YouTube)
   - Hoặc Browse file video local (.mp4, .avi, .mkv, .mov, .flv)

2. **Settings**
   - **Cover Mode**: Cách che phủ đề cũ
     - `none`: Giữ nguyên sub gốc
     - `blur`: Làm mờ vùng có sub cũ (khuyến nghị)
     - `blackbar`: Che đen vùng có sub cũ
   
   - **Whisper Model**: Model nhận dạng giọng nói
     - `tiny`: Nhanh nhất, chất lượng thấp
     - `base`: Cân bằng tốc độ/chất lượng (khuyến nghị)
     - `small`: Chậm hơn, chất lượng tốt hơn
     - `medium`: Chậm, chất lượng cao
     - `large`: Chậm nhất, chất lượng tốt nhất
   
   - **Burn subtitle**: Ghi phụ đề vào video
     - Tích: Tạo thêm file video_sub_viet.mp4 có phụ đề
     - Không tích: Chỉ tạo file .srt riêng

3. **Lồng tiếng**
   - **Bật lồng tiếng tiếng Việt**: Tạo thêm audio dub và video đã lồng tiếng
   - **Chế độ giọng**
     - `Giọng mẫu`: Chọn sẵn giọng trong VieNeu
     - `Clone từ file`: Dùng file audio mẫu để clone giọng
   - **Text nghe thử**: Nhập nội dung để nghe thử trước khi render
   - **Âm lượng gốc**: Chỉnh âm thanh gốc còn lại phía sau track lồng tiếng
   - **Cách mix audio**
     - `nen_nho`: Giữ audio gốc nhỏ phía sau
     - `tat_goc`: Tắt hẳn audio gốc, chỉ giữ voice dub

4. **Start Processing**
   - Click để bắt đầu xử lý
   - Theo dõi tiến trình trong Log

## Kết quả

Sau khi xử lý xong, các file được lưu trong `output/[tên_video_timestamp]/`:

- `video_ready.mp4` - Video đã che phủ đề cũ
- `file_sub_viet.srt` - File phụ đề tiếng Việt
- `audio_goc.mp3` - Audio gốc
- `kich_ban_dich.txt` - Kịch bản dịch (chỉ text)
- `song_ngu_tham_chieu.txt` - Bản song ngữ tham chiếu
- `video_sub_viet.mp4` - Video có phụ đề (nếu chọn Burn subtitle)
- `audio_long_tieng.wav` - Track lồng tiếng tiếng Việt
- `video_long_tieng.mp4` - Video đã lồng tiếng
- `render_meta.json` - Metadata để preview khớp hơn với vị trí subtitle khi xuất

## Ví dụ sử dụng

### Ví dụ 1: Xử lý video từ URL

1. Copy URL video Douyin/Bilibili
2. Paste vào ô "Video Source"
3. Chọn Cover Mode: `blur`
4. Chọn Whisper Model: `base`
5. Click "Start Processing"
6. Đợi xử lý xong (5-15 phút tùy độ dài video)

### Ví dụ 2: Xử lý video local

1. Click "Browse" và chọn file video
2. Chọn settings như mong muốn
3. Click "Start Processing"

### Ví dụ 3: Tạo video có phụ đề

1. Paste URL hoặc browse file
2. Chọn Cover Mode: `blur`
3. Chọn Whisper Model: `base`
4. **Tích vào "Burn subtitle to video"**
5. Click "Start Processing"
6. Kết quả: Có thêm file `video_sub_viet.mp4` với phụ đề đã ghi vào

### Ví dụ 4: Clone giọng và lồng tiếng

1. Mở tab `Lồng Tiếng`
2. Tích `Bật lồng tiếng tiếng Việt`
3. Chọn `Clone từ file`
4. Chọn file audio mẫu, ví dụ `C:\Users\xhiep\Downloads\testV.mp3`
5. Nhập hoặc giữ nguyên text nghe thử rồi bấm `Nghe Thử Giọng`
6. Quay lại xử lý video như bình thường
7. Kết quả có thêm `audio_long_tieng.wav` và `video_long_tieng.mp4`

## Xử lý sự cố

### Whisper quá chậm

Giảm model size:
- `large` → `medium` (nhanh 2x)
- `medium` → `small` (nhanh 2x)
- `small` → `base` (nhanh 2x)

### Lỗi tải video

1. Kiểm tra cookies.txt:
   - Đăng nhập vào website (Douyin/Bilibili)
   - Export cookies bằng extension EditThisCookie
   - Lưu vào file `cookies.txt` ở thư mục gốc

2. Thử lại với URL khác

3. Dùng file video local thay vì URL

### NVENC encoding lỗi

App tự động fallback về CPU encoding (libx264).
Không cần làm gì, chỉ chậm hơn một chút.

### Lỗi "ffmpeg not found"

Chạy lại installer:
```bash
scripts\install.bat
```

### VieNeu-TTS không chạy

1. Chạy lại:
```bash
scripts\install.bat
```
2. Kiểm tra:
```bash
venv\Scripts\python.exe scripts\system_check.py
```
3. Nếu dùng clone giọng, file audio mẫu phải tồn tại thật và đọc được

## Cấu hình nâng cao

### File config.json

Lưu settings của GUI, tự động cập nhật khi dùng.

### File .env (tùy chọn)

Copy `.env.example` thành `.env` và chỉnh sửa:

```bash
WHISPER_MODEL=base      # Model mặc định
TARGET_LANGUAGE=vi      # Ngôn ngữ đích
OUTPUT_DIR=output       # Thư mục output
```

## GPU Support

### NVENC Encoding

- **Hỗ trợ**: NVIDIA GPU với NVENC
- **Hiệu năng**: 3-5x nhanh hơn CPU encoding
- **Auto fallback**: Tự động chuyển sang CPU nếu NVENC lỗi

### Whisper Transcription

- **Hiện tại**: Chạy trên CPU
- **Lý do**: RTX 5060 (sm_120) chưa được PyTorch hỗ trợ đầy đủ
- **Hiệu năng**: Vẫn rất nhanh trên CPU

## Tips & Tricks

1. **Tốc độ xử lý**:
   - Video 5 phút với model `base`: ~3-5 phút
   - Video 5 phút với model `large`: ~10-15 phút

2. **Chất lượng dịch**:
   - Model lớn hơn = nhận dạng chính xác hơn = dịch tốt hơn
   - Khuyến nghị: `base` cho video thông thường, `small` cho video quan trọng

3. **Cover mode**:
   - `blur`: Tự nhiên nhất, hiện bám theo thời gian subtitle mới sau khi dịch
   - `blackbar`: Rõ ràng hơn nhưng kém tự nhiên
   - `none`: Dùng khi không có sub cũ hoặc muốn giữ nguyên

4. **Burn subtitle**:
   - Tích: Video có sẵn phụ đề, dễ xem trên mọi thiết bị
   - Không tích: Linh hoạt hơn, có thể chỉnh sửa file .srt sau

5. **Preview subtitle**:
   - Sau khi render, preview đọc `render_meta.json` và `file_sub_viet.srt`
   - Marker timeline giúp nhảy đúng câu subtitle mới
   - Kéo trực tiếp subtitle trên khung video để chỉnh vị trí dọc

## Hỗ trợ

- **Documentation**: Xem thư mục `docs/`
- **AGENTS.md**: Cấu trúc project và quy tắc code
- **README.md**: Tài liệu chi tiết

## Changelog

### v2.5 (2026-04-22)

- ✅ Tích hợp VieNeu-TTS
- ✅ Thêm giọng mẫu, clone giọng, nghe thử trong UI
- ✅ Xuất `audio_long_tieng.wav` và `video_long_tieng.mp4`
- ✅ Blur bám theo thời gian subtitle mới sau bước dịch
- ✅ Preview đọc metadata render để gần với vị trí subtitle thực tế hơn

### v2.4.1 (2026-04-22)

- ✅ Fixed: srt_generator.py syntax error
- ✅ Fixed: video_encoder.py missing functions
- ✅ Fixed: subtitle_burner.py missing functions
- ✅ Fixed: workflow.py missing process_video function
- ✅ All modules now working correctly
- ✅ GUI tested and functional

### v2.4 (2026-04-22)

- Refactored to modular structure
- Added GPU optimization (NVENC)
- Added virtual environment support
- Improved configuration management
- Updated documentation

---

**Quick Start**: `scripts\install.bat` → `scripts\run.bat`

**Support**: Check `docs/START_HERE.txt`
