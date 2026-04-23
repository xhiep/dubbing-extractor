---
wave: 2
plan_id: "03"
depends_on: ["01", "02"]
files_modified:
  - main.py
  - src/modules/workflow.py
  - src/modules/transcription/whisper_engine.py
  - src/modules/transcription/translator.py
  - src/modules/transcription/srt_generator.py
  - src/modules/downloader/ytdlp_wrapper.py
  - src/modules/downloader/platform_detector.py
  - src/modules/downloader/url_resolver.py
  - src/modules/video_processing/ffmpeg_wrapper.py
  - src/modules/video_processing/subtitle_detector.py
  - src/modules/video_processing/subtitle_burner.py
  - src/modules/video_processing/video_encoder.py
  - src/modules/tts/vieneu_engine.py
  - src/modules/tts/audio_dubber.py
  - src/components/ui/inputs.py
  - src/components/ui/widgets.py
  - src/components/ui/display.py
  - src/components/layout/containers.py
  - src/components/theme.py
  - src/components/hooks/state.py
autonomous: true
requirements_addressed: []
---

# Plan 03: Remove Commented Code and Unused Imports

<objective>
Xóa tất cả commented-out code blocks và unused imports từ toàn bộ codebase. Giữ lại explanatory comments và docstrings.
</objective>

<tasks>

<task id="3.1">
<read_first>
- main.py
- src/modules/workflow.py
- Tất cả files trong src/modules/, src/components/
</read_first>

<action>
Tìm và xóa commented-out code (không phải explanatory comments):

1. Search for commented code:
   grep -r "^#.*def \|^#.*class \|^# *import \|^# *from " src/ main.py --include="*.py"

2. For each match, determine if it's:
   - Commented code (DELETE)
   - Explanatory comment (KEEP)
   - TODO/FIXME (KEEP if actionable, DELETE if stale)

3. Patterns to DELETE:
   - # def old_function(...):
   - # class OldClass:
   - # import unused_module
   - # from module import unused
   - Multi-line commented code blocks

4. Patterns to KEEP:
   - # This function does X because Y (explanation)
   - # TODO: Add feature Z (actionable)
   - # FIXME: Bug in edge case (actionable)
   - Docstrings ("""...""")

5. Manual review each file after automated search.
</action>

<acceptance_criteria>
- grep -r "^#.*def " src/ main.py --include="*.py" returns no commented function definitions
- grep -r "^#.*class " src/ main.py --include="*.py" returns no commented class definitions
- Explanatory comments still present (manual review)
- Docstrings intact
- All files still have valid Python syntax
</acceptance_criteria>
</task>

<task id="3.2">
<read_first>
- main.py
- All files in src/modules/
- All files in src/components/
</read_first>

<action>
Remove unused imports using flake8:

1. Run flake8 to detect unused imports:
   flake8 --select=F401 src/ main.py

2. For each F401 error (unused import):
   - Verify import is truly unused (grep for usage)
   - Remove the import line
   - Re-run flake8 to verify

3. Common unused imports to check:
   - import sys (often unused)
   - import os (when only pathlib is used)
   - from typing import X (when X not used in type hints)
   - from datetime import X (when X not used)

4. After removing each import:
   - Verify syntax: python -m py_compile <file>
   - Verify app still runs

5. Repeat until flake8 --select=F401 returns no errors.
</action>

<acceptance_criteria>
- flake8 --select=F401 src/ main.py exits 0 (no unused imports)
- All files have valid syntax: find src/ -name "*.py" -exec python -m py_compile {} \;
- App launches: python main.py
- No import errors at runtime
</acceptance_criteria>
</task>

<task id="3.3">
<read_first>
- All modified files
</read_first>

<action>
Final verification pass:

1. Run full syntax check:
   find src/ -name "*.py" -exec python -m py_compile {} \;
   python -m py_compile main.py

2. Check for any remaining issues:
   flake8 src/ main.py (full check, not just F401)

3. Launch app and verify:
   python main.py
   - All tabs load
   - No import errors
   - No runtime errors

4. Count lines saved:
   wc -l main.py src/modules/**/*.py src/components/**/*.py
</action>

<acceptance_criteria>
- All Python files compile without syntax errors
- flake8 --select=F401 returns 0 unused imports
- App launches successfully
- All tabs visible and functional
- No import errors in console
</acceptance_criteria>
</task>

</tasks>

<verification>
## Functional Verification
- [ ] App launches: python main.py
- [ ] No import errors at startup
- [ ] All tabs load correctly
- [ ] No runtime errors when clicking through UI

## Code Quality
- [ ] No commented code: grep -r "^#.*def \|^#.*class " src/ main.py
- [ ] No unused imports: flake8 --select=F401 src/ main.py
- [ ] All syntax valid: find src/ -name "*.py" -exec python -m py_compile {} \;
- [ ] Explanatory comments preserved (manual review)

## Regression Testing
- [ ] Launch app, check all tabs
- [ ] Click through all UI controls
- [ ] Verify no missing functionality
- [ ] Run quick pipeline test if possible
</verification>

<must_haves>
- No commented-out code blocks
- No unused imports (flake8 clean)
- Explanatory comments preserved
- All syntax valid
- App launches and runs
</must_haves>

<notes>
Wave 2 because it depends on Plans 01 and 02 completing first (those plans remove large blocks of code, which may make some imports unused).

This is the most tedious task but also very safe - removing comments and unused imports cannot break functionality.
</notes>

<rollback_plan>
If removal breaks imports:
1. Check error message for missing import
2. Restore that specific import
3. Verify it's actually used (may be indirect usage)
4. Re-run flake8 to confirm it's needed
</rollback_plan>
