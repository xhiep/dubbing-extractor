# Test Run - Bilibili Video Processing

**Video URL**: https://www.bilibili.com/video/BV11sBvBqE8H/?spm_id_from=333.788.recommend_more_video.1&trackid=web_related_0.router-related-2479604-pxdwc.1776944977986.280&vd_source=59b4ec7d597ac0b51069a5293639d20e

**Date**: 2026-04-24
**Purpose**: Test UI improvements với video thực tế

## Các bước thực hiện

### 1. Mở ứng dụng
```bash
cd /c/Users/xhiep/Downloads/dubbing-extractor
python main.py
```

### 2. Nhập link video
- Paste link Bilibili vào ô "Nguồn Video"
- Hoặc click "📋 Dán" để paste từ clipboard

### 3. Cấu hình (tùy chọn)
- **Whisper Model**: base (mặc định) hoặc small/medium
- **Cover Mode**: blur (mặc định)
- **Subtitle Preset**: Mặc Định

### 4. Chạy từng bước và quan sát Toast Notifications

#### Bước 1: Tải video
- Click "▶ Bắt Đầu Xử Lý" hoặc "1️⃣ Tải Video"
- **Expect**: 
  - Toast xanh: "Bước 1 hoàn thành: Video đã tải xong"
  - Log area hiển thị chi tiết

#### Bước 2: Nhận dạng giọng nói
- Click "2️⃣ Nhận Dạng"
- **Expect**:
  - Toast xanh: "Bước 2 hoàn thành: Nhận dạng X đoạn"
  - Thời gian: ~1-3 phút tùy độ dài video

#### Bước 3: Dịch sang tiếng Việt
- Click "3️⃣ Dịch"
- **Expect**:
  - Toast xanh: "Bước 3 hoàn thành: Đã dịch X đoạn"
  - SRT editor xuất hiện để kiểm tra/sửa bản dịch

#### Bước 4: Render video
- Click "4️⃣ Render"
- **Expect**:
  - Toast xanh: "Bước 4 hoàn thành: Video đã render xong"
  - Video output trong thư mục output/

## Những gì cần quan sát

### ✅ Toast Notifications
- [ ] Toast xuất hiện ở top center
- [ ] Màu xanh cho success
- [ ] Màu đỏ nếu có lỗi
- [ ] Tự động ẩn sau 3 giây
- [ ] Nhiều toast có thể hiện cùng lúc

### ✅ Hover Effects
- [ ] Button "▶ Bắt Đầu Xử Lý" sáng hơn khi hover
- [ ] Button "Xóa Nhật Ký" sáng hơn khi hover
- [ ] Transition mượt mà

### ✅ Error Handling
Nếu có lỗi:
- [ ] Toast đỏ xuất hiện với thông báo lỗi
- [ ] Log area hiển thị chi tiết
- [ ] Pipeline dừng lại ở bước lỗi

## Expected Output

Sau khi hoàn thành bước 4, bạn sẽ có:

```
output/
└── [video-title]/
    ├── video_covered.mp4          # Video đã che phụ đề gốc
    ├── file_sub_viet.srt          # Phụ đề tiếng Việt
    ├── raw_video.mp4              # Video gốc
    ├── raw_audio.wav              # Audio gốc
    └── ...
```

## Troubleshooting

### Nếu Toast không xuất hiện:
1. Kiểm tra console có lỗi không
2. Restart ứng dụng
3. Kiểm tra import: `python -c "from src.components.toast import ToastManager; print('OK')"`

### Nếu download Bilibili thất bại:
- Kiểm tra yt-dlp đã cài đặt: `yt-dlp --version`
- Thử link khác
- Kiểm tra kết nối internet

### Nếu Whisper chậm:
- Dùng model "base" thay vì "medium" hoặc "large"
- Đảm bảo có GPU (nếu có)

## Screenshots cần chụp (nếu muốn)

1. Toast notification xuất hiện sau bước 1
2. Toast notification xuất hiện sau bước 2
3. Toast notification xuất hiện sau bước 3
4. Toast notification xuất hiện sau bước 4
5. Hover effect trên button

## Notes

- Toàn bộ quá trình có thể mất 5-15 phút tùy độ dài video
- Toast notifications không ảnh hưởng đến performance
- Bạn vẫn có thể làm việc khác trong khi xử lý
- Log area vẫn hiển thị đầy đủ thông tin như trước

---

**Status**: Ready to test
**Expected duration**: 5-15 minutes
**UI improvements**: Toast notifications + Hover effects active
