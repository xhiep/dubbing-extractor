"""Display widgets - Labels and text areas."""
import tkinter as tk
from ..theme import T


class Label:
    """Reusable label component."""

    def __init__(self, parent, text: str = "",
                 font: tuple = None,
                 fg: str = None, bg: str = None,
                 anchor: str = "w"):
        _font = font or T.FONT_BODY
        _fg = fg or T.TEXT_PRIMARY
        _bg = bg or T.BG_LIGHT
        self.widget = tk.Label(parent, text=text, font=_font, fg=_fg, bg=_bg, anchor=anchor)
        self.var = tk.StringVar(value=text)
        self.widget.config(textvariable=self.var)

    def set_text(self, text: str):
        self.var.set(text)
        return self

    def pack(self, **kwargs):
        self.widget.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.widget.grid(**kwargs)
        return self


class TextArea:
    """Reusable text area component with scrollbar."""

    def __init__(self, parent, width: int = 80, height: int = 20,
                 font: tuple = None):
        _font = font or T.FONT_MONO
        self.frame = tk.Frame(parent, bg=T.BG_LIGHT)
        self.scrollbar = tk.Scrollbar(self.frame, troughcolor=T.BG_LIGHT,
                                      bg=T.BORDER, relief=tk.FLAT,
                                      borderwidth=0)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widget = tk.Text(
            self.frame, width=width, height=height, font=_font,
            yscrollcommand=self.scrollbar.set, wrap=tk.WORD,
            bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
            relief=tk.FLAT, borderwidth=0,
            insertbackground=T.ACCENT,
            selectbackground=T.ACCENT,
            selectforeground=T.BG_WHITE,
            padx=8, pady=8,
        )
        self.widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.widget.yview)

    def append(self, text: str):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)
        return self

    def clear(self):
        self.widget.delete(1.0, tk.END)
        return self

    def get_text(self) -> str:
        return self.widget.get(1.0, tk.END)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self
