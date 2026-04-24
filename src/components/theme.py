"""Apple-inspired design tokens for Tkinter.

Adapted from DESIGN.md — maps Apple web design system to Tkinter constraints.
SF Pro is used when available; falls back to Segoe UI (Windows), then Helvetica/Arial.
"""

_FONT_STACK = "SF Pro Display", "Segoe UI", "Helvetica Neue", "Arial"
_FONT_STACK_TEXT = "SF Pro Text", "Segoe UI", "Helvetica Neue", "Arial"
_FONT_MONO = "Consolas", "SF Mono", "Menlo", "Courier New"

# Pick first available font (Tkinter can't enumerate easily, so provide tuple directly)
_D = _FONT_STACK[1]   # Display: Segoe UI (closest to SF Pro on Windows)
_T = _FONT_STACK_TEXT[1]  # Text
_M = _FONT_MONO[0]


class T:
    """Design tokens — Apple-inspired."""

    # ── Colors ──────────────────────────────────────────────────────────────
    # Backgrounds
    BG_DARK = "#000000"       # Hero dark sections
    BG_LIGHT = "#f5f5f7"      # Default light background (not pure white)
    BG_WHITE = "#ffffff"      # Input fields, text areas
    BG_CARD_DARK = "#1d1d1f"  # Cards on dark sections

    # Surfaces (dark elevation)
    SURFACE_DARK_1 = "#272729"
    SURFACE_DARK_2 = "#1d1d1f"

    # Text
    TEXT_PRIMARY = "#1d1d1f"            # Near-black — primary on light bg
    TEXT_SECONDARY = "#6e6e73"          # Gray — labels, hints
    TEXT_DISABLED = "#aeaeb2"           # Disabled / placeholder
    TEXT_ON_DARK = "#ffffff"            # White text on dark bg
    TEXT_ON_DARK_SEC = "#a1a1a6"        # Secondary text on dark bg

    # Interactive
    ACCENT = "#0071e3"          # Apple Blue — CTA buttons, focus rings
    ACCENT_HOVER = "#0077ed"    # Slightly brighter on hover
    ACCENT_DARK = "#2997ff"     # Links on dark backgrounds
    LINK = "#0066cc"            # Inline links on light bg

    # Structure
    BORDER = "#d2d2d7"          # Subtle separator lines (1px)
    BORDER_FOCUS = "#0071e3"    # Focus ring

    # Log area (dark terminal feel)
    BG_LOG = "#1d1d1f"
    FG_LOG = "#e0e0e5"

    # State colors (for notifications, alerts, status indicators)
    SUCCESS = "#34c759"      # Green - success states
    WARNING = "#ff9500"      # Orange - warning states
    ERROR = "#ff3b30"        # Red - error states
    INFO = "#0071e3"         # Blue - info states

    # ── Typography (Tkinter font tuples) ────────────────────────────────────
    # Display — SF Pro Display / Segoe UI, large sizes
    FONT_HERO = (_D, 20, "bold")       # Window title
    FONT_SECTION = (_D, 13, "bold")    # Card / section headings
    FONT_CARD_TITLE = (_D, 11, "bold") # Card title labels
    FONT_LABEL = (_T, 9)               # Field labels, micro text (uppercase in Section)

    # Body — SF Pro Text / Segoe UI
    FONT_BODY = (_T, 10)               # Standard body text, inputs
    FONT_BODY_SEMIBOLD = (_T, 10, "bold")  # Buttons, emphasized body
    FONT_SMALL = (_T, 9)               # Hints, secondary labels
    FONT_CAPTION = (_T, 8)             # Captions, fine print

    # Mono — for log area and SRT editor
    FONT_MONO = (_M, 9)

    # ── Spacing (multiples of 8px base) ─────────────────────────────────────
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32


class DarkTheme:
    """Dark mode design tokens."""

    # ── Colors ──────────────────────────────────────────────────────────────
    # Backgrounds
    BG_DARK = "#000000"
    BG_LIGHT = "#1d1d1f"      # Main background in dark mode
    BG_WHITE = "#2c2c2e"      # Input fields, text areas
    BG_CARD_DARK = "#1c1c1e"  # Cards

    # Surfaces
    SURFACE_DARK_1 = "#2c2c2e"
    SURFACE_DARK_2 = "#3a3a3c"

    # Text
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#98989d"
    TEXT_DISABLED = "#636366"
    TEXT_ON_DARK = "#ffffff"
    TEXT_ON_DARK_SEC = "#98989d"

    # Interactive
    ACCENT = "#0a84ff"          # Brighter blue for dark mode
    ACCENT_HOVER = "#409cff"
    ACCENT_DARK = "#0a84ff"
    LINK = "#2997ff"

    # Structure
    BORDER = "#38383a"
    BORDER_FOCUS = "#0a84ff"

    # Log area
    BG_LOG = "#000000"
    FG_LOG = "#e5e5ea"

    # State colors (same as light mode)
    SUCCESS = "#32d74b"      # Slightly brighter green for dark mode
    WARNING = "#ff9f0a"      # Slightly brighter orange
    ERROR = "#ff453a"        # Slightly brighter red
    INFO = "#0a84ff"         # Brighter blue

    # Typography (same as light mode)
    FONT_HERO = T.FONT_HERO
    FONT_SECTION = T.FONT_SECTION
    FONT_CARD_TITLE = T.FONT_CARD_TITLE
    FONT_LABEL = T.FONT_LABEL
    FONT_BODY = T.FONT_BODY
    FONT_BODY_SEMIBOLD = T.FONT_BODY_SEMIBOLD
    FONT_SMALL = T.FONT_SMALL
    FONT_CAPTION = T.FONT_CAPTION
    FONT_MONO = T.FONT_MONO

    # Spacing (same as light mode)
    SPACE_XS = T.SPACE_XS
    SPACE_SM = T.SPACE_SM
    SPACE_MD = T.SPACE_MD
    SPACE_LG = T.SPACE_LG
    SPACE_XL = T.SPACE_XL


class ThemeManager:
    """Manages theme switching between light and dark modes."""

    def __init__(self):
        self._current_theme = T  # Default to light theme
        self._is_dark = False

    @property
    def current(self):
        """Get current theme."""
        return self._current_theme

    @property
    def is_dark(self) -> bool:
        """Check if dark mode is active."""
        return self._is_dark

    def toggle(self):
        """Toggle between light and dark themes."""
        if self._is_dark:
            self._current_theme = T
            self._is_dark = False
        else:
            self._current_theme = DarkTheme
            self._is_dark = True
        return self._current_theme

    def set_light(self):
        """Set light theme."""
        self._current_theme = T
        self._is_dark = False
        return self._current_theme

    def set_dark(self):
        """Set dark theme."""
        self._current_theme = DarkTheme
        self._is_dark = True
        return self._current_theme


# Global theme manager instance
theme_manager = ThemeManager()
