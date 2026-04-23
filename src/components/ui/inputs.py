"""Basic input widgets."""
import tkinter as tk
from typing import Callable
from ..theme import T


class Button:
    """Reusable button — Apple Primary Blue by default."""

    def __init__(self, parent, text: str, command: Callable,
                 bg: str = None, fg: str = None,
                 width: int = 20, height: int = 2,
                 font: tuple = None):
        _bg = bg or T.ACCENT
        _fg = fg or T.BG_WHITE
        _font = font or T.FONT_BODY_SEMIBOLD
        self.widget = tk.Button(
            parent, text=text, command=command,
            bg=_bg, fg=_fg, width=width, height=height,
            font=_font, relief=tk.FLAT, cursor="hand2",
            activebackground=T.ACCENT_HOVER,
            activeforeground=T.BG_WHITE,
            borderwidth=0,
            padx=15, pady=4,
        )
        # Hover effect
        self.widget.bind("<Enter>", lambda _: self.widget.config(bg=T.ACCENT_HOVER))
        self.widget.bind("<Leave>", lambda _: self.widget.config(bg=_bg))

    def pack(self, **kwargs):
        self.widget.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.widget.grid(**kwargs)
        return self

    def config(self, **kwargs):
        self.widget.config(**kwargs)
        return self


class Input:
    """Reusable input/entry — Apple search-field style."""

    def __init__(self, parent, placeholder: str = "",
                 width: int = 50, font: tuple = None):
        _font = font or T.FONT_BODY
        self.var = tk.StringVar()
        self._placeholder = placeholder
        self._has_placeholder = False

        self.widget = tk.Entry(
            parent, textvariable=self.var, width=width, font=_font,
            bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
            relief=tk.FLAT, borderwidth=0,
            insertbackground=T.ACCENT,
            selectbackground=T.ACCENT,
            selectforeground=T.BG_WHITE,
        )

        if placeholder:
            self._show_placeholder()

    def _show_placeholder(self):
        self.widget.insert(0, self._placeholder)
        self.widget.config(fg=T.TEXT_DISABLED)
        self._has_placeholder = True
        self.widget.bind("<FocusIn>", self._on_focus_in)
        self.widget.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        if self._has_placeholder:
            self.widget.delete(0, tk.END)
            self.widget.config(fg=T.TEXT_PRIMARY)
            self._has_placeholder = False

    def _on_focus_out(self, event):
        if not self.widget.get():
            self.widget.insert(0, self._placeholder)
            self.widget.config(fg=T.TEXT_DISABLED)
            self._has_placeholder = True

    def get_value(self) -> str:
        if self._has_placeholder:
            return ""
        return self.var.get()

    def set_value(self, value: str):
        self.var.set(value)
        return self

    def pack(self, **kwargs):
        self.widget.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.widget.grid(**kwargs)
        return self


class Checkbox:
    """Reusable checkbox — Apple accent color."""

    def __init__(self, parent, text: str, default: bool = False):
        self.var = tk.BooleanVar(value=default)
        self.widget = tk.Checkbutton(
            parent, text=text, variable=self.var,
            font=T.FONT_BODY,
            bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
            activebackground=T.BG_LIGHT,
            activeforeground=T.TEXT_PRIMARY,
            selectcolor=T.BG_WHITE,
            relief=tk.FLAT, borderwidth=0,
            cursor="hand2",
        )

    def is_checked(self) -> bool:
        return self.var.get()

    def set_checked(self, value: bool):
        self.var.set(value)
        return self

    def pack(self, **kwargs):
        self.widget.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.widget.grid(**kwargs)
        return self


class RadioGroup:
    """Reusable radio button group."""

    def __init__(self, parent, options: list, default: str = None):
        self.var = tk.StringVar(value=default or options[0])
        self.buttons = []
        for option in options:
            btn = tk.Radiobutton(
                parent, text=option, variable=self.var, value=option,
                font=T.FONT_BODY,
                bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                activebackground=T.BG_LIGHT,
                selectcolor=T.BG_WHITE,
                relief=tk.FLAT, borderwidth=0,
                cursor="hand2",
            )
            self.buttons.append(btn)

    def get_selected(self) -> str:
        return self.var.get()

    def set_selected(self, value: str):
        self.var.set(value)
        return self

    def pack_all(self, **kwargs):
        for btn in self.buttons:
            btn.pack(**kwargs)
        return self

    def grid_all(self, start_row: int = 0, column: int = 0, **kwargs):
        for i, btn in enumerate(self.buttons):
            btn.grid(row=start_row + i, column=column, **kwargs)
        return self
