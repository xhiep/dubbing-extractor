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
