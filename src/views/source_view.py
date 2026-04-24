"""Source tab view - video input and processing controls."""
import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, Callable

from ..components.ui import Button, Input, Label
from ..components.layout import Card, Row
from ..components.theme import T


class SourceView:
    """Source tab view - video source input, model selection, and step-by-step controls."""

    def __init__(self,
                 parent: tk.Widget,
                 state: Dict[str, Any],
                 callbacks: Dict[str, Callable]):
        """Initialize source view.

        Args:
            parent: Parent widget (notebook)
            state: Dictionary of tk state variables
                - source_state: StringVar for video source input
                - whisper_model_state: StringVar for Whisper model selection
                - pipeline_state: Dict for step-by-step processing state
                - preview_guard: Dict for preview state management
            callbacks: Dictionary of callback functions
                - paste_clipboard: Function to paste from clipboard
                - browse_file: Function to open file dialog
                - load_source_preview: Function to load video preview
                - log: Function to log messages
        """
        self.parent = parent
        self.state = state
        self.callbacks = callbacks
        self.widgets = {}

    def build(self) -> tk.Frame:
        """Build and return the source tab frame.

        Returns:
            Configured tk.Frame ready to add to notebook
        """
        # Create tab frame
        frame = tk.Frame(self.parent, padx=16, pady=16, bg=T.BG_WHITE)

        # Video source section
        source_card = Card(frame, title="📹 Nguồn Video")
        source_container = source_card.get_container()

        source_input = Input(source_container, placeholder="Dán link video (YouTube, Bilibili, Douyin) hoặc chọn file local...", width=70)
        source_input.var = self.state['source_state'].var
        source_input.pack(fill=tk.X, pady=5)
        source_input.widget.bind("<Return>", lambda _e: self.callbacks['load_source_preview'](force=True))
        source_input.widget.bind("<FocusOut>", lambda _e: self.callbacks['load_source_preview'](force=True))

        btn_row = Row(source_container, spacing=8, bg=T.BG_LIGHT)
        Button(btn_row.frame, text="Dan Link", command=lambda: self.callbacks['paste_clipboard'](),
               bg=T.ACCENT, fg=T.BG_WHITE, width=14, height=1,
               font=T.FONT_BODY).widget.pack(side=tk.LEFT, padx=(0, 8))
        Button(btn_row.frame, text="Chon File", command=lambda: self.callbacks['browse_file'](),
               bg=T.SURFACE_DARK_2, fg=T.BG_WHITE, width=14, height=1,
               font=T.FONT_BODY).widget.pack(side=tk.LEFT)
        btn_row.pack(anchor=tk.W, pady=(4, 0))

        source_hint = Label(
            source_container,
            text="Ho tro: YouTube, Bilibili, Douyin | File video local (MP4, AVI, MKV, MOV)",
            font=T.FONT_SMALL,
            fg=T.TEXT_SECONDARY,
            bg=T.BG_LIGHT,
        )
        source_hint.pack(anchor=tk.W, pady=(8, 0))

        source_card.pack(fill=tk.X, pady=5)

        # ── Pipeline state ──────────────────────────────────────────────────
        pipeline_state = self.state['pipeline_state']

        # Màu nút theo trạng thái
        STEP_COLOR_IDLE    = "#95a5a6"
        STEP_COLOR_RUNNING = "#3498db"
        STEP_COLOR_DONE    = "#27ae60"
        STEP_COLOR_ERROR   = "#e74c3c"

        # ── Card "Chạy Từng Bước" trong tab Nguồn ───────────────────────────
        steps_card = Card(frame, title="🔢 Chạy Từng Bước")
        steps_container = steps_card.get_container()

        # Hàng nút các bước
        step_btns_row = tk.Frame(steps_container, bg="white")
        step_btns_row.pack(fill=tk.X, pady=(0, 8))

        STEP_LABELS = [
            "1: Tải Video",
            "2: Nhận Dạng",
            "3: Dịch",
            "4: Render Video",
            "5: Burn Sub + Lồng",
        ]
        step_btn_widgets = []
        for i, label in enumerate(STEP_LABELS):
            btn = tk.Button(
                step_btns_row,
                text=f"Bước {label}",
                bg=STEP_COLOR_IDLE,
                fg="white",
                font=("Segoe UI", 9, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=6,
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=(0, 6))
            step_btn_widgets.append(btn)

        # Hàng trạng thái + nút Reset
        status_row = tk.Frame(steps_container, bg="white")
        status_row.pack(fill=tk.X, pady=(0, 12))

        pipeline_status_var = tk.StringVar(value="● Chưa bắt đầu")
        pipeline_status_label = tk.Label(
            status_row,
            textvariable=pipeline_status_var,
            font=("Segoe UI", 9),
            fg="#7f8c8d",
            bg="white",
            anchor="w",
        )
        pipeline_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        reset_pipeline_btn = tk.Button(
            status_row,
            text="↺ Reset",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
        )
        reset_pipeline_btn.pack(side=tk.RIGHT)

        # Separator
        tk.Frame(steps_container, height=1, bg="#e0e0e0").pack(fill=tk.X, pady=(0, 10))

        # ── Ô edit SRT ──────────────────────────────────────────────────────
        srt_edit_label = tk.Label(
            steps_container,
            text="✏️ Sửa Bản Dịch (SRT) — Chỉnh sửa sau Bước 3, trước khi chạy Bước 4",
            font=("Segoe UI", 9, "bold"),
            fg="#2c3e50",
            bg="white",
            anchor="w",
        )
        srt_edit_label.pack(fill=tk.X, pady=(0, 4))

        srt_edit_ctrl_row = tk.Frame(steps_container, bg="white")
        srt_edit_ctrl_row.pack(fill=tk.X, pady=(0, 6))

        open_srt_btn = tk.Button(
            srt_edit_ctrl_row,
            text="📂 Mở File Ngoài",
            bg="#2196F3",
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            state=tk.DISABLED,
            cursor="hand2",
        )
        open_srt_btn.pack(side=tk.LEFT, padx=(0, 6))

        reload_srt_btn = tk.Button(
            srt_edit_ctrl_row,
            text="🔄 Tải Lại",
            bg="#FF9800",
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            state=tk.DISABLED,
            cursor="hand2",
        )
        reload_srt_btn.pack(side=tk.LEFT, padx=(0, 6))

        save_srt_btn = tk.Button(
            srt_edit_ctrl_row,
            text="💾 Lưu Thay Đổi",
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            state=tk.DISABLED,
            cursor="hand2",
        )
        save_srt_btn.pack(side=tk.LEFT)

        srt_file_label_var = tk.StringVar(value="(Chưa có file SRT)")
        tk.Label(
            srt_edit_ctrl_row,
            textvariable=srt_file_label_var,
            font=("Segoe UI", 8),
            fg="#95a5a6",
            bg="white",
        ).pack(side=tk.LEFT, padx=(12, 0))

        srt_edit_frame = tk.Frame(steps_container, bg="white")
        srt_edit_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        srt_editor = tk.Text(
            srt_edit_frame,
            height=14,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50",
            relief=tk.SUNKEN,
            borderwidth=1,
            state=tk.DISABLED,
            wrap=tk.NONE,
        )
        srt_scrollbar_y = ttk.Scrollbar(srt_edit_frame, orient=tk.VERTICAL, command=srt_editor.yview)
        srt_scrollbar_x = ttk.Scrollbar(steps_container, orient=tk.HORIZONTAL, command=srt_editor.xview)
        srt_editor.configure(yscrollcommand=srt_scrollbar_y.set, xscrollcommand=srt_scrollbar_x.set)
        srt_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        srt_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        srt_scrollbar_x.pack(fill=tk.X)

        steps_card.pack(fill=tk.BOTH, expand=True, pady=5)

        # Store widget references for controller access
        self.widgets['source_input'] = source_input
        self.widgets['step_btn_widgets'] = step_btn_widgets
        self.widgets['pipeline_status_var'] = pipeline_status_var
        self.widgets['pipeline_status_label'] = pipeline_status_label
        self.widgets['reset_pipeline_btn'] = reset_pipeline_btn
        self.widgets['open_srt_btn'] = open_srt_btn
        self.widgets['reload_srt_btn'] = reload_srt_btn
        self.widgets['save_srt_btn'] = save_srt_btn
        self.widgets['srt_file_label_var'] = srt_file_label_var
        self.widgets['srt_editor'] = srt_editor
        self.widgets['STEP_COLOR_IDLE'] = STEP_COLOR_IDLE
        self.widgets['STEP_COLOR_RUNNING'] = STEP_COLOR_RUNNING
        self.widgets['STEP_COLOR_DONE'] = STEP_COLOR_DONE
        self.widgets['STEP_COLOR_ERROR'] = STEP_COLOR_ERROR

        return frame

    def get_widgets(self) -> Dict[str, Any]:
        """Get widget references for controller access.

        Returns:
            Dictionary of widget references
        """
        return self.widgets
