# UI Improvements TODO

## Session Context
- **Date**: 2026-04-24
- **Current State**: App hoạt động tốt với Apple-inspired design
- **Tkinter Version**: 8.6
- **Theme**: src/components/theme.py (Apple design tokens)

## Yêu cầu cải thiện

### 1. Animations & Transitions ✅ COMPLETED
- [x] Thêm fade-in effects khi load tabs
- [x] Smooth progress indicators
- [x] Hover effects cho buttons

**Implementation**: `src/components/animations.py`

### 2. Visual Feedback ✅ COMPLETED
- [x] Loading spinners đẹp hơn
- [x] Toast notifications thay vì status text
- [x] Progress bars với gradients

**Implementation**: 
- `src/components/loading.py`
- `src/components/toast.py`
- `src/components/enhanced_progress.py`

### 3. Modern Components ⏳ PARTIAL
- [ ] Custom styled scrollbars
- [ ] Rounded corners cho cards
- [ ] Shadow effects (nếu Tkinter hỗ trợ)

**Status**: Foundation ready, needs integration

### 4. Color Enhancements ✅ COMPLETED
- [x] Thêm gradient backgrounds
- [x] Accent colors cho states (success, error, warning)
- [x] Dark mode toggle

**Implementation**: `src/components/theme.py` (updated)

## Files cần tạo/sửa

### Tạo mới:
1. `src/components/animations.py` - Animation helpers
2. `src/components/toast.py` - Toast notification widget
3. `src/components/loading.py` - Loading spinner widget
4. `src/components/enhanced_progress.py` - Gradient progress bar

### Sửa đổi:
1. `src/components/theme.py` - Thêm state colors và dark theme
2. `src/components/ui/widgets.py` - Apply animations cho existing widgets
3. `main.py` - Integrate new components

## Technical Constraints

### Tkinter Limitations:
- Không có native CSS-like transitions
- Shadow effects cần simulate bằng layered widgets
- Gradients cần vẽ bằng Canvas
- Animations phải dùng `after()` scheduling

### Performance Considerations:
- Giữ animations dưới 60fps
- Avoid blocking main thread
- Cache rendered gradients
- Lazy load heavy components

## Testing Checklist

- [ ] Test animations trên Windows
- [ ] Verify performance với large files
- [ ] Check memory usage với animations
- [ ] Test dark mode toggle
- [ ] Verify toast notifications không block UI

## References

- Current theme: `src/components/theme.py`
- Existing components: `src/components/ui/`
- Main UI: `main.py` (2060 lines)
- Helper modules: `src/helpers/` (đã tạo sẵn)

## Next Steps

1. Bắt đầu với animations.py (foundation)
2. Implement toast notifications (high impact)
3. Add state colors to theme
4. Create enhanced progress bar
5. Implement dark mode toggle
6. Apply animations to existing components

## Notes

- Giữ Apple-inspired aesthetic
- Maintain code quality và structure
- Test từng component trước khi integrate
- Document mọi thay đổi
