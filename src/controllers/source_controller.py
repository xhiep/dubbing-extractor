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
