"""Adjust tab view - subtitle parameters and preview canvas."""
import json
import subprocess
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, Callable

from ..components.ui import Button, Input, Label, Checkbox
from ..components.layout import Card, Row
from ..components.theme import T
from ..modules.video_processing.ffmpeg_wrapper import ffmpeg_cmd, get_dims, probe_duration
from ..modules.video_processing.subtitle_burner import compute_subtitle_layout
from ..utils.ui_helpers import expand_band_from_center, shift_band


class AdjustView:
    """Adjust tab view - subtitle adjustment controls and preview canvas with scrolling."""

    def __init__(self,
                 parent: tk.Widget,
                 state: Dict[str, Any],
                 callbacks: Dict[str, Callable],
                 here: Path,
                 subtitle_presets: Dict[str, Any]):
        """Initialize adjust view.

        Args:
            parent: Parent widget (notebook)
            state: Dictionary of tk state variables
                - cover_mode_state: StringVar for cover mode selection
                - whisper_model_state: StringVar for Whisper model selection
                - burn_sub_state: BooleanVar for burn subtitle option
                - preset_state: StringVar for preset selection
                - subtitle_offset_state: DoubleVar for subtitle offset
                - subtitle_scale_state: DoubleVar for subtitle timing scale
                - video_speed_state: DoubleVar for video speed
                - font_scale_state: DoubleVar for font scale
                - font_size_state: IntVar for font size
                - margin_state: IntVar for margin
                - chars_per_line_state: IntVar for chars per line
                - blur_padding_state: IntVar for blur padding
                - cover_offset_state: IntVar for cover offset
                - blur_power_state: IntVar for blur power
                - preview_text_state: StringVar for preview text
                - preview_time_state: DoubleVar for preview time
                - preview_guard: Dict for preview state management
                - preset_guard: Dict for preset state management
            callbacks: Dictionary of callback functions
                - mark_preset_custom: Function to mark preset as custom
                - apply_selected_preset: Function to apply selected preset
                - update_preview: Function to update preview canvas
                - log: Function to log messages
            here: Path to project root directory
            subtitle_presets: Dictionary of subtitle presets
        """
        self.parent = parent
        self.state = state
        self.callbacks = callbacks
        self.here = here
        self.subtitle_presets = subtitle_presets
        self.widgets = {}

        # Canvas and scroll widgets (will be set in build())
        self.adjust_canvas = None
        self.adjust_scrollbar = None
        self.adjust_body = None
        self.adjust_window = None
        self.adjust_left = None
        self.adjust_right = None

        # Preview widgets
        self.preview_canvas = None
        self.preview_info_var = None
        self.preview_status_var = None
        self.preview_time_label_var = None
        self.preview_seek = None
        self.preview_marker_canvas = None
        self.preview_text_box = None
        self.preview_play_btn = None
        self.preview_refresh_btn = None
        self.preview_reset_pos_btn = None
        self.preview_reset_style_btn = None
        self.last_output_var = None
        self.open_output_btn = None

    def build(self) -> tk.Frame:
        """Build and return the adjust tab frame with scrolling.

        Returns:
            Configured tk.Frame ready to add to notebook
        """
        # Create tab frame
        frame = tk.Frame(self.parent, padx=16, pady=16, bg=T.BG_WHITE)

        # ── Scroll Setup ──────────────────────────────────────────
        # CRITICAL: Keep this entire block together (see RESEARCH.md Pitfall 5)

        # Canvas + Scrollbar
        self.adjust_canvas = tk.Canvas(frame, highlightthickness=0, bg=T.BG_WHITE)
        self.adjust_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL,
                                              command=self.adjust_canvas.yview)
        self.adjust_canvas.configure(yscrollcommand=self.adjust_scrollbar.set)
        self.adjust_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.adjust_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame inside canvas
        self.adjust_body = tk.Frame(self.adjust_canvas, bg=T.BG_WHITE)
        self.adjust_window = self.adjust_canvas.create_window((0, 0),
                                                               window=self.adjust_body,
                                                               anchor="nw")

        # Bind scroll events
        self.adjust_body.bind("<Configure>", self._sync_adjust_scroll)
        self.adjust_canvas.bind("<Configure>", self._resize_adjust_window)

        # Split layout
        adjust_split = tk.Frame(self.adjust_body, bg=T.BG_WHITE)
        adjust_split.pack(fill=tk.BOTH, expand=True)
        adjust_split.grid_columnconfigure(0, weight=0, minsize=420)
        adjust_split.grid_columnconfigure(1, weight=1)
        adjust_split.grid_rowconfigure(0, weight=1)

        self.adjust_left = tk.Frame(adjust_split, bg=T.BG_WHITE)
        self.adjust_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.adjust_right = tk.Frame(adjust_split, bg=T.BG_WHITE)
        self.adjust_right.grid(row=0, column=1, sticky="nsew")
        self.adjust_right.grid_rowconfigure(0, weight=1)
        self.adjust_right.grid_columnconfigure(0, weight=1)

        # ── Left Panel: Settings ──────────────────────────────────
        self._build_settings_panel()

        # ── Right Panel: Preview Canvas ───────────────────────────
        self._build_preview_panel()

        # Bind recursive scroll (must be after all widgets are created)
        self._bind_scroll_recursive(self.adjust_body)

        # Store widget references
        self.widgets['adjust_canvas'] = self.adjust_canvas
        self.widgets['adjust_body'] = self.adjust_body
        self.widgets['adjust_left'] = self.adjust_left
        self.widgets['adjust_right'] = self.adjust_right
        self.widgets['preview_canvas'] = self.preview_canvas
        self.widgets['preview_info_var'] = self.preview_info_var
        self.widgets['preview_status_var'] = self.preview_status_var
        self.widgets['preview_time_label_var'] = self.preview_time_label_var
        self.widgets['preview_seek'] = self.preview_seek
        self.widgets['preview_marker_canvas'] = self.preview_marker_canvas
        self.widgets['preview_text_box'] = self.preview_text_box
        self.widgets['preview_play_btn'] = self.preview_play_btn
        self.widgets['preview_refresh_btn'] = self.preview_refresh_btn
        self.widgets['preview_reset_pos_btn'] = self.preview_reset_pos_btn
        self.widgets['preview_reset_style_btn'] = self.preview_reset_style_btn
        self.widgets['last_output_var'] = self.last_output_var
        self.widgets['open_output_btn'] = self.open_output_btn

        return frame

    def _build_settings_panel(self):
        """Build the left panel with subtitle parameter controls."""
        settings_card = Card(self.adjust_left, title="Cai Dat Phu De Va Vung Che")
        settings_container = settings_card.get_container()

        def _lbl(parent, text, width=18):
            return tk.Label(parent, text=text, width=width, anchor="w",
                            font=T.FONT_BODY, fg=T.TEXT_PRIMARY, bg=T.BG_LIGHT)

        def _hint(parent, text):
            return tk.Label(parent, text=text, font=T.FONT_SMALL,
                            fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT)

        # Cover mode
        cover_label = Label(settings_container, text="Che Subtitle Goc:")
        cover_label.pack(anchor=tk.W)
        cover_frame = tk.Frame(settings_container, bg=T.BG_LIGHT)
        cover_frame.pack(fill=tk.X, pady=5)
        for mode in ["none", "blur", "blackbar"]:
            tk.Radiobutton(
                cover_frame,
                text={"none": "Khong che", "blur": "Lam mo", "blackbar": "Thanh den"}[mode],
                variable=self.state['cover_mode_state'].var,
                value=mode,
                font=T.FONT_BODY, bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                activebackground=T.BG_LIGHT, selectcolor=T.BG_WHITE,
                relief=tk.FLAT, cursor="hand2",
            ).pack(side=tk.LEFT, padx=5)

        # Whisper model
        model_label = Label(settings_container, text="Mo Hinh Whisper:")
        model_label.pack(anchor=tk.W, pady=(10, 0))
        model_frame = tk.Frame(settings_container, bg=T.BG_LIGHT)
        model_frame.pack(fill=tk.X, pady=5)
        for model in ["tiny", "base", "small", "medium", "large"]:
            tk.Radiobutton(model_frame, text=model, variable=self.state['whisper_model_state'].var, value=model,
                           font=T.FONT_BODY, bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                           activebackground=T.BG_LIGHT, selectcolor=T.BG_WHITE,
                           relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Burn subtitle
        burn_check = Checkbox(settings_container, text="Ghi phu de vao video", default=self.state['burn_sub_state'].get())
        burn_check.var = self.state['burn_sub_state'].var
        burn_check.pack(anchor=tk.W, pady=5)

        # Preset selection
        preset_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        preset_row.pack(fill=tk.X, pady=(12, 6))
        _lbl(preset_row, "Mau Phu De:").pack(side=tk.LEFT)
        preset_combo = ttk.Combobox(
            preset_row, textvariable=self.state['preset_state'].var,
            values=list(self.subtitle_presets.keys()), state="readonly", width=16,
        )
        preset_combo.pack(side=tk.LEFT)
        _hint(preset_row, "Chon preset hoac de Tuy Chinh de chinh tay").pack(side=tk.LEFT, padx=8)

        # Timing parameters
        timing_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        timing_row.pack(fill=tk.X, pady=(12, 6))
        _lbl(timing_row, "Lech Thoi Gian (s):").pack(side=tk.LEFT)
        tk.Spinbox(timing_row, from_=-30.0, to=30.0, increment=0.1, textvariable=self.state['subtitle_offset_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(timing_row, "Am = hien som hon, duong = hien tre hon").pack(side=tk.LEFT, padx=8)

        speed_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        speed_row.pack(fill=tk.X, pady=6)
        _lbl(speed_row, "Ti Le Timing Sub:").pack(side=tk.LEFT)
        tk.Spinbox(speed_row, from_=0.5, to=2.0, increment=0.05, textvariable=self.state['subtitle_scale_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(speed_row, "1.0 = thoi gian goc").pack(side=tk.LEFT, padx=8)

        video_speed_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        video_speed_row.pack(fill=tk.X, pady=6)
        _lbl(video_speed_row, "Toc Do Video:").pack(side=tk.LEFT)
        tk.Spinbox(video_speed_row, from_=0.25, to=4.0, increment=0.05, textvariable=self.state['video_speed_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(video_speed_row, "1.0 = goc | >1 nhanh hon | <1 cham hon").pack(side=tk.LEFT, padx=8)

        # Font parameters
        font_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        font_row.pack(fill=tk.X, pady=6)
        _lbl(font_row, "Ti Le Co Chu:").pack(side=tk.LEFT)
        tk.Spinbox(font_row, from_=0.5, to=2.5, increment=0.1, textvariable=self.state['font_scale_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(font_row, "Dung khi ghi phu de vao video").pack(side=tk.LEFT, padx=8)

        font_size_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        font_size_row.pack(fill=tk.X, pady=6)
        _lbl(font_size_row, "Co Chu:").pack(side=tk.LEFT)
        tk.Spinbox(font_size_row, from_=0, to=96, increment=1, textvariable=self.state['font_size_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(font_size_row, "0 = tu dong theo ti le co chu").pack(side=tk.LEFT, padx=8)

        margin_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        margin_row.pack(fill=tk.X, pady=6)
        _lbl(margin_row, "Lech Vi Tri Doc:").pack(side=tk.LEFT)
        tk.Spinbox(margin_row, from_=-240, to=240, increment=4, textvariable=self.state['margin_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(margin_row, "So pixel lech so voi vi tri mac dinh").pack(side=tk.LEFT, padx=8)

        chars_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        chars_row.pack(fill=tk.X, pady=6)
        _lbl(chars_row, "Ky Tu Moi Dong:").pack(side=tk.LEFT)
        tk.Spinbox(chars_row, from_=20, to=80, increment=1, textvariable=self.state['chars_per_line_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(chars_row, "Dung khi xuat file SRT").pack(side=tk.LEFT, padx=8)

        # Blur/cover parameters
        blur_pad_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        blur_pad_row.pack(fill=tk.X, pady=6)
        _lbl(blur_pad_row, "Noi Vung Che (px):").pack(side=tk.LEFT)
        tk.Spinbox(blur_pad_row, from_=0, to=200, increment=2, textvariable=self.state['blur_padding_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(blur_pad_row, "Noi doi xung tu tam vung subtitle cu").pack(side=tk.LEFT, padx=8)

        blur_power_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        blur_power_row.pack(fill=tk.X, pady=6)
        _lbl(blur_power_row, "Do Mo:").pack(side=tk.LEFT)
        tk.Spinbox(blur_power_row, from_=1, to=10, increment=1, textvariable=self.state['blur_power_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(blur_power_row, "Chi ap dung khi chon che do Lam mo").pack(side=tk.LEFT, padx=8)

        cover_offset_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
        cover_offset_row.pack(fill=tk.X, pady=6)
        _lbl(cover_offset_row, "Day Vung Che Len:").pack(side=tk.LEFT)
        tk.Spinbox(cover_offset_row, from_=-240, to=240, increment=2, textvariable=self.state['cover_offset_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(cover_offset_row, "Duong = day len, am = keo xuong").pack(side=tk.LEFT, padx=8)

        settings_card.pack(fill=tk.X, pady=5)

        # Output card
        output_card = Card(self.adjust_left, title="Output Gan Nhat")
        output_container = output_card.get_container()
        self.last_output_var = tk.StringVar(value="")
        tk.Label(output_container, textvariable=self.last_output_var, anchor="w",
                 justify=tk.LEFT, fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT,
                 font=T.FONT_SMALL).pack(fill=tk.X)
        self.open_output_btn = tk.Button(output_container, text="Mo Thu Muc Render",
                                    bg=T.ACCENT, fg=T.BG_WHITE,
                                    font=T.FONT_BODY, relief=tk.FLAT,
                                    cursor="hand2", width=18)
        self.open_output_btn.pack(anchor=tk.W, pady=(8, 0))
        output_card.pack(fill=tk.X, pady=5)

    def _build_preview_panel(self):
        """Build the right panel with preview canvas."""
        preview_card = Card(self.adjust_right, title="Xem Truoc Va Can Chinh")
        preview_container = preview_card.get_container()

        self.preview_info_var = tk.StringVar(value="")
        preview_info = tk.Label(preview_container, textvariable=self.preview_info_var,
                                anchor="w", justify=tk.LEFT,
                                fg=T.TEXT_PRIMARY, bg=T.BG_LIGHT,
                                font=T.FONT_SMALL)
        preview_info.pack(fill=tk.X, pady=(0, 8))

        self.preview_status_var = tk.StringVar(value="Chua tai xem truoc.")
        tk.Label(preview_container, textvariable=self.preview_status_var,
                 anchor="w", justify=tk.LEFT,
                 fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT,
                 font=T.FONT_SMALL).pack(fill=tk.X, pady=(0, 8))

        preview_controls = tk.Frame(preview_container, bg=T.BG_LIGHT)
        preview_controls.pack(fill=tk.X, pady=(0, 10))

        def _ctrl_btn(parent, text, width, accent=False):
            bg = T.ACCENT if accent else T.SURFACE_DARK_2
            b = tk.Button(parent, text=text, width=width,
                          bg=bg, fg=T.BG_WHITE,
                          font=T.FONT_BODY, relief=tk.FLAT, cursor="hand2")
            return b

        self.preview_play_btn = _ctrl_btn(preview_controls, "Phat", 10, accent=True)
        self.preview_play_btn.pack(side=tk.LEFT)

        self.preview_refresh_btn = _ctrl_btn(preview_controls, "Tai Lai Khung", 12)
        self.preview_refresh_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.preview_reset_pos_btn = _ctrl_btn(preview_controls, "Dat Lai Vi Tri", 14)
        self.preview_reset_pos_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.preview_reset_style_btn = _ctrl_btn(preview_controls, "Dat Lai Kieu", 12)
        self.preview_reset_style_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.preview_time_label_var = tk.StringVar(value="00:00 / 00:00")
        tk.Label(preview_controls, textvariable=self.preview_time_label_var,
                 fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT,
                 font=T.FONT_SMALL).pack(side=tk.RIGHT)

        self.preview_seek = tk.Scale(
            preview_container,
            from_=0, to=100, orient=tk.HORIZONTAL,
            showvalue=False, resolution=0.1, length=860,
            bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
            troughcolor=T.BORDER, highlightthickness=0,
            activebackground=T.ACCENT,
        )
        self.preview_seek.pack(fill=tk.X, pady=(0, 10))

        self.preview_marker_canvas = tk.Canvas(preview_container, height=54,
                                          bg=T.BG_CARD_DARK,
                                          highlightthickness=1,
                                          highlightbackground=T.SURFACE_DARK_1)
        self.preview_marker_canvas.pack(fill=tk.X, pady=(0, 10))

        self.preview_text_box = tk.Text(preview_container, height=2, font=T.FONT_BODY,
                                   bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
                                   relief=tk.FLAT, borderwidth=0,
                                   insertbackground=T.ACCENT,
                                   padx=6, pady=4)
        self.preview_text_box.pack(fill=tk.X, pady=(0, 10))
        self.preview_text_box.insert("1.0", self.state['preview_text_state'].get())

        self.preview_canvas = tk.Canvas(preview_container, width=900, height=360,
                                   bg=T.BG_CARD_DARK, highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)

        preview_card.pack(fill=tk.BOTH, expand=True, pady=5)

    def _sync_adjust_scroll(self, _event=None):
        """Sync scroll region to canvas content."""
        self.adjust_canvas.configure(scrollregion=self.adjust_canvas.bbox("all"))

    def _resize_adjust_window(self, event):
        """Resize canvas window to match canvas width."""
        self.adjust_canvas.itemconfigure(self.adjust_window, width=event.width)

    def _wheel_adjust(self, event):
        """Handle mouse wheel scrolling."""
        if self.state['preview_guard'].get("over_preview"):
            return "break"
        delta = event.delta
        if delta == 0 and getattr(event, "num", None) == 4:
            delta = 120
        elif delta == 0 and getattr(event, "num", None) == 5:
            delta = -120
        if delta:
            self.adjust_canvas.yview_scroll(int(-delta / 120), "units")
            return "break"
        return None

    def _bind_scroll_recursive(self, widget):
        """Recursively bind scroll events to widget and children."""
        widget.bind("<MouseWheel>", self._wheel_adjust, add="+")
        widget.bind("<Button-4>", self._wheel_adjust, add="+")
        widget.bind("<Button-5>", self._wheel_adjust, add="+")
        for child in widget.winfo_children():
            self._bind_scroll_recursive(child)

    def get_widgets(self) -> Dict[str, Any]:
        """Get widget references for controller access.

        Returns:
            Dictionary of widget references
        """
        return self.widgets
