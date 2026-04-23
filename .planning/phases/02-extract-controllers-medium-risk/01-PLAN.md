---
wave: 1
plan_id: "01"
depends_on: []
files_modified:
  - src/controllers/__init__.py
  - src/controllers/app_controller.py
  - src/controllers/source_controller.py
  - src/controllers/subtitle_controller.py
  - src/controllers/tts_controller.py
autonomous: true
requirements_addressed: []
---

# Plan 01: Create Controller Structure

<objective>
Tạo directory structure và skeleton files cho controllers. Thiết lập base pattern cho tất cả controllers sẽ follow.
</objective>

<tasks>

<task id="1.1">
<read_first>
- .planning/phases/02-extract-controllers-medium-risk/02-RESEARCH.md (Controller Pattern Design section)
- src/modules/workflow.py (để hiểu business logic interface)
- src/config.py (để hiểu config structure)
</read_first>

<action>
Tạo controller directory structure:

1. Create directory:
   mkdir -p src/controllers

2. Create __init__.py với exports:
   ```python
   """Controllers - Event handlers for UI interactions.
   
   Controllers mediate between View (UI) and Model (business logic).
   They are thin glue code with no business logic.
   """
   from .app_controller import AppController
   from .source_controller import SourceController
   from .subtitle_controller import SubtitleController
   from .tts_controller import TtsController
   
   __all__ = [
       'AppController',
       'SourceController',
       'SubtitleController',
       'TtsController',
   ]
   ```

3. Verify imports work:
   python -c "from src.controllers import AppController, SourceController, SubtitleController, TtsController"
</action>

<acceptance_criteria>
- src/controllers/ directory exists
- src/controllers/__init__.py exists và exports 4 controllers
- python -c "from src.controllers import AppController" exits 0
- Directory structure matches research document
</acceptance_criteria>
</task>

<task id="1.2">
<read_first>
- .planning/phases/02-extract-controllers-medium-risk/02-RESEARCH.md (Controller Structure example)
</read_first>

<action>
Create AppController skeleton:

File: src/controllers/app_controller.py

```python
"""App Controller - Application-level event handlers.

Handles:
- Config save/load
- Window close
- Tab switching
- Cross-controller coordination
"""
from typing import Dict, Any, Optional


class AppController:
    """Application-level controller."""
    
    def __init__(self, widgets: Dict[str, Any], config: Dict[str, Any]):
        """Initialize app controller.
        
        Args:
            widgets: Dict of widget references
                Required keys: TBD (will be determined during extraction)
            config: Global config dict
        """
        self.widgets = widgets
        self.config = config
    
    def on_config_save(self):
        """Handle config save request."""
        # TODO: Extract from main.py
        pass
    
    def on_config_load(self):
        """Handle config load request."""
        # TODO: Extract from main.py
        pass
    
    def on_window_close(self):
        """Handle window close event."""
        # TODO: Extract from main.py
        pass
    
    def on_tab_changed(self, event=None):
        """Handle tab switch event."""
        # TODO: Extract from main.py
        pass
```
</action>

<acceptance_criteria>
- src/controllers/app_controller.py exists
- AppController class defined with __init__ and 4 methods
- python -m py_compile src/controllers/app_controller.py exits 0
- from src.controllers import AppController works
</acceptance_criteria>
</task>

<task id="1.3">
<read_first>
- .planning/phases/02-extract-controllers-medium-risk/02-RESEARCH.md (source_controller responsibilities)
</read_first>

<action>
Create SourceController skeleton:

File: src/controllers/source_controller.py

```python
"""Source Controller - Source tab event handlers.

Handles:
- Start processing button
- Source input changes
- Video preview
- Metadata fetching
"""
from typing import Dict, Any, Optional, Callable


class SourceController:
    """Source tab controller."""
    
    def __init__(self, widgets: Dict[str, Any], config: Dict[str, Any]):
        """Initialize source controller.
        
        Args:
            widgets: Dict of widget references
                Required keys: TBD (will be determined during extraction)
            config: Global config dict
        """
        self.widgets = widgets
        self.config = config
    
    def on_start_clicked(self):
        """Handle start processing button click."""
        # TODO: Extract from main.py
        pass
    
    def on_source_changed(self, event=None):
        """Handle source input change."""
        # TODO: Extract from main.py
        pass
    
    def on_preview_clicked(self):
        """Handle preview button click."""
        # TODO: Extract from main.py
        pass
    
    def on_fetch_info(self):
        """Handle fetch video info request."""
        # TODO: Extract from main.py
        pass
    
    def _log_callback(self, message: str):
        """Callback for progress updates.
        
        Args:
            message: Progress message to display
        """
        # TODO: Extract from main.py
        pass
```
</action>

<acceptance_criteria>
- src/controllers/source_controller.py exists
- SourceController class defined with __init__ and 5 methods
- python -m py_compile src/controllers/source_controller.py exits 0
- from src.controllers import SourceController works
</acceptance_criteria>
</task>

<task id="1.4">
<read_first>
- .planning/phases/02-extract-controllers-medium-risk/02-RESEARCH.md (subtitle_controller responsibilities)
</read_first>

<action>
Create SubtitleController skeleton:

File: src/controllers/subtitle_controller.py

```python
"""Subtitle Controller - Subtitle tab event handlers.

Handles:
- Cover mode selection
- Subtitle preview
- Blur parameter adjustments
- Preset selection
- Font/margin adjustments
"""
from typing import Dict, Any, Optional


class SubtitleController:
    """Subtitle tab controller."""
    
    def __init__(self, widgets: Dict[str, Any], config: Dict[str, Any]):
        """Initialize subtitle controller.
        
        Args:
            widgets: Dict of widget references
                Required keys: TBD (will be determined during extraction)
            config: Global config dict
        """
        self.widgets = widgets
        self.config = config
    
    def on_cover_mode_changed(self, event=None):
        """Handle cover mode selection change."""
        # TODO: Extract from main.py
        pass
    
    def on_preview_subtitle(self):
        """Handle subtitle preview request."""
        # TODO: Extract from main.py
        pass
    
    def on_blur_params_changed(self, event=None):
        """Handle blur parameter changes."""
        # TODO: Extract from main.py
        pass
    
    def on_preset_changed(self, event=None):
        """Handle subtitle preset selection."""
        # TODO: Extract from main.py
        pass
    
    def on_subtitle_params_changed(self, event=None):
        """Handle subtitle parameter changes (font, margin, etc.)."""
        # TODO: Extract from main.py
        pass
```
</action>

<acceptance_criteria>
- src/controllers/subtitle_controller.py exists
- SubtitleController class defined with __init__ and 5 methods
- python -m py_compile src/controllers/subtitle_controller.py exits 0
- from src.controllers import SubtitleController works
</acceptance_criteria>
</task>

<task id="1.5">
<read_first>
- .planning/phases/02-extract-controllers-medium-risk/02-RESEARCH.md (tts_controller responsibilities)
</read_first>

<action>
Create TtsController skeleton:

File: src/controllers/tts_controller.py

```python
"""TTS Controller - TTS tab event handlers.

Handles:
- TTS mode selection
- Voice selection
- TTS preview
- Reference audio browsing
- Volume adjustments
"""
from typing import Dict, Any, Optional


class TtsController:
    """TTS tab controller."""
    
    def __init__(self, widgets: Dict[str, Any], config: Dict[str, Any]):
        """Initialize TTS controller.
        
        Args:
            widgets: Dict of widget references
                Required keys: TBD (will be determined during extraction)
            config: Global config dict
        """
        self.widgets = widgets
        self.config = config
    
    def on_dub_mode_changed(self, event=None):
        """Handle TTS mode selection change."""
        # TODO: Extract from main.py
        pass
    
    def on_voice_changed(self, event=None):
        """Handle voice selection change."""
        # TODO: Extract from main.py
        pass
    
    def on_tts_preview(self):
        """Handle TTS preview request."""
        # TODO: Extract from main.py
        pass
    
    def on_ref_audio_browse(self):
        """Handle reference audio browse button."""
        # TODO: Extract from main.py
        pass
    
    def on_volume_changed(self, event=None):
        """Handle volume slider changes."""
        # TODO: Extract from main.py
        pass
```
</action>

<acceptance_criteria>
- src/controllers/tts_controller.py exists
- TtsController class defined with __init__ and 5 methods
- python -m py_compile src/controllers/tts_controller.py exits 0
- from src.controllers import TtsController works
</acceptance_criteria>
</task>

<task id="1.6">
<read_first>
- All created controller files
</read_first>

<action>
Verify controller structure:

1. Check all files exist:
   ls -la src/controllers/

2. Verify all imports work:
   python -c "from src.controllers import AppController, SourceController, SubtitleController, TtsController; print('All imports OK')"

3. Verify syntax:
   find src/controllers/ -name "*.py" -exec python -m py_compile {} \;

4. Count lines:
   wc -l src/controllers/*.py
   # Should be ~200-250 lines total (skeleton code)
</action>

<acceptance_criteria>
- All 5 files exist in src/controllers/
- All imports work without errors
- All files have valid Python syntax
- Total ~200-250 lines of skeleton code
- Ready for extraction in next plans
</acceptance_criteria>
</task>

</tasks>

<verification>
## Structure Verification
- [ ] src/controllers/ directory created
- [ ] __init__.py exports all 4 controllers
- [ ] All 4 controller files created
- [ ] All controllers have skeleton methods

## Code Quality
- [ ] All syntax valid: find src/controllers/ -name "*.py" -exec python -m py_compile {} \;
- [ ] All imports work: from src.controllers import *
- [ ] Docstrings present for all classes and methods

## Readiness
- [ ] Controllers ready for extraction
- [ ] Pattern established for all controllers
- [ ] No functionality yet (just structure)
</verification>

<must_haves>
- Controller directory structure created
- All 4 controller skeleton files
- All imports working
- All syntax valid
- Ready for extraction
</must_haves>

<notes>
Wave 1 because this is foundation work - must be done before any extraction.

This plan creates structure only - no functionality yet. Actual event handler extraction happens in subsequent plans.

Skeleton methods have TODO comments to guide extraction.
</notes>
