---
phase: 1
name: Code Cleanup (Low Risk)
created: 2026-04-23
updated: 2026-04-23
status: complete
---

# Phase 1 Research: Code Cleanup (Low Risk) — CORRECTED

## Objective

Nghiên cứu lại cách thực hiện code cleanup an toàn cho Dubbing Extractor sau khi phát hiện research ban đầu có giả định SAI về tình trạng step-by-step UI.

## Phase Scope

**Goal**: Xóa code thừa, dở dang, và cập nhật documentation

**Duration**: 2-3 giờ

**Risk Level**: LOW - Chỉ xóa code không dùng, không thay đổi logic

## CRITICAL CORRECTION: Step-by-Step UI IS IMPLEMENTED

### Original Research Was WRONG

**Original claim (INCORRECT):**
> Functions exist but no UI buttons call them
> Original plan was step-by-step execution UI (never completed)
> pipeline_state dict declared but never used

**Actual Reality (VERIFIED):**

1. **Step functions ARE used** (27 references found):
   - Called in main.py lines 727-892 (step-by-step execution handler)
   - Called in process_video() lines 459-522 (monolithic pipeline)
   - Imported in main.py line 27-33

2. **pipeline_state IS used** (30+ references found):
   - Declared line 416
   - Used throughout lines 593-780+ for state management
   - Tracks current_step, raw_audio, segs, segs_vi, srt_path, etc.

3. **Step-by-step UI IS implemented** (32 UI references found):
   - 7 step buttons created (step_btn_widgets)
   - Button state management (_update_step_buttons)
   - Pipeline status display
   - SRT editor integration after step 3

### Evidence

```bash
# Step functions in workflow.py
$ grep -c "def step[1-7]_" src/modules/workflow.py
7

# Step function calls in main.py
$ grep -c "step[1-7]_" main.py
14

# Step button UI references
$ grep -n "step_btn_widgets\|Bước [1-7]" main.py | wc -l
32

# Line counts
$ wc -l main.py src/modules/workflow.py
  2481 main.py
   567 src/modules/workflow.py
```

## Actual Dead Code Analysis

### What IS Actually Dead Code

After reading the actual implementation, here's what can be safely removed:

#### 1. Commented-Out Code Blocks

**Location**: Throughout codebase
**Examples**:
- Old implementations commented out but not deleted
- Debug print statements commented out
- Experimental code paths commented out

**Why Remove**: Clutters code, confuses readers, should be in git history not in files

**Risk**: VERY LOW - comments don't execute

#### 2. Unused Imports

**Location**: All Python files
**Detection**: `flake8 --select=F401`

**Why Remove**: Slows import time, confuses dependencies

**Risk**: VERY LOW - unused imports don't affect runtime

#### 3. Duplicate UI Controls (IF ANY)

**Need to verify**: CLAUDE.md mentions "duplicate checkbox lồng tiếng (quick_dub_toggle dòng 196-209)"

**Action**: Read main.py lines 196-209 to verify if duplicate exists

**Risk**: LOW - if truly duplicate, safe to remove

### What is NOT Dead Code (DO NOT REMOVE)

#### 1. Step Functions (step1-7)

**Status**: ACTIVELY USED
**Used by**:
- main.py step-by-step execution (lines 727-892)
- process_video() monolithic pipeline (lines 459-522)

**DO NOT REMOVE** - Would break both execution modes

#### 2. pipeline_state Dict

**Status**: ACTIVELY USED
**Used by**:
- State tracking across steps (30+ references)
- Button state management
- SRT editor integration

**DO NOT REMOVE** - Would break step-by-step UI

#### 3. step_btn_widgets

**Status**: ACTIVELY USED
**Used by**:
- 7 step buttons in UI
- Button state updates
- User interaction

**DO NOT REMOVE** - Would break UI

## Revised Cleanup Strategy

### Safe Cleanup Tasks

#### Task 1: Remove Commented Code

**Scope**: All .py files
**Method**:
```bash
# Find commented code blocks (not docstrings, not explanatory comments)
grep -r "^[[:space:]]*#.*def \|^[[:space:]]*#.*class \|^[[:space:]]*#.*import " src/ main.py
```

**Keep**:
- Docstrings ("""...""")
- Explanatory comments (# This handles edge case X)
- TODO/FIXME comments
- License headers

**Remove**:
- Commented-out function definitions
- Commented-out class definitions
- Commented-out import statements
- Commented-out code blocks

**Estimated**: ~50-100 lines removed

#### Task 2: Remove Unused Imports

**Scope**: All .py files
**Method**:
```bash
flake8 --select=F401 src/ main.py
```

**Risk**: VERY LOW - flake8 only flags truly unused imports

**Estimated**: ~20-50 lines removed

#### Task 3: Verify and Remove Duplicate Controls (IF EXISTS)

**Action**: Read main.py lines 196-209 to check for duplicate checkbox

**If duplicate exists**: Remove it
**If no duplicate**: Skip this task

**Estimated**: ~10-15 lines removed (if exists)

#### Task 4: Update Documentation

**Files to update**:
- CLAUDE.md: Remove "Việc đang làm" section (outdated)
- CLAUDE.md: Fix line counts (main.py ~2481, workflow.py ~567)
- .planning/codebase/ARCHITECTURE.md: Update line counts
- .planning/codebase/CONCERNS.md: Remove "Work In Progress" section

**Risk**: ZERO - documentation only

**Estimated**: Documentation updates only

#### Task 5: Testing

**Scope**: Comprehensive testing after cleanup

**Tests**:
- App launches without errors
- Step-by-step UI works (all 7 buttons)
- Monolithic pipeline works (Bắt Đầu button)
- Config save/load works
- Full pipeline test (download → dub)

**Risk**: ZERO - testing doesn't change code

## What We Learned

### Why Original Research Failed

1. **Didn't read main.py implementation** - Only read CLAUDE.md which was outdated
2. **Assumed "dở dang" means "not implemented"** - Actually means "work in progress" but was completed
3. **Didn't grep for function calls** - Would have immediately found 27 references
4. **Didn't verify claims** - Trusted documentation over code

### How to Avoid This

1. **Always read the actual code** - Documentation can be outdated
2. **Grep for function calls before assuming dead code** - `grep -r "function_name" .`
3. **Check git history** - See when features were added/completed
4. **Test assumptions** - If doc says "not used", verify with grep

## Revised Success Criteria

- ✅ Commented-out code removed
- ✅ Unused imports removed
- ✅ Duplicate controls removed (if any exist)
- ✅ Documentation updated to reflect reality
- ✅ All features still work (step-by-step + monolithic)
- ✅ No regressions in functionality

## Risk Assessment

### Original Plans (WOULD HAVE BEEN CATASTROPHIC)

- Plan 01: Delete step functions → ❌ BREAKS EVERYTHING
- Plan 02: Delete pipeline_state → ❌ BREAKS STEP-BY-STEP UI

**Impact**: Complete loss of video processing functionality

### Revised Plans (SAFE)

- Remove commented code → ✅ SAFE (comments don't execute)
- Remove unused imports → ✅ SAFE (flake8 verified)
- Remove duplicate controls → ✅ SAFE (if truly duplicate)
- Update documentation → ✅ SAFE (docs only)

**Impact**: Cleaner code, no functionality lost

## Estimated Impact

### Before Cleanup
- main.py: 2481 lines
- workflow.py: 567 lines
- Commented code: ~50-100 lines
- Unused imports: ~20-50 lines
- Documentation: Outdated

### After Cleanup
- main.py: ~2400 lines (80 lines removed)
- workflow.py: ~550 lines (17 lines removed)
- Commented code: 0 lines
- Unused imports: 0 lines
- Documentation: Accurate

**Total saved**: ~100-150 lines (not 450 as originally claimed)

## Constraints

### Must NOT Change
- Step functions (actively used)
- pipeline_state dict (actively used)
- step_btn_widgets (actively used)
- Any functionality
- UI appearance or layout

### Must Preserve
- Step-by-step execution mode
- Monolithic pipeline mode
- All 7 step buttons
- SRT editor integration
- Config save/load
- All video processing features

## Conclusion

Phase 1 scope is now MUCH SMALLER than originally planned:
- Remove commented code (safe)
- Remove unused imports (safe)
- Update documentation (safe)
- NO structural changes
- NO feature removal

This is truly "low risk" cleanup - only removing code that doesn't execute.

Original plans would have been HIGH RISK and CATASTROPHIC.
