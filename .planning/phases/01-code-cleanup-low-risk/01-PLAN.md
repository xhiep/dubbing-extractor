---
wave: 1
plan_id: "01"
depends_on: []
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

# Plan 01: Remove Commented-Out Code

<objective>
Xóa tất cả commented-out code blocks (function definitions, class definitions, import statements, code blocks) từ toàn bộ codebase. Giữ lại docstrings, explanatory comments, TODO/FIXME comments, và license headers.
</objective>

<tasks>

<task id="1.1">
<read_first>
- main.py (toàn bộ file để tìm commented code)
- src/modules/workflow.py (toàn bộ file)
- All files in src/modules/ (scan for commented code)
- All files in src/components/ (scan for commented code)
</read_first>

<action>
Tìm và xóa commented-out code:

1. Search for commented function definitions:
   grep -rn "^[[:space:]]*#.*def " src/ main.py --include="*.py"

2. Search for commented class definitions:
   grep -rn "^[[:space:]]*#.*class " src/ main.py --include="*.py"

3. Search for commented import statements:
   grep -rn "^[[:space:]]*#.*import " src/ main.py --include="*.py"

4. For each file with commented code:
   - Read the file
   - Identify commented code blocks (not explanatory comments)
   - Remove commented code blocks
   - Keep:
     * Docstrings ("""...""")
     * Explanatory comments (# This handles edge case X)
     * TODO/FIXME comments
     * License headers
     * Section dividers (# ─────────)

5. Verify no functional code was removed:
   - Check syntax: python -m py_compile <file>
   - Check imports still work
</action>

<acceptance_criteria>
- grep -rn "^[[:space:]]*#.*def " src/ main.py returns no commented function definitions
- grep -rn "^[[:space:]]*#.*class " src/ main.py returns no commented class definitions
- grep -rn "^[[:space:]]*#.*import " src/ main.py returns no commented import statements
- All Python files still have valid syntax: find src/ -name "*.py" -exec python -m py_compile {} \;
- python -m py_compile main.py exits 0
- Explanatory comments, docstrings, TODO/FIXME preserved
- Estimated ~50-100 lines removed
</acceptance_criteria>
</task>

<task id="1.2">
<read_first>
- All modified files from task 1.1
</read_first>

<action>
Verify cleanup didn't break anything:

1. Check syntax on all modified files:
   find src/ -name "*.py" -exec python -m py_compile {} \;
   python -m py_compile main.py

2. Test imports:
   python -c "from src.modules.workflow import process_video"
   python -c "from src.modules.transcription.whisper_engine import transcribe"
   python -c "from src.modules.tts.vieneu_engine import VieNeuTTS"

3. Quick smoke test:
   python main.py
   # Verify app launches without import errors
</action>

<acceptance_criteria>
- All Python files compile without syntax errors
- All imports work
- App launches successfully
- No functionality broken
</acceptance_criteria>
</task>

</tasks>

<verification>
## Code Quality
- [ ] No commented function definitions remain
- [ ] No commented class definitions remain
- [ ] No commented import statements remain
- [ ] All syntax valid
- [ ] All imports work

## Functional Verification
- [ ] App launches: python main.py
- [ ] No import errors
- [ ] All tabs visible

## Preserved
- [ ] Docstrings intact
- [ ] Explanatory comments intact
- [ ] TODO/FIXME comments intact
- [ ] License headers intact
</verification>

<must_haves>
- All commented-out code removed
- No syntax errors introduced
- App still launches
- Explanatory comments preserved
</must_haves>

<rollback_plan>
If cleanup breaks anything:
1. Restore files from .planning/phases/01-code-cleanup-low-risk/old-plans/ backup
2. Identify which commented code was actually needed
3. Restore only that code
4. Re-test
</rollback_plan>
