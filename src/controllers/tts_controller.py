"""TTS Controller - TTS tab event handlers.

Handles:
- TTS mode selection
- Voice selection
- TTS preview
- Reference audio browsing
- Volume adjustments

Note: Thin wrapper pattern - delegates to main.py functions.
"""
from typing import Dict, Any, Optional, Callable


class TtsController:
    """TTS tab controller - thin wrapper pattern."""

    def __init__(self,
                 on_dub_mode_changed_fn: Callable = None,
                 on_voice_changed_fn: Callable = None,
                 play_tts_preview_fn: Callable = None,
                 stop_preview_audio_fn: Callable = None):
        """Initialize TTS controller.

        Args:
            on_dub_mode_changed_fn: Dub mode change handler
            on_voice_changed_fn: Voice selection change handler
            play_tts_preview_fn: TTS preview play handler
            stop_preview_audio_fn: Stop preview audio handler
        """
        self.on_dub_mode_changed_fn = on_dub_mode_changed_fn
        self.on_voice_changed_fn = on_voice_changed_fn
        self.play_tts_preview_fn = play_tts_preview_fn
        self.stop_preview_audio_fn = stop_preview_audio_fn

    def on_dub_mode_changed(self, event=None):
        """Handle TTS mode selection change."""
        if self.on_dub_mode_changed_fn:
            self.on_dub_mode_changed_fn(event)

    def on_voice_changed(self, event=None):
        """Handle voice selection change."""
        if self.on_voice_changed_fn:
            self.on_voice_changed_fn(event)

    def on_tts_preview(self):
        """Handle TTS preview request."""
        if self.play_tts_preview_fn:
            self.play_tts_preview_fn()

    def on_stop_preview(self):
        """Handle stop preview request."""
        if self.stop_preview_audio_fn:
            self.stop_preview_audio_fn()
