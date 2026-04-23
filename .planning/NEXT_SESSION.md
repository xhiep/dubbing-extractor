# Next Session - Phase 5: Extract Tab Views

**Date**: 2026-04-24
**Status**: Ready to start

## Current State

✅ **Completed (Phase 1-4):**
- Phase 1: Code cleanup (4 plans)
- Phase 2: Extract controllers (5 plans)
- Phase 3: Split main.py further (3 plans)
- Phase 4: Quality improvements (4 plans)

**Current main.py**: 2,527 dòng

## Goal Not Yet Achieved

❌ **Mục tiêu ban đầu**: main.py < 1,500 dòng (gọn, dễ nhìn, dễ sửa)
❌ **Hiện tại**: 2,527 dòng (vẫn còn ~2,300 dòng UI layout code)

## Phase 5 Plan: Extract Tab Views

**Objective**: Tách 4 tabs ra separate view files để main.py gọn hơn

**Tasks**:
1. Tạo `src/views/` directory
2. Extract Source tab → `src/views/source_tab.py` (~500 dòng)
3. Extract Adjust tab → `src/views/adjust_tab.py` (~800 dòng)
4. Extract Dub tab → `src/views/dub_tab.py` (~600 dòng)
5. Extract Log tab → `src/views/log_tab.py` (~200 dòng)
6. Update main.py to import and use views

**Expected Result**:
- main.py: 2,527 → ~400 dòng (giảm 84%)
- Mỗi tab: 1 file riêng, dễ maintain
- Mục tiêu đạt được: main.py < 1,500 dòng ✅

**Risk Level**: MEDIUM-HIGH
- Cần test kỹ sau khi tách
- UI layout phức tạp, nhiều dependencies
- Cần giữ nguyên tất cả functionality

## How to Start

```bash
cd C:/Users/xhiep/Downloads/dubbing-extractor
claude --dangerously-skip-permissions

# Lập kế hoạch Phase 5
/gsd-plan-phase 5

# Hoặc thêm phase vào roadmap trước
/gsd-add-phase "Extract Tab Views" --after 4
```

## Notes

- Tất cả Phase 1-4 đã push lên GitHub
- Backup: https://github.com/xhiep/dubbing-extractor
- Tất cả features đang hoạt động tốt
- Code quality đã được cải thiện đáng kể

## Context for Next Session

**What was done**:
- 16 plans executed successfully
- 30+ files improved with logging, type hints, docstrings
- Controllers extracted, code organized
- CHANGELOG.md created

**What's left**:
- Extract tab views to achieve original goal (main.py < 1,500 lines)
- This is the final step to make main.py truly "gọn, dễ nhìn, dễ sửa"

