"""Layout components - Reusable layout containers."""
import tkinter as tk
from typing import Optional, Callable
from ..theme import T


class Card:
    """Card component — Apple style: flat, light gray, no border, subtle shadow via bg contrast."""

    def __init__(self, parent, title: str = None,
                 bg: str = None,
                 border_color: str = None,
                 padding: int = 12):
        _bg = bg or T.BG_LIGHT
        # Flat frame — Apple cards use background contrast, not borders
        self.frame = tk.Frame(parent, bg=_bg, relief=tk.FLAT, borderwidth=0)

        self.inner = tk.Frame(self.frame, bg=_bg)
        self.inner.pack(padx=padding, pady=padding, fill=tk.BOTH, expand=True)

        if title:
            title_label = tk.Label(
                self.inner,
                text=title,
                font=T.FONT_CARD_TITLE,
                bg=_bg,
                fg=T.TEXT_PRIMARY,
                anchor="w",
            )
            title_label.pack(fill=tk.X, pady=(0, 8))
            # Thin separator line (1px, subtle)
            sep = tk.Frame(self.inner, height=1, bg=T.BORDER)
            sep.pack(fill=tk.X, pady=(0, 10))

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self

    def get_container(self):
        return self.inner


class Section:
    """Section component — Labeled section with separator."""

    def __init__(self, parent, title: str,
                 title_font: tuple = None,
                 title_color: str = None):
        _font = title_font or T.FONT_LABEL
        _color = title_color or T.TEXT_SECONDARY
        self.frame = tk.Frame(parent, bg=T.BG_LIGHT)

        title_label = tk.Label(
            self.frame, text=title.upper(),
            font=_font, fg=_color, bg=T.BG_LIGHT, anchor="w",
        )
        title_label.pack(fill=tk.X, pady=(10, 4))

        separator = tk.Frame(self.frame, height=1, bg=T.BORDER)
        separator.pack(fill=tk.X, pady=(0, 8))

        self.content = tk.Frame(self.frame, bg=T.BG_LIGHT)
        self.content.pack(fill=tk.BOTH, expand=True)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self

    def get_container(self):
        return self.content


class Row:
    """Row component — Horizontal layout."""

    def __init__(self, parent, spacing: int = 8, align: str = "left",
                 bg: str = None):
        _bg = bg or T.BG_LIGHT
        self.frame = tk.Frame(parent, bg=_bg)
        self.spacing = spacing
        self.align = align
        self.children = []

    def add(self, widget, flex: int = 0):
        if self.children:
            spacer = tk.Frame(self.frame, width=self.spacing, bg=self.frame.cget("bg"))
            spacer.pack(side=tk.LEFT)
        if flex > 0:
            widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        else:
            widget.pack(side=tk.LEFT)
        self.children.append(widget)
        return self

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self


class Column:
    """Column component — Vertical layout."""

    def __init__(self, parent, spacing: int = 8, bg: str = None):
        _bg = bg or T.BG_LIGHT
        self.frame = tk.Frame(parent, bg=_bg)
        self.spacing = spacing
        self.children = []

    def add(self, widget, flex: int = 0):
        if self.children:
            spacer = tk.Frame(self.frame, height=self.spacing,
                              bg=self.frame.cget("bg"))
            spacer.pack(fill=tk.X)
        if flex > 0:
            widget.pack(fill=tk.BOTH, expand=True)
        else:
            widget.pack(fill=tk.X)
        self.children.append(widget)
        return self

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self


class Grid:
    """Grid component — Grid layout."""

    def __init__(self, parent, columns: int = 2,
                 row_spacing: int = 8, col_spacing: int = 8,
                 bg: str = None):
        _bg = bg or T.BG_LIGHT
        self.frame = tk.Frame(parent, bg=_bg)
        self.columns = columns
        self.row_spacing = row_spacing
        self.col_spacing = col_spacing
        self.current_row = 0
        self.current_col = 0

    def add(self, widget, colspan: int = 1, rowspan: int = 1, sticky: str = "ew"):
        widget.grid(
            row=self.current_row, column=self.current_col,
            columnspan=colspan, rowspan=rowspan,
            sticky=sticky,
            padx=(0, self.col_spacing), pady=(0, self.row_spacing),
        )
        self.current_col += colspan
        if self.current_col >= self.columns:
            self.current_col = 0
            self.current_row += 1
        return self

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self


class Spacer:
    """Spacer component — Empty space."""

    def __init__(self, parent, width: int = 0, height: int = 0, bg: str = None):
        _bg = bg or T.BG_LIGHT
        self.frame = tk.Frame(parent, width=width, height=height, bg=_bg)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self
