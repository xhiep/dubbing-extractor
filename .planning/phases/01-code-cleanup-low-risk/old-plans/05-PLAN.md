---
wave: 4
plan_id: "05"
depends_on: ["01", "02", "03", "04"]
files_modified: []
autonomous: false
requirements_addressed: []
---

# Plan 05: Final Testing and Verification

<objective>
Thực hiện comprehensive testing để verify tất cả tính năng vẫn hoạt động sau cleanup. Tạo testing report để document Phase 1 completion.
</objective>

<tasks>

<task id="5.1">
<read_first>
- .planning/REQUIREMENTS.md (FR1: Giữ Nguyên Tất Cả Tính Năng)
- .planning/ROADMAP.md (Phase 1 Success Criteria)
</read_first>

<action>
Smoke Test - Quick verification:

1. Launch app:
   scripts\run.bat
   
2. Verify app launches without errors:
   - No import errors in console
   - Window appears
   - All tabs visible (Nguồn, Phụ Đề, Lồng Tiếng)

3. Check each tab:
   - Tab Nguồn: All controls visible
   - Tab Phụ Đề: All controls visible
   - Tab Lồng Tiếng: Only ONE TTS checkbox visible (not duplicate)

4. Quick interaction test:
   - Change source input
   - Change cover mode
   - Toggle TTS checkbox
   - All controls respond

5. Config test:
   - Change some settings
   - Close app
   - Reopen app
   - Verify settings persisted
</action>

<acceptance_criteria>
- App launches: scripts\run.bat exits 0
- No errors in console output
- All 3 tabs visible and clickable
- Only one TTS checkbox visible (duplicate removed)
- All UI controls respond to interaction
- Config saves and loads correctly
</acceptance_criteria>
</task>

<task id="5.2">
<read_first>
- dummy_in.mp4 (if exists, use as test video)
- .planning/REQUIREMENTS.md (FR1 acceptance criteria)
</read_first>

<action>
Full Pipeline Test - Comprehensive verification:

1. Prepare test video:
   - Use dummy_in.mp4 if exists
   - Or use small local video file
   - Or use short YouTube URL

2. Run complete pipeline:
   - Load video in app
   - Set cover mode: blur
   - Enable TTS
   - Click "Bắt Đầu" button
   - Wait for completion

3. Verify each step completes:
   - Download/load: ✓
   - Transcribe (Whisper): ✓
   - Translate: ✓
   - Cover subtitles: ✓
   - Export SRT: ✓
   - Burn subtitles: ✓
   - TTS dubbing: ✓

4. Check outputs:
   - output/{title}_{timestamp}/ directory created
   - audio_goc.mp3 exists
   - video_sach.mp4 exists (covered subtitles)
   - phu_de_goc.srt exists
   - phu_de_viet.srt exists
   - phu_de_song_ngu.srt exists
   - video_phu_de.mp4 exists (burned subtitles)
   - video_long_tieng.mp4 exists (dubbed)

5. Verify video quality:
   - Play video_long_tieng.mp4
   - Check video plays
   - Check audio plays
   - Check subtitles visible (if burned)
</action>

<acceptance_criteria>
- Pipeline completes without errors
- All 7 steps execute successfully
- All output files created in output/ directory
- SRT files contain valid subtitle data
- Video files playable
- Audio synchronized with video
- No functionality lost compared to before cleanup
</acceptance_criteria>
</task>

<task id="5.3">
<read_first>
- .planning/ROADMAP.md (Phase 1 Success Criteria)
- .planning/REQUIREMENTS.md (NFR2: Remove Dead Code)
</read_first>

<action>
Code Quality Verification:

1. Verify no dead code remains:
   grep -r "step[1-7]_" src/ main.py
   # Should return: no results
   
   grep -r "pipeline_state" main.py
   # Should return: no results

2. Verify no unused imports:
   flake8 --select=F401 src/ main.py
   # Should return: no errors

3. Verify no commented code:
   grep -r "^#.*def \|^#.*class " src/ main.py --include="*.py"
   # Should return: no commented function/class definitions

4. Count lines saved:
   wc -l main.py
   # Should be ~2800 (down from ~3000)
   
   wc -l src/modules/workflow.py
   # Should be ~350 (down from ~600)
   
   Total saved: ~450 lines

5. Verify syntax:
   find src/ -name "*.py" -exec python -m py_compile {} \;
   python -m py_compile main.py
   # All should exit 0
</action>

<acceptance_criteria>
- No references to step1-7 functions: grep returns empty
- No references to pipeline_state: grep returns empty
- No unused imports: flake8 F401 clean
- No commented code blocks: grep returns empty
- main.py ~2800 lines (200 saved)
- workflow.py ~350 lines (250 saved)
- All Python files compile without syntax errors
</acceptance_criteria>
</task>

<task id="5.4">
<read_first>
- CLAUDE.md
- .planning/codebase/ARCHITECTURE.md
- .planning/codebase/CONCERNS.md
</read_first>

<action>
Documentation Verification:

1. Verify CLAUDE.md accurate:
   - Line count matches: wc -l main.py
   - No "Việc đang làm" section about step-by-step UI
   - Has "Trạng thái hiện tại" section

2. Verify codebase maps accurate:
   - ARCHITECTURE.md line counts match reality
   - CONCERNS.md "Work In Progress" section removed
   - STRUCTURE.md file paths valid

3. Verify no broken references:
   - All file paths exist
   - All function names exist
   - No references to removed code
</action>

<acceptance_criteria>
- CLAUDE.md line count accurate: matches wc -l main.py
- CLAUDE.md không reference removed code
- .planning/codebase/*.md accurate và consistent
- No broken file paths or function references
</acceptance_criteria>
</task>

<task id="5.5">
<read_first>
- All verification results from tasks 5.1-5.4
</read_first>

<action>
Create Phase 1 Testing Report:

Create file: .planning/phases/01-code-cleanup-low-risk/01-TESTING-REPORT.md

Content:
```markdown
# Phase 1 Testing Report

**Date**: 2026-04-23
**Phase**: 1 - Code Cleanup (Low Risk)
**Status**: COMPLETE

## Summary

Phase 1 cleanup completed successfully. All dead code removed, documentation updated, all features working.

## Code Changes

### Removed
- 7 step functions from workflow.py (~250 lines)
- pipeline_state dict from main.py (~15 lines)
- Duplicate TTS checkbox from main.py (~15 lines)
- Commented code blocks (~50 lines)
- Unused imports (~120 lines)

### Total Lines Removed: ~450 lines

### Files Modified
- src/modules/workflow.py: 600 → 350 lines
- main.py: 3000 → 2800 lines
- Documentation: CLAUDE.md, codebase maps

## Testing Results

### Smoke Test: ✅ PASS
- App launches without errors
- All tabs visible and functional
- Only one TTS checkbox (duplicate removed)
- Config save/load works

### Full Pipeline Test: ✅ PASS
- Complete pipeline executed successfully
- All 7 steps completed
- All output files created
- Video playback works
- Audio synchronized

### Code Quality: ✅ PASS
- No dead code: grep verified
- No unused imports: flake8 clean
- No commented code: grep verified
- All syntax valid: py_compile passed

### Documentation: ✅ PASS
- CLAUDE.md accurate
- Codebase maps updated
- No broken references

## Regression Testing

### Features Tested
- ✅ Video download (YouTube, Bilibili)
- ✅ Local file load
- ✅ Whisper transcription
- ✅ Google Translate
- ✅ Subtitle detection & covering
- ✅ SRT export (3 types)
- ✅ Subtitle burning
- ✅ VieNeu-TTS dubbing
- ✅ Config persistence
- ✅ UI controls

### All Features: ✅ WORKING

## Success Criteria

- ✅ No unused functions remain
- ✅ No commented-out code blocks
- ✅ No unused imports (flake8 clean)
- ✅ Documentation accurate
- ✅ All features still work

## Conclusion

Phase 1 completed successfully. Codebase is cleaner, more maintainable, and all functionality preserved. Ready to proceed to Phase 2 (Extract Controllers).

**Next**: /gsd-plan-phase 2
```

Save this report.
</action>

<acceptance_criteria>
- Testing report created at .planning/phases/01-code-cleanup-low-risk/01-TESTING-REPORT.md
- Report documents all test results
- Report confirms all success criteria met
- Report includes line counts and file changes
- Report status: COMPLETE
</acceptance_criteria>
</task>

</tasks>

<verification>
## All Tests Pass
- [ ] Smoke test: App launches, all tabs work
- [ ] Full pipeline test: Complete workflow succeeds
- [ ] Code quality: No dead code, no unused imports
- [ ] Documentation: Accurate and up-to-date
- [ ] Testing report: Created and complete

## Success Criteria Met
- [ ] No unused functions remain
- [ ] No commented-out code blocks
- [ ] No unused imports (flake8 clean)
- [ ] Documentation accurate
- [ ] All features still work (manual test)

## Ready for Phase 2
- [ ] Phase 1 complete
- [ ] Codebase clean
- [ ] All tests passing
- [ ] Documentation updated
</verification>

<must_haves>
- All tests pass (smoke + full pipeline)
- No regressions detected
- Testing report created
- Phase 1 marked complete
</must_haves>

<notes>
Wave 4 (final) because testing must happen AFTER all code and documentation changes.

This plan requires manual testing (autonomous: false) because:
- Need to visually verify UI
- Need to watch video playback
- Need to confirm audio quality
- Automated tests don't exist yet

Estimated time: 30-45 minutes for thorough testing.
</notes>

<rollback_plan>
If any test fails:
1. Document the failure in testing report
2. Identify which change caused the regression
3. Restore that specific change from backup
4. Re-test to confirm fix
5. Investigate root cause before re-attempting
</rollback_plan>
