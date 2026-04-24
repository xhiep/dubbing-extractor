# Phase 5 Manual Test Plan

**Date:** 2026-04-24
**Tester:** User
**App Version:** After Phase 5 view extraction

## Test Environment
- Launch: `scripts\run.bat`
- Test URL: https://www.bilibili.com/video/BV11sBvBqE8H/

---

## Test Cases

### 1. Tab Visibility ✓/✗
- [ ] Tab "Nguồn" (Source) visible
- [ ] Tab "Điều Chỉnh" (Adjust) visible  
- [ ] Tab "Lồng Tiếng" (Dub) visible
- [ ] Tab "Nhật Ký" (Log) visible

### 2. Source Tab - Basic Controls
- [ ] Source input field visible
- [ ] "Dán Link" button visible
- [ ] "Chọn File" button visible
- [ ] Click "Dán Link" → paste from clipboard works
- [ ] Click "Chọn File" → file dialog opens
- [ ] Paste Bilibili URL → preview loads (or shows error)
- [ ] Press Enter in source input → preview loads

### 3. Source Tab - Step Buttons
- [ ] 5 step buttons visible (Bước 1-5)
- [ ] Step buttons are clickable
- [ ] Reset button visible
- [ ] SRT editor area visible

### 4. Adjust Tab - Layout
- [ ] Tab opens without error
- [ ] Left panel (settings) visible
- [ ] Right panel (preview) visible
- [ ] Scrollbar visible on right side
- [ ] Mouse wheel scrolls the content

### 5. Adjust Tab - Controls
- [ ] Cover mode radio buttons (blur/blackbar/none) visible
- [ ] Preset dropdown visible
- [ ] Blur radius slider visible
- [ ] Blackbar height slider visible
- [ ] Font scale slider visible
- [ ] All sliders are draggable

### 6. Dub Tab - Controls
- [ ] TTS mode radio buttons visible
- [ ] Voice dropdown visible
- [ ] Quick dub checkbox visible
- [ ] Reference audio browse button visible
- [ ] Voice preview button visible

### 7. Log Tab
- [ ] Log text area visible
- [ ] "Xóa Nhật Ký" button visible
- [ ] Click "Xóa Nhật Ký" → log clears

### 8. Main Controls
- [ ] "Bắt Đầu Xử Lý" button visible
- [ ] "Xóa Nhật Ký" button visible (top bar)
- [ ] Both buttons are clickable

### 9. Full Pipeline Test (Optional)
- [ ] Load Bilibili URL
- [ ] Click "Bắt Đầu Xử Lý"
- [ ] Processing starts without crash
- [ ] Log shows progress messages
- [ ] Output files created in output/ folder

---

## Known Issues to Check
1. ~~Missing Log and Dub tabs~~ ✓ FIXED
2. ~~"Dán Link" button not calling preview~~ ✓ FIXED
3. Scroll behavior in Adjust tab
4. Preview canvas rendering

---

## Report Format

**Pass:** All tests ✓
**Fail:** List failed tests with details

Example:
```
FAIL: Test 2 - "Dán Link" button
- Expected: Paste URL and load preview
- Actual: Nothing happens
- Error: (if any console error)
```
