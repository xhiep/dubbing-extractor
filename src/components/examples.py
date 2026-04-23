"""Example: Video Input Component - Reusable component for video URL/file input."""
import tkinter as tk
from tkinter import filedialog
from typing import Callable, Optional

from ..ui import Button, Input, Label
from ..layout import Card, Row
from ..hooks import use_tk_state

class VideoInputComponent:
    """Reusable video input component.
    
    Usage:
        video_input = VideoInputComponent(
            parent=root,
            on_change=lambda url: print(f"URL changed: {url}")
        )
        video_input.pack(fill=tk.X, padx=10, pady=10)
    """
    
    def __init__(self, parent, 
                 on_change: Optional[Callable[[str], None]] = None,
                 placeholder: str = "Paste video URL or select file..."):
        self.on_change = on_change
        
        # State
        self.url_state = use_tk_state("string", "")
        if on_change:
            self.url_state.trace(on_change)
        
        # Create card container
        self.card = Card(parent, title="Video Source")
        container = self.card.get_container()
        
        # Create row layout
        row = Row(container, spacing=10)
        
        # Input field
        self.input = Input(
            container,
            placeholder=placeholder,
            width=60
        )
        self.input.var = self.url_state.var  # Bind to state
        row.add(self.input.widget, flex=1)
        
        # Paste button
        paste_btn = Button(
            container,
            text="Paste",
            command=self._paste_from_clipboard,
            bg="#2196F3",
            width=10,
            height=1
        )
        row.add(paste_btn.widget)
        
        # Browse button
        browse_btn = Button(
            container,
            text="Browse",
            command=self._browse_file,
            bg="#FF9800",
            width=10,
            height=1
        )
        row.add(browse_btn.widget)
        
        row.pack(fill=tk.X)
    
    def _paste_from_clipboard(self):
        try:
            clipboard = self.input.widget.clipboard_get()
            self.url_state.set(clipboard.strip())
        except:
            pass
    
    def _browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mkv *.mov *.flv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.url_state.set(filename)
    
    def get_value(self) -> str:
        return self.url_state.get()
    
    def set_value(self, value: str):
        self.url_state.set(value)
    
    def pack(self, **kwargs):
        self.card.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        self.card.grid(**kwargs)
        return self

class SettingsComponent:
    """Reusable settings component.
    
    Usage:
        settings = SettingsComponent(
            parent=root,
            options={
                "whisper_model": ["tiny", "base", "small", "medium", "large"],
                "cover_mode": ["none", "blur", "blackbar"]
            },
            on_change=lambda key, value: print(f"{key} = {value}")
        )
        settings.pack(fill=tk.X, padx=10, pady=10)
    """
    
    def __init__(self, parent,
                 options: dict,
                 defaults: dict = None,
                 on_change: Optional[Callable[[str, str], None]] = None):
        self.options = options
        self.on_change = on_change
        self.states = {}
        
        # Create card
        self.card = Card(parent, title="Settings")
        container = self.card.get_container()
        
        # Create option rows
        for key, values in options.items():
            default = defaults.get(key) if defaults else values[0]
            self._create_option_row(container, key, values, default)
    
    def _create_option_row(self, parent, key: str, values: list, default: str):
        row_frame = tk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=5)
        
        # Label
        label = Label(row_frame, text=f"{key.replace('_', ' ').title()}:")
        label.widget.pack(side=tk.LEFT, padx=(0, 10))
        
        # State
        state = use_tk_state("string", default)
        self.states[key] = state
        
        if self.on_change:
            state.trace(lambda value: self.on_change(key, value))
        
        # Radio buttons
        for value in values:
            rb = tk.Radiobutton(
                row_frame,
                text=value,
                variable=state.var,
                value=value
            )
            rb.pack(side=tk.LEFT, padx=5)
    
    def get_values(self) -> dict:
        return {key: state.get() for key, state in self.states.items()}
    
    def set_value(self, key: str, value: str):
        if key in self.states:
            self.states[key].set(value)
    
    def pack(self, **kwargs):
        self.card.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        self.card.grid(**kwargs)
        return self

class LogViewerComponent:
    """Reusable log viewer component.
    
    Usage:
        log_viewer = LogViewerComponent(parent=root)
        log_viewer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        log_viewer.append("Processing started...\n")
    """
    
    def __init__(self, parent, height: int = 15):
        # Create card
        self.card = Card(parent, title="Log")
        container = self.card.get_container()
        
        # Create text area
        from ..ui import TextArea
        self.text_area = TextArea(container, height=height)
        self.text_area.pack(fill=tk.BOTH, expand=True)
    
    def append(self, text: str):
        self.text_area.append(text)
        return self
    
    def clear(self):
        self.text_area.clear()
        return self
    
    def pack(self, **kwargs):
        self.card.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        self.card.grid(**kwargs)
        return self
