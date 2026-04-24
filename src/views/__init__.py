"""View components for GUI tabs.

Each view class builds and returns a configured tk.Frame for a tab.
Views are pure UI - no business logic, only widget creation and layout.
"""

from .log_view import LogView
from .dub_view import DubView
from .source_view import SourceView
from .adjust_view import AdjustView

__all__ = ["LogView", "DubView", "SourceView", "AdjustView"]
