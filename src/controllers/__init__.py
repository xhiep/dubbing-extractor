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
