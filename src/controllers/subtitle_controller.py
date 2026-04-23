"""Subtitle Controller - Subtitle tab event handlers.

Handles:
- Cover mode selection
- Subtitle preview
- Blur parameter adjustments
- Preset selection
- Font/margin adjustments

Note: Thin wrapper pattern - delegates to main.py functions.
"""
from typing import Dict, Any, Optional, Callable


class SubtitleController:
    """Subtitle tab controller - thin wrapper pattern."""

    def __init__(self,
                 on_cover_mode_changed_fn: Callable = None,
                 on_preset_changed_fn: Callable = None,
                 on_param_changed_fn: Callable = None):
        """Initialize subtitle controller.

        Args:
            on_cover_mode_changed_fn: Cover mode change handler
            on_preset_changed_fn: Preset change handler
            on_param_changed_fn: Parameter change handler (blur, font, margin, etc.)
        """
        self.on_cover_mode_changed_fn = on_cover_mode_changed_fn
        self.on_preset_changed_fn = on_preset_changed_fn
        self.on_param_changed_fn = on_param_changed_fn

    def on_cover_mode_changed(self, event=None):
        """Handle cover mode selection change."""
        if self.on_cover_mode_changed_fn:
            self.on_cover_mode_changed_fn(event)

    def on_preset_changed(self, event=None):
        """Handle subtitle preset selection."""
        if self.on_preset_changed_fn:
            self.on_preset_changed_fn(event)

    def on_param_changed(self, event=None):
        """Handle parameter changes (blur, font, margin, etc.)."""
        if self.on_param_changed_fn:
            self.on_param_changed_fn(event)
