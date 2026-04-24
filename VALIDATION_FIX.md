# Sửa Lỗi Validation Input Video

## Vấn Đề
- App không kiểm tra input trước khi xử lý
- Chấp nhận thư mục thay vì file video → FFmpeg lỗi "Permission denied"
- Chấp nhận file không phải video → Lỗi khi xử lý

## Ví Dụ Lỗi
```
Input: C:\Users\xhiep\Downloads\dubbing-extractor (thư mục)
→ FFmpeg cố mở thư mục như file video
→ Error: Permission denied
```

## Giải Pháp
Thêm validation đầy đủ cho cả 2 hàm:
1. `start_processing()` - Nút "Bắt Đầu Xử Lý"
2. `run_up_to_step()` - Các nút "Bước 1-5"

### Validation Checks

**1. Kiểm tra input không trống:**
```python
source = source_state.get().strip()
if not source:
    toast.error("Vui lòng nhập link video hoặc đường dẫn file")
    return
```

**2. Kiểm tra file local:**
```python
if is_local_file(source):
    source_path = Path(source)
    
    # Check file tồn tại
    if not source_path.exists():
        toast.error("File không tồn tại")
        return
    
    # Check không phải thư mục
    if source_path.is_dir():
        toast.error("Vui lòng chọn file video, không phải thư mục")
        return
    
    # Check định dạng video hợp lệ
    valid_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', 
                       '.wmv', '.webm', '.m4v', '.mpg', '.mpeg'}
    if source_path.suffix.lower() not in valid_extensions:
        toast.error(f"File không phải video hợp lệ ({source_path.suffix})")
        return
```

**3. Kiểm tra link online:**
```python
else:
    ok, preflight_msg = check_source_preconditions(source)
    if not ok:
        toast.error(f"Preflight failed: {preflight_msg}")
        return
```

## Kết Quả
Giờ khi người dùng:
- Để trống input → **"❌ Vui lòng nhập link video hoặc đường dẫn file"**
- Chọn thư mục → **"❌ Vui lòng chọn file video, không phải thư mục"**
- Chọn file .txt → **"❌ File không phải video hợp lệ (.txt)"**
- File không tồn tại → **"❌ File không tồn tại"**

Tất cả thông báo hiển thị màu đỏ trong pipeline_status_label.

## Files Đã Sửa
- `main.py` (dòng 1921-1951, 582-618)

## Ngày Sửa
2026-04-24
