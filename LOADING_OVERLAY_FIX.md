# Thêm Loading Overlay

## Vấn Đề
- Khi xử lý video, UI bị đơ và không phản hồi
- User không biết app đang làm gì
- Không có indicator cho biết đang xử lý

## Giải Pháp
Thêm `LoadingOverlay` - một overlay toàn màn hình với spinner và message

### Thay Đổi Code

**1. Import LoadingOverlay (dòng 57):**
```python
from src.components.loading import LoadingSpinner, LoadingOverlay
```

**2. Tạo loading overlay (dòng 319-323):**
```python
# Main container
main_frame = tk.Frame(root, padx=16, pady=16, bg=T.BG_LIGHT)
main_frame.pack(fill=tk.BOTH, expand=True)

# Create loading overlay (hidden by default)
loading_overlay = LoadingOverlay(root, message="Đang xử lý...")
loading_overlay.place_forget()  # Hide initially
```

**3. Hiển thị loading trong `start_processing()` (dòng 2080-2084):**
```python
try:
    # Show loading overlay
    loading_overlay.update_message("Đang xử lý video...")
    loading_overlay.show()
    root.update()

    # Disable buttons during processing
    start_btn.config(state=tk.DISABLED)
    
    # Process video...
```

**4. Ẩn loading khi xong (dòng 2131-2133):**
```python
finally:
    # Hide loading overlay
    loading_overlay.hide()
    start_btn.config(state=tk.NORMAL)
```

**5. Tương tự cho `run_up_to_step()` (dòng 624-632, 843-846):**
```python
# Show loading
loading_overlay.update_message(f"Đang chạy bước {target_step}...")
loading_overlay.show()
root.update()

try:
    # Process steps...
finally:
    # Hide loading overlay
    loading_overlay.hide()
    _update_step_buttons()
    start_btn.config(state=tk.NORMAL)
```

## Kết Quả
- ✅ Hiển thị overlay với spinner khi đang xử lý
- ✅ Message rõ ràng: "Đang xử lý video..." hoặc "Đang chạy bước X..."
- ✅ UI không bị đơ, user biết app đang hoạt động
- ✅ Tự động ẩn khi xử lý xong hoặc lỗi

## UI Components Sử dụng
- `LoadingOverlay`: Overlay toàn màn hình với background semi-transparent
- `LoadingSpinner`: Spinner xoay 360 độ
- Message label: Hiển thị trạng thái hiện tại

## Ngày Thêm
2026-04-24
