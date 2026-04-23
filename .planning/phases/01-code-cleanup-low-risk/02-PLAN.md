---
wave: 1
plan_id: "02"
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

# Plan 02: Remove Unused Imports

<objective>
Xóa tất cả unused imports từ toàn bộ codebase sử dụng flake8. Chỉ xóa imports thực sự không được sử dụng, không ảnh hưởng đến functionality.
</objective>

<tasks>

<task id="2.1">
<read_first>
- main.py (để verify imports trước khi xóa)
- src/modules/workflow.py (để verify imports)
</read_first>

<action>
Detect và xóa unused imports:

1. Run flake8 to find unused imports:
   flake8 --select=F401 src/ main.py > unused_imports.txt

2. For each unused import reported:
   - Read the file
   - Verify import is truly unused (flake8 is accurate but double-check)
   - Remove the import line
   - Keep imports that:
     * Are used in type hints
     * Are re-exported (__all__)
     * Are used in docstring examples
     * Are imported for side effects

3. Process files in this order:
   - main.py first (most imports)
   - src/modules/workflow.py
   - Other src/modules/ files
   - src/components/ files

4. After each file:
   - Verify syntax: python -m py_compile <file>
   - Verify imports still work
</action>

<acceptance_criteria>
- flake8 --select=F401 src/ main.py returns no unused imports
- All Python files still have valid syntax
- python -m py_compile main.py exits 0
- find src/ -name "*.py" -exec python -m py_compile {} \; exits 0
- All necessary imports preserved
- Estimated ~20-50 lines removed
</acceptance_criteria>
</task>

<task id="2.2">
<read_first>
- All modified files from task 2.1
</read_first>

<action>
Verify import cleanup didn't break anything:

1. Check syntax on all modified files:
   find src/ -name "*.py" -exec python -m py_compile {} \;
   python -m py_compile main.py

2. Test critical imports:
   python -c "from src.modules.workflow import process_video"
   python -c "from src.modules.transcription.whisper_engine import transcribe"
   python -c "from src.modules.transcription.translator import translate"
   python -c "from src.modules.tts.vieneu_engine import VieNeuTTS"
   python -c "from src.modules.downloader.ytdlp_wrapper import download"

3. Launch app to verify all imports work:
   python main.py
   # Verify app launches without import errors
</action>

<acceptance_criteria>
- All Python files compile without syntax errors
- All critical imports work
- App launches successfully
- No ImportError exceptions
- No functionality broken
</acceptance_criteria>
</task>

</tasks>

<verification>
## Code Quality
- [ ] flake8 --select=F401 returns no unused imports
- [ ] All syntax valid
- [ ] All necessary imports preserved

## Functional Verification
- [ ] App launches: python main.py
- [ ] No ImportError exceptions
- [ ] All tabs visible
- [ ] All modules importable

## Regression Testing
- [ ] process_video importable
- [ ] transcribe importable
- [ ] translate importable
- [ ] VieNeuTTS importable
- [ ] download importable
</verification>

<must_haves>
- All unused imports removed
- No syntax errors introduced
- App still launches
- All necessary imports preserved
</must_haves>

<rollback_plan>
If import removal breaks anything:
1. Check error message for missing import
2. Restore that specific import
3. Re-test
4. Update flake8 ignore if import is needed but appears unused
</rollback_plan>
