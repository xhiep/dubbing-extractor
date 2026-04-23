"""Basic UI components - Reusable Tkinter widgets."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Any

class Button:
    """Reusable button component."""
    
    def __init__(self, parent, text: str, command: Callable, 
                 bg: str = "#4CAF50", fg: str = "white", 
                 width: int = 20, height: int = 2,
                 font: tuple = ("Arial", 10, "bold")):
        self.widget = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            width=width,
            height=height,
            font=font,
            relief=tk.FLAT,
            cursor="hand2"
        )
    
    def pack(self, **kwargs):
        self.widget.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        self.widget.grid(**kwargs)
        return self
    
    def config(self, **kwargs):
        self.widget.config(**kwargs)
        return self

class Label:
    """Reusable label component."""
    
    def __init__(self, parent, text: str = "", 
                 font: tuple = ("Arial", 10),
                 fg: str = "black", bg: str = None,
                 anchor: str = "w"):
        self.widget = tk.Label(
            parent,
            text=text,
            font=font,
            fg=fg,
            bg=bg,
            anchor=anchor
        )
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

class Input:
    """Reusable input/entry component."""
    
    def __init__(self, parent, placeholder: str = "",
                 width: int = 50, font: tuple = ("Arial", 10)):
        self.var = tk.StringVar()
        self.widget = tk.Entry(
            parent,
            textvariable=self.var,
            width=width,
            font=font
        )
        self.placeholder = placeholder
        if placeholder:
            self._show_placeholder()
    
    def _show_placeholder(self):
        self.widget.insert(0, self.placeholder)
        self.widget.config(fg="gray")
        self.widget.bind("<FocusIn>", self._on_focus_in)
        self.widget.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        if self.widget.get() == self.placeholder:
            self.widget.delete(0, tk.END)
            self.widget.config(fg="black")
    
    def _on_focus_out(self, event):
        if not self.widget.get():
            self.widget.insert(0, self.placeholder)
            self.widget.config(fg="gray")
    
    def get_value(self) -> str:
        val = self.var.get()
        return "" if val == self.placeholder else val
    
    def set_value(self, value: str):
        self.var.set(value)
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
                 font: tuple = ("Consolas", 9)):
        self.frame = tk.Frame(parent)
        
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.widget = tk.Text(
            self.frame,
            width=width,
            height=height,
            font=font,
            yscrollcommand=self.scrollbar.set,
            wrap=tk.WORD
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

class Checkbox:
    """Reusable checkbox component."""
    
    def __init__(self, parent, text: str, default: bool = False):
        self.var = tk.BooleanVar(value=default)
        self.widget = tk.Checkbutton(
            parent,
            text=text,
            variable=self.var
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
    """Reusable radio button group component."""
    
    def __init__(self, parent, options: list, default: str = None):
        self.var = tk.StringVar(value=default or options[0])
        self.buttons = []
        
        for option in options:
            btn = tk.Radiobutton(
                parent,
                text=option,
                variable=self.var,
                value=option
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
