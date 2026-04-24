"""Log tab view - output display and status."""
import tkinter as tk
from typing import Dict, Any

from ..components.ui import TextArea
from ..components.layout import Card
from ..components.theme import T


class LogView:
    """Log tab view - displays processing output and status messages."""

    def __init__(self, parent: tk.Widget, state: Dict[str, Any]):
        """Initialize log view.

        Args:
            parent: Parent widget (notebook)
            state: Dictionary to store widget references
                - Will set state['log_area'] to the TextArea widget
        """
        self.parent = parent
        self.state = state

    def build(self) -> tk.Frame:
        """Build and return the log tab frame.

        Returns:
            Configured tk.Frame ready to add to notebook
        """
        # Create tab frame (matches line 1295-1296 pattern)
        frame = tk.Frame(self.parent, padx=16, pady=16, bg=T.BG_WHITE)

        # Log card (matches lines 1298-1299)
        log_card = Card(frame, title="Nhat Ky Xu Ly")
        log_container = log_card.get_container()

        # Log text area (matches lines 1301-1304)
        log_area = TextArea(log_container, height=12, font=T.FONT_MONO)
        log_area.widget.config(bg=T.BG_LOG, fg=T.FG_LOG,
                               insertbackground=T.ACCENT)
        log_area.pack(fill=tk.BOTH, expand=True)

        # Pack card (matches line 1306)
        log_card.pack(fill=tk.BOTH, expand=True, pady=5)

        # Store reference for main.py to use
        self.state['log_area'] = log_area

        return frame
