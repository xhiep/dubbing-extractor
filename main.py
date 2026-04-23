#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dubbing Extractor v2 - Main Entry Point.

Modular architecture with component-based UI.
"""

# ── Standard Library ──────────────────────────────────────────
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Third-Party ───────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk
import winsound

# ── Local Modules ─────────────────────────────────────────────
# Add src to path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from src.utils.suppress_warnings import install_stderr_filter
install_stderr_filter()

from src.utils.logger import setup_logging
from src.config import config, load_app_config, save_app_config
from src.modules.workflow import (
    process_video,
    step1_prepare,
    step2_transcribe,
    step3_translate,
    step4_cover,
    step5_export,
    step6_burn,
    step7_dub,
)
from src.modules.downloader.ytdlp_wrapper import check_source_preconditions, fetch_preview_info
from src.modules.video_processing.ffmpeg_wrapper import ffmpeg_cmd, get_dims, probe_duration
from src.modules.video_processing.subtitle_burner import compute_subtitle_layout
from src.modules.tts import (
    get_vieneu_error,
    is_vieneu_available,
    list_preset_voices,
    release_tts_resources,
    render_dubbed_outputs,
    synthesize_speech,
)
from src.components.ui import Button, Input, Label, TextArea, Checkbox
from src.components.layout import Card, Section, Row, Column
from src.components.theme import T
from src.components.hooks import use_tk_state
from src.controllers import SourceController, SubtitleController, TtsController, AppController
from src.utils.file_utils import is_local_file
from src.utils.runtime_env import ensure_local_runtime_env
from src.utils.ui_helpers import expand_band_from_center, shift_band

ensure_local_runtime_env()

LOG_DIR = HERE / "output"
APP_LOG_FILE = LOG_DIR / "app_debug.log"
APP_LOG_BACKUP_FILE = LOG_DIR / "app_debug.log.1"
APP_LOG_MAX_BYTES = 2 * 1024 * 1024


def _rotate_app_log_if_needed() -> None:
    try:
        if not APP_LOG_FILE.exists() or APP_LOG_FILE.stat().st_size < APP_LOG_MAX_BYTES:
            return
        if APP_LOG_BACKUP_FILE.exists():
            APP_LOG_BACKUP_FILE.unlink()
        APP_LOG_FILE.replace(APP_LOG_BACKUP_FILE)
    except Exception:
        pass


def _write_app_log_line(message: str) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        _rotate_app_log_if_needed()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(APP_LOG_FILE, "a", encoding="utf-8", errors="replace") as handle:
            handle.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

SUBTITLE_PRESETS = {
    "Tùy Chỉnh": None,
    "Mặc Định": {
        "subtitle_font_scale": 1.0,
        "subtitle_font_size": 0,
        "subtitle_margin_px": 0,
        "srt_max_chars_per_line": 45,
        "subtitle_offset_sec": 0.0,
        "subtitle_timing_scale": 1.0,
    },
    "Chữ Lớn": {
        "subtitle_font_scale": 1.4,
        "subtitle_font_size": 0,
        "subtitle_margin_px": 16,
        "srt_max_chars_per_line": 34,
        "subtitle_offset_sec": 0.0,
        "subtitle_timing_scale": 1.0,
    },
    "Gọn": {
        "subtitle_font_scale": 0.85,
        "subtitle_font_size": 0,
        "subtitle_margin_px": -8,
        "srt_max_chars_per_line": 52,
        "subtitle_offset_sec": 0.0,
        "subtitle_timing_scale": 1.0,
    },
    "TikTok": {
        "subtitle_font_scale": 1.55,
        "subtitle_font_size": 0,
        "subtitle_margin_px": 44,
        "srt_max_chars_per_line": 24,
        "subtitle_offset_sec": 0.0,
        "subtitle_timing_scale": 1.0,
    },
    "Kiểu Anime": {
        "subtitle_font_scale": 1.15,
        "subtitle_font_size": 30,
        "subtitle_margin_px": 30,
        "srt_max_chars_per_line": 32,
        "subtitle_offset_sec": 0.0,
        "subtitle_timing_scale": 1.0,
    },
}

def _apply_ttk_theme(style: ttk.Style) -> None:
    """Apply Apple-inspired ttk styles across all widget types."""
    BG = T.BG_LIGHT
    FG = T.TEXT_PRIMARY
    ACC = T.ACCENT
    BORDER = T.BORDER
    SEL_BG = T.ACCENT
    SEL_FG = T.BG_WHITE
    FONT = T.FONT_BODY
    FONT_SM = T.FONT_SMALL

    style.theme_use("clam")

    # ── Notebook (tabs) ──────────────────────────────────────────────────────
    style.configure("TNotebook",
                    background=BG, borderwidth=0, tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
                    background=BG, foreground=T.TEXT_SECONDARY,
                    font=FONT, padding=[16, 8],
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", T.BG_WHITE), ("active", T.BG_WHITE)],
              foreground=[("selected", FG), ("active", FG)])

    # ── Scrollbar ────────────────────────────────────────────────────────────
    style.configure("TScrollbar",
                    background=BORDER, troughcolor=BG,
                    borderwidth=0, relief=tk.FLAT,
                    arrowsize=12)
    style.map("TScrollbar",
              background=[("active", T.TEXT_DISABLED)])

    # ── Combobox ─────────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    fieldbackground=T.BG_WHITE, background=BG,
                    foreground=FG, selectbackground=SEL_BG,
                    selectforeground=SEL_FG,
                    borderwidth=1, relief=tk.FLAT,
                    font=FONT, padding=[6, 4])
    style.map("TCombobox",
              fieldbackground=[("readonly", T.BG_WHITE)],
              foreground=[("readonly", FG)])

    # ── Spinbox ──────────────────────────────────────────────────────────────
    style.configure("TSpinbox",
                    fieldbackground=T.BG_WHITE, background=BG,
                    foreground=FG, borderwidth=1, relief=tk.FLAT,
                    font=FONT, padding=[4, 3])

    # ── Frame / LabelFrame ───────────────────────────────────────────────────
    style.configure("TFrame", background=BG)
    style.configure("TLabelframe", background=BG, foreground=FG,
                    borderwidth=1, relief=tk.FLAT)
    style.configure("TLabelframe.Label", background=BG, foreground=FG,
                    font=T.FONT_LABEL)

    # ── Label ────────────────────────────────────────────────────────────────
    style.configure("TLabel", background=BG, foreground=FG, font=FONT)

    # ── Button (ttk — for any remaining ttk.Button) ──────────────────────────
    style.configure("TButton",
                    background=ACC, foreground=T.BG_WHITE,
                    font=FONT, borderwidth=0, relief=tk.FLAT, padding=[12, 6])
    style.map("TButton",
              background=[("active", T.ACCENT_HOVER), ("disabled", BORDER)],
              foreground=[("disabled", T.TEXT_DISABLED)])

    # ── Checkbutton / Radiobutton ────────────────────────────────────────────
    style.configure("TCheckbutton",
                    background=BG, foreground=FG, font=FONT)
    style.configure("TRadiobutton",
                    background=BG, foreground=FG, font=FONT)

    # ── Scale ────────────────────────────────────────────────────────────────
    style.configure("Horizontal.TScale",
                    background=BG, troughcolor=BORDER,
                    sliderthickness=14)


def launch_gui():
    """Launch main GUI application."""
    # ═══════════════════════════════════════════════════════════
    # SECTION 1: Window Setup
    # ═══════════════════════════════════════════════════════════
    root = tk.Tk()
    root.title("Dubbing Extractor v2.5")
    root.geometry("1120x800")
    root.minsize(1000, 720)

    style = ttk.Style()
    _apply_ttk_theme(style)

    root.configure(bg=T.BG_LIGHT)

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: Configuration & State Management
    # ═══════════════════════════════════════════════════════════
    # Load saved config
    app_config = load_app_config()
    legacy_presets = {
        "Custom": "Tùy Chỉnh",
        "Default": "Mặc Định",
        "Large": "Chữ Lớn",
        "Compact": "Gọn",
        "Anime": "Kiểu Anime",
        "Tuy Chinh": "Tùy Chỉnh",
        "Mac Dinh": "Mặc Định",
        "Chu Lon": "Chữ Lớn",
        "Gon": "Gọn",
        "Kieu Anime": "Kiểu Anime",
    }
    if app_config.get("subtitle_preset") in legacy_presets:
        app_config["subtitle_preset"] = legacy_presets[app_config["subtitle_preset"]]
    
    # State management
    source_state = use_tk_state("string", app_config.get("source_input", ""))
    cover_mode_state = use_tk_state("string", app_config.get("cover_mode", "blur"))
    whisper_model_state = use_tk_state("string", app_config.get("whisper_model", "base"))
    burn_sub_state = use_tk_state("bool", app_config.get("burn_sub", False))
    subtitle_offset_state = use_tk_state("double", app_config.get("subtitle_offset_sec", 0.0))
    subtitle_scale_state = use_tk_state("double", app_config.get("subtitle_timing_scale", 1.0))
    video_speed_state = use_tk_state("double", app_config.get("video_speed", 1.0))
    font_scale_state = use_tk_state("double", app_config.get("subtitle_font_scale", 1.0))
    font_size_state = use_tk_state("int", app_config.get("subtitle_font_size", 0))
    margin_state = use_tk_state("int", app_config.get("subtitle_margin_px", 0))
    chars_per_line_state = use_tk_state("int", app_config.get("srt_max_chars_per_line", 45))
    preset_state = use_tk_state("string", app_config.get("subtitle_preset", "Tùy Chỉnh"))
    preview_text_state = use_tk_state("string", app_config.get("preview_text", "Dòng phụ đề mẫu số 1\nDòng phụ đề mẫu số 2"))
    preview_time_state = use_tk_state("double", 0.0)
    blur_padding_state = use_tk_state("int", app_config.get("blur_padding_px", 12))
    cover_offset_state = use_tk_state("int", app_config.get("cover_offset_px", 0))
    blur_power_state = use_tk_state("int", app_config.get("blur_power", 4))
    enable_dub_state = use_tk_state("bool", app_config.get("enable_dub", False))
    dub_mode_state = use_tk_state("string", app_config.get("dub_mode", "preset"))
    dub_backend_mode_state = use_tk_state("string", app_config.get("dub_backend_mode", "turbo"))
    dub_remote_api_base_state = use_tk_state("string", app_config.get("dub_remote_api_base", "http://localhost:23333/v1"))
    dub_preset_voice_state = use_tk_state("string", app_config.get("dub_preset_voice", ""))
    dub_ref_audio_state = use_tk_state("string", app_config.get("dub_ref_audio", ""))
    dub_ref_text_state = use_tk_state("string", app_config.get("dub_ref_text", "Day la mau giong de clone."))
    dub_voice_volume_state = use_tk_state("double", app_config.get("dub_voice_volume", 1.35))
    dub_source_volume_state = use_tk_state("double", app_config.get("dub_source_volume", 0.18))
    dub_mix_mode_state = use_tk_state("string", app_config.get("dub_mix_mode", "nen_nho"))
    tts_preview_text_state = use_tk_state("string", app_config.get("tts_preview_text", "Xin chao, day la mau thu giong tieng Viet de kiem tra long tieng."))

    # Main container
    main_frame = tk.Frame(root, padx=16, pady=16, bg=T.BG_LIGHT)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # ── Title bar ──────────────────────────────────────────────────────────
    title_frame = tk.Frame(main_frame, bg=T.BG_LIGHT)
    title_frame.pack(pady=(0, 16))
    title = Label(title_frame, text="Dubbing Extractor", font=T.FONT_HERO,
                  bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY)
    title.pack()
    subtitle = Label(title_frame, text="Tu dong dich, long tieng va them phu de cho video",
                     font=T.FONT_SMALL, bg=T.BG_LIGHT, fg=T.TEXT_SECONDARY)
    subtitle.pack()

    # ── Action bar ─────────────────────────────────────────────────────────
    action_frame = tk.Frame(main_frame, bg=T.BG_LIGHT)
    action_frame.pack(fill=tk.X, pady=(0, 16))

    start_btn = Button(action_frame, text="▶  Bat Dau Xu Ly",
                       command=None,  # Will be set after controller creation
                       bg=T.ACCENT, fg=T.BG_WHITE,
                       width=22, height=2, font=T.FONT_BODY_SEMIBOLD)
    start_btn.pack(side=tk.LEFT, padx=(0, 8))

    clear_btn = Button(action_frame, text="Xoa Nhat Ky",
                       command=lambda: log_area.clear(),
                       bg=T.SURFACE_DARK_2, fg=T.BG_WHITE,
                       width=16, height=2, font=T.FONT_BODY)
    clear_btn.pack(side=tk.LEFT)

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: UI Layout - Notebook & Tabs
    # ═══════════════════════════════════════════════════════════
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True)

    source_tab = tk.Frame(notebook, padx=16, pady=16, bg=T.BG_WHITE)
    adjust_tab = tk.Frame(notebook, padx=16, pady=16, bg=T.BG_WHITE)
    dub_tab = tk.Frame(notebook, padx=16, pady=16, bg=T.BG_WHITE)
    log_tab = tk.Frame(notebook, padx=16, pady=16, bg=T.BG_WHITE)

    notebook.add(source_tab, text="  Nguon  ")
    notebook.add(adjust_tab, text="  Can Chinh  ")
    notebook.add(dub_tab, text="  Long Tieng  ")
    notebook.add(log_tab, text="  Nhat Ky  ")

    adjust_canvas = tk.Canvas(adjust_tab, highlightthickness=0, bg=T.BG_WHITE)
    adjust_scrollbar = ttk.Scrollbar(adjust_tab, orient=tk.VERTICAL, command=adjust_canvas.yview)
    adjust_canvas.configure(yscrollcommand=adjust_scrollbar.set)
    adjust_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    adjust_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    adjust_body = tk.Frame(adjust_canvas, bg=T.BG_WHITE)
    adjust_window = adjust_canvas.create_window((0, 0), window=adjust_body, anchor="nw")

    def _sync_adjust_scroll(_event=None):
        adjust_canvas.configure(scrollregion=adjust_canvas.bbox("all"))

    def _resize_adjust_window(event):
        adjust_canvas.itemconfigure(adjust_window, width=event.width)

    def _wheel_adjust(event):
        if preview_guard.get("over_preview"):
            return "break"
        delta = event.delta
        if delta == 0 and getattr(event, "num", None) == 4:
            delta = 120
        elif delta == 0 and getattr(event, "num", None) == 5:
            delta = -120
        if delta:
            adjust_canvas.yview_scroll(int(-delta / 120), "units")
            return "break"
        return None

    adjust_body.bind("<Configure>", _sync_adjust_scroll)
    adjust_canvas.bind("<Configure>", _resize_adjust_window)

    adjust_split = tk.Frame(adjust_body, bg=T.BG_WHITE)
    adjust_split.pack(fill=tk.BOTH, expand=True)
    adjust_split.grid_columnconfigure(0, weight=0, minsize=420)
    adjust_split.grid_columnconfigure(1, weight=1)
    adjust_split.grid_rowconfigure(0, weight=1)

    adjust_left = tk.Frame(adjust_split, bg=T.BG_WHITE)
    adjust_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    adjust_right = tk.Frame(adjust_split, bg=T.BG_WHITE)
    adjust_right.grid(row=0, column=1, sticky="nsew")
    adjust_right.grid_rowconfigure(0, weight=1)
    adjust_right.grid_columnconfigure(0, weight=1)

    def _bind_scroll_recursive(widget):
        widget.bind("<MouseWheel>", _wheel_adjust, add="+")
        widget.bind("<Button-4>", _wheel_adjust, add="+")
        widget.bind("<Button-5>", _wheel_adjust, add="+")
        for child in widget.winfo_children():
            _bind_scroll_recursive(child)

    # ═══════════════════════════════════════════════════════════
    # SECTION 4: Source Tab - Video Input & Processing
    # ═══════════════════════════════════════════════════════════
    # Video source section
    source_card = Card(source_tab, title="📹 Nguồn Video")
    source_container = source_card.get_container()

    source_input = Input(source_container, placeholder="Dán link video (YouTube, Bilibili, Douyin) hoặc chọn file local...", width=70)
    source_input.var = source_state.var
    source_input.pack(fill=tk.X, pady=5)
    source_input.widget.bind("<Return>", lambda _e: load_source_preview(force=True))
    source_input.widget.bind("<FocusOut>", lambda _e: load_source_preview(force=True))

    btn_row = Row(source_container, spacing=8, bg=T.BG_LIGHT)
    Button(btn_row.frame, text="Dan Link", command=lambda: paste_clipboard(),
           bg=T.ACCENT, fg=T.BG_WHITE, width=14, height=1,
           font=T.FONT_BODY).widget.pack(side=tk.LEFT, padx=(0, 8))
    Button(btn_row.frame, text="Chon File", command=lambda: browse_file(),
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
    pipeline_state = {
        "out_dir": None,
        "temp_dir": None,
        "raw_video": None,
        "raw_audio": None,
        "title": None,
        "segs": None,
        "segs_vi": None,
        "cover_meta": None,
        "final_video": None,
        "srt_path": None,
        "current_step": 0,  # bước đã hoàn thành gần nhất
    }

    # Màu nút theo trạng thái
    STEP_COLOR_IDLE    = "#95a5a6"
    STEP_COLOR_RUNNING = "#3498db"
    STEP_COLOR_DONE    = "#27ae60"
    STEP_COLOR_ERROR   = "#e74c3c"

    # ── Card "Chạy Từng Bước" trong tab Nguồn ───────────────────────────
    steps_card = Card(source_tab, title="🔢 Chạy Từng Bước")
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

    # ── Hàm hỗ trợ pipeline ─────────────────────────────────────────────

    def _set_pipeline_status(msg: str, color: str = "#7f8c8d"):
        pipeline_status_var.set(msg)
        pipeline_status_label.config(fg=color)

    def _update_step_buttons(running_step: int = -1):
        """Cập nhật màu sắc các nút bước theo pipeline_state."""
        done = pipeline_state["current_step"]
        for i, btn in enumerate(step_btn_widgets):
            step_num = i + 1
            if step_num == running_step:
                btn.config(bg=STEP_COLOR_RUNNING, state=tk.DISABLED)
            elif step_num <= done:
                btn.config(bg=STEP_COLOR_DONE, state=tk.NORMAL)
            else:
                btn.config(bg=STEP_COLOR_IDLE, state=tk.NORMAL)

    def _mark_step_error(step_num: int):
        if 1 <= step_num <= len(step_btn_widgets):
            step_btn_widgets[step_num - 1].config(bg=STEP_COLOR_ERROR, state=tk.NORMAL)

    def _enable_srt_editor(srt_path: str):
        """Hiện và enable ô edit SRT với nội dung file."""
        srt_editor.config(state=tk.NORMAL, bg="white")
        srt_editor.delete("1.0", tk.END)
        try:
            content = Path(srt_path).read_text(encoding="utf-8")
            srt_editor.insert("1.0", content)
        except Exception as exc:
            srt_editor.insert("1.0", f"[Không đọc được file: {exc}]")
        open_srt_btn.config(state=tk.NORMAL)
        reload_srt_btn.config(state=tk.NORMAL)
        save_srt_btn.config(state=tk.NORMAL)
        srt_file_label_var.set(Path(srt_path).name)

    def _disable_srt_editor():
        srt_editor.config(state=tk.DISABLED, bg="#f8f9fa")
        open_srt_btn.config(state=tk.DISABLED)
        reload_srt_btn.config(state=tk.DISABLED)
        save_srt_btn.config(state=tk.DISABLED)
        srt_file_label_var.set("(Chưa có file SRT)")

    def open_srt_external():
        srt_path = pipeline_state.get("srt_path")
        if srt_path and Path(srt_path).exists():
            os.startfile(srt_path)
        else:
            _set_pipeline_status("⚠ Chưa có file SRT để mở.", "#e67e22")

    def reload_srt_from_file():
        srt_path = pipeline_state.get("srt_path")
        if srt_path and Path(srt_path).exists():
            _enable_srt_editor(srt_path)
            _set_pipeline_status("✓ Đã tải lại nội dung SRT từ file.", "#27ae60")
        else:
            _set_pipeline_status("⚠ Chưa có file SRT để tải lại.", "#e67e22")

    def save_srt_to_file():
        srt_path = pipeline_state.get("srt_path")
        if not srt_path:
            _set_pipeline_status("⚠ Chưa có file SRT để lưu.", "#e67e22")
            return
        content = srt_editor.get("1.0", tk.END)
        try:
            Path(srt_path).write_text(content, encoding="utf-8")
            _set_pipeline_status(f"✓ Đã lưu thay đổi vào {Path(srt_path).name}", "#27ae60")
        except Exception as exc:
            _set_pipeline_status(f"❌ Lưu file SRT thất bại: {exc}", "#e74c3c")

    def reset_pipeline():
        pipeline_state.update({
            "out_dir": None, "temp_dir": None,
            "raw_video": None, "raw_audio": None,
            "title": None, "segs": None, "segs_vi": None,
            "cover_meta": None, "final_video": None,
            "srt_path": None, "current_step": 0,
        })
        _update_step_buttons()
        _disable_srt_editor()
        _set_pipeline_status("● Đã reset. Sẵn sàng chạy lại.", "#7f8c8d")
        log("[INFO] Pipeline đã được reset.")

    def _collect_params() -> dict:
        """Thu thập toàn bộ params từ UI state."""
        return dict(
            source_input=source_state.get().strip(),
            cover_mode=cover_mode_state.get(),
            whisper_model=whisper_model_state.get(),
            burn_sub=burn_sub_state.get(),
            subtitle_offset_sec=float(subtitle_offset_state.get()),
            subtitle_timing_scale=float(subtitle_scale_state.get()),
            video_speed=float(video_speed_state.get()),
            srt_max_chars_per_line=int(chars_per_line_state.get()),
            subtitle_font_scale=float(font_scale_state.get()),
            subtitle_font_size=int(font_size_state.get()),
            subtitle_margin_px=int(margin_state.get()),
            blur_padding_px=int(blur_padding_state.get()),
            cover_offset_px=int(cover_offset_state.get()),
            blur_power=int(blur_power_state.get()),
            enable_dub=bool(enable_dub_state.get()),
            dub_mode=dub_mode_state.get(),
            dub_backend_mode=dub_backend_mode_state.get(),
            dub_remote_api_base=dub_remote_api_base_state.get().strip(),
            dub_preset_voice=dub_preset_voice_state.get(),
            dub_ref_audio=dub_ref_audio_state.get(),
            dub_ref_text=ref_text_box.get("1.0", tk.END).strip(),
            dub_voice_volume=float(dub_voice_volume_state.get()),
            dub_source_volume=float(dub_source_volume_state.get()),
            dub_mix_mode=dub_mix_mode_state.get(),
        )

    def run_up_to_step(target_step: int):
        """Chạy pipeline từ bước hiện tại đến target_step."""
        p = _collect_params()
        source = p["source_input"]
        if not source:
            log("[ERROR] Vui lòng nhập link video hoặc đường dẫn file")
            return

        # Validate dub nếu target_step == 5
        if target_step == 5 and p["enable_dub"]:
            backend_mode = p["dub_backend_mode"]
            remote_api_base = p["dub_remote_api_base"]
            if not is_vieneu_available(engine_mode=backend_mode, remote_api_base=remote_api_base):
                log(f"[ERROR] VieNeu-TTS chưa sẵn sàng: {get_vieneu_error(engine_mode=backend_mode, remote_api_base=remote_api_base)}")
                notebook.select(dub_tab)
                return

        # Disable tất cả nút bước khi đang chạy
        for btn in step_btn_widgets:
            btn.config(state=tk.DISABLED)
        start_btn.config(state=tk.DISABLED)

        try:
            # ── Bước 1: Tải video ────────────────────────────────────────
            if pipeline_state["current_step"] < 1:
                _update_step_buttons(running_step=1)
                _set_pipeline_status("⏳ Bước 1: Đang tải video...", "#3498db")
                root.update()
                try:
                    result1 = step1_prepare(source, log_cb=log)
                    pipeline_state.update(result1)
                    pipeline_state["current_step"] = 1
                    _set_pipeline_status(f"✓ Bước 1 xong: {Path(result1['raw_video']).name}", "#27ae60")
                except Exception as exc:
                    log(f"[ERROR] Bước 1 thất bại: {exc}")
                    _mark_step_error(1)
                    _set_pipeline_status(f"❌ Bước 1 thất bại: {exc}", "#e74c3c")
                    return

            if target_step <= 1:
                return

            # ── Bước 2: Transcribe ───────────────────────────────────────
            if pipeline_state["current_step"] < 2:
                _update_step_buttons(running_step=2)
                _set_pipeline_status("⏳ Bước 2: Đang nhận dạng giọng nói...", "#3498db")
                root.update()
                config["whisper_model"] = p["whisper_model"]
                try:
                    segs = step2_transcribe(pipeline_state["raw_audio"], log_cb=log)
                    pipeline_state["segs"] = segs
                    pipeline_state["current_step"] = 2
                    _set_pipeline_status(f"✓ Bước 2 xong: {len(segs)} đoạn nhận dạng.", "#27ae60")
                except Exception as exc:
                    log(f"[ERROR] Bước 2 thất bại: {exc}")
                    _mark_step_error(2)
                    _set_pipeline_status(f"❌ Bước 2 thất bại: {exc}", "#e74c3c")
                    return

            if target_step <= 2:
                return

            # ── Bước 3: Dịch ─────────────────────────────────────────────
            if pipeline_state["current_step"] < 3:
                _update_step_buttons(running_step=3)
                _set_pipeline_status("⏳ Bước 3: Đang dịch sang tiếng Việt...", "#3498db")
                root.update()
                try:
                    segs_vi = step3_translate(
                        pipeline_state["segs"],
                        subtitle_timing_scale=p["subtitle_timing_scale"],
                        subtitle_offset_sec=p["subtitle_offset_sec"],
                        video_speed=p["video_speed"],
                        log_cb=log,
                    )
                    pipeline_state["segs_vi"] = segs_vi
                    pipeline_state["current_step"] = 3
                    _set_pipeline_status(f"✓ Bước 3 xong: {len(segs_vi)} đoạn đã dịch. Hãy kiểm tra và sửa bản dịch bên dưới.", "#27ae60")
                    # Ghi SRT tạm để user xem/sửa
                    temp_srt = Path(pipeline_state["out_dir"]) / "file_sub_viet.srt"
                    from src.modules.transcription.srt_generator import write_srt
                    write_srt(segs_vi, temp_srt, max_chars_per_line=p["srt_max_chars_per_line"])
                    pipeline_state["srt_path"] = str(temp_srt)
                    _enable_srt_editor(str(temp_srt))
                    notebook.select(source_tab)
                except Exception as exc:
                    log(f"[ERROR] Bước 3 thất bại: {exc}")
                    _mark_step_error(3)
                    _set_pipeline_status(f"❌ Bước 3 thất bại: {exc}", "#e74c3c")
                    return

            if target_step <= 3:
                return

            # ── Bước 4: Render video (che sub gốc) ───────────────────────
            if pipeline_state["current_step"] < 4:
                # Lưu nội dung editor vào file trước khi render
                if pipeline_state.get("srt_path"):
                    save_srt_to_file()

                _update_step_buttons(running_step=4)
                _set_pipeline_status("⏳ Bước 4: Đang render video...", "#3498db")
                root.update()
                config["blur_padding_px"] = p["blur_padding_px"]
                config["cover_offset_px"] = p["cover_offset_px"]
                config["blur_power"] = p["blur_power"]
                config["video_speed"] = p["video_speed"]
                try:
                    result4 = step4_cover(
                        pipeline_state["raw_video"],
                        pipeline_state["segs_vi"],
                        pipeline_state["out_dir"],
                        cover_mode=p["cover_mode"],
                        blur_padding_px=p["blur_padding_px"],
                        cover_offset_px=p["cover_offset_px"],
                        blur_power=p["blur_power"],
                        video_speed=p["video_speed"],
                        log_cb=log,
                    )
                    pipeline_state["final_video"] = result4["final_video"]
                    pipeline_state["cover_meta"] = result4["cover_meta"]

                    # Re-parse SRT đã sửa để segs_vi đồng bộ
                    if pipeline_state.get("srt_path") and Path(pipeline_state["srt_path"]).exists():
                        from src.modules.transcription.srt_generator import parse_srt
                        parsed = parse_srt(Path(pipeline_state["srt_path"]))
                        if parsed:
                            pipeline_state["segs_vi"] = parsed

                    srt_path = step5_export(
                        pipeline_state["segs_vi"],
                        pipeline_state["out_dir"],
                        pipeline_state["title"],
                        pipeline_state["cover_meta"],
                        pipeline_state["raw_video"],
                        srt_max_chars_per_line=p["srt_max_chars_per_line"],
                        subtitle_font_scale=p["subtitle_font_scale"],
                        subtitle_font_size=p["subtitle_font_size"],
                        subtitle_margin_px=p["subtitle_margin_px"],
                        blur_padding_px=p["blur_padding_px"],
                        blur_power=p["blur_power"],
                        cover_offset_px=p["cover_offset_px"],
                        subtitle_offset_sec=p["subtitle_offset_sec"],
                        subtitle_timing_scale=p["subtitle_timing_scale"],
                        video_speed=p["video_speed"],
                        cover_mode=p["cover_mode"],
                        log_cb=log,
                    )
                    pipeline_state["srt_path"] = srt_path
                    pipeline_state["current_step"] = 4

                    out_dir_result = pipeline_state["out_dir"]
                    save_app_config({"last_render_dir": out_dir_result})
                    last_output_var.set(out_dir_result)
                    load_preview_segments(out_dir_result)
                    _set_pipeline_status("✓ Bước 4 xong: Video đã render, SRT đã xuất.", "#27ae60")
                except Exception as exc:
                    log(f"[ERROR] Bước 4 thất bại: {exc}")
                    _mark_step_error(4)
                    _set_pipeline_status(f"❌ Bước 4 thất bại: {exc}", "#e74c3c")
                    return

            if target_step <= 4:
                return

            # ── Bước 5: Burn sub + Lồng tiếng ────────────────────────────
            _update_step_buttons(running_step=5)
            _set_pipeline_status("⏳ Bước 5: Đang xử lý sub/lồng tiếng...", "#3498db")
            root.update()
            try:
                dub_video_source = pipeline_state["final_video"]

                if p["burn_sub"] and pipeline_state.get("srt_path") and Path(pipeline_state["srt_path"]).exists():
                    burned = step6_burn(
                        pipeline_state["final_video"],
                        pipeline_state["srt_path"],
                        pipeline_state["cover_meta"],
                        pipeline_state["out_dir"],
                        subtitle_font_scale=p["subtitle_font_scale"],
                        subtitle_font_size=p["subtitle_font_size"],
                        subtitle_margin_px=p["subtitle_margin_px"],
                        log_cb=log,
                    )
                    if Path(burned).exists():
                        dub_video_source = burned

                if p["enable_dub"] and pipeline_state.get("segs_vi"):
                    dub_segments = list(pipeline_state["segs_vi"])
                    if pipeline_state.get("srt_path") and Path(pipeline_state["srt_path"]).exists():
                        from src.modules.transcription.srt_generator import parse_srt
                        parsed = parse_srt(Path(pipeline_state["srt_path"]))
                        if parsed:
                            dub_segments = parsed

                    step7_dub(
                        dub_video_source,
                        dub_segments,
                        pipeline_state["out_dir"],
                        dub_mode=p["dub_mode"],
                        dub_backend_mode=p["dub_backend_mode"],
                        dub_remote_api_base=p["dub_remote_api_base"],
                        dub_preset_voice=p["dub_preset_voice"],
                        dub_ref_audio=p["dub_ref_audio"],
                        dub_ref_text=p["dub_ref_text"],
                        dub_voice_volume=p["dub_voice_volume"],
                        dub_source_volume=p["dub_source_volume"],
                        dub_mix_mode=p["dub_mix_mode"],
                        output_video_name="video_sub_viet_long_tieng.mp4" if p["burn_sub"] else "video_long_tieng.mp4",
                        log_cb=log,
                    )

                pipeline_state["current_step"] = 5
                _set_pipeline_status("✅ Hoàn tất! Tất cả các bước đã xong.", "#27ae60")
                log(f"[SUCCESS] Output: {pipeline_state['out_dir']}")
                notebook.select(adjust_tab)

            except Exception as exc:
                log(f"[ERROR] Bước 5 thất bại: {exc}")
                _mark_step_error(5)
                _set_pipeline_status(f"❌ Bước 5 thất bại: {exc}", "#e74c3c")

        finally:
            _update_step_buttons()
            start_btn.config(state=tk.NORMAL)

    # Gán command cho từng nút bước (will be updated after controller creation)
    for i, btn in enumerate(step_btn_widgets):
        step_num = i + 1
        btn.config(command=lambda n=step_num: run_up_to_step(n))

    # Gán command các nút SRT
    open_srt_btn.config(command=open_srt_external)
    reload_srt_btn.config(command=reload_srt_from_file)
    save_srt_btn.config(command=save_srt_to_file)
    reset_pipeline_btn.config(command=reset_pipeline)

    # ═══════════════════════════════════════════════════════════
    # SECTION 5: Adjust Tab - Subtitle Parameters
    # ═══════════════════════════════════════════════════════════
    # Settings section
    settings_card = Card(adjust_left, title="Cai Dat Phu De Va Vung Che")
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
            variable=cover_mode_state.var,
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
        tk.Radiobutton(model_frame, text=model, variable=whisper_model_state.var, value=model,
                       font=T.FONT_BODY, bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                       activebackground=T.BG_LIGHT, selectcolor=T.BG_WHITE,
                       relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # Burn subtitle
    burn_check = Checkbox(settings_container, text="Ghi phu de vao video", default=burn_sub_state.get())
    burn_check.var = burn_sub_state.var
    burn_check.pack(anchor=tk.W, pady=5)

    preset_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    preset_row.pack(fill=tk.X, pady=(12, 6))
    _lbl(preset_row, "Mau Phu De:").pack(side=tk.LEFT)
    preset_combo = ttk.Combobox(
        preset_row, textvariable=preset_state.var,
        values=list(SUBTITLE_PRESETS.keys()), state="readonly", width=16,
    )
    preset_combo.pack(side=tk.LEFT)
    _hint(preset_row, "Chon preset hoac de Tuy Chinh de chinh tay").pack(side=tk.LEFT, padx=8)

    timing_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    timing_row.pack(fill=tk.X, pady=(12, 6))
    _lbl(timing_row, "Lech Thoi Gian (s):").pack(side=tk.LEFT)
    tk.Spinbox(timing_row, from_=-30.0, to=30.0, increment=0.1, textvariable=subtitle_offset_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(timing_row, "Am = hien som hon, duong = hien tre hon").pack(side=tk.LEFT, padx=8)

    speed_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    speed_row.pack(fill=tk.X, pady=6)
    _lbl(speed_row, "Ti Le Timing Sub:").pack(side=tk.LEFT)
    tk.Spinbox(speed_row, from_=0.5, to=2.0, increment=0.05, textvariable=subtitle_scale_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(speed_row, "1.0 = thoi gian goc").pack(side=tk.LEFT, padx=8)

    video_speed_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    video_speed_row.pack(fill=tk.X, pady=6)
    _lbl(video_speed_row, "Toc Do Video:").pack(side=tk.LEFT)
    tk.Spinbox(video_speed_row, from_=0.25, to=4.0, increment=0.05, textvariable=video_speed_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(video_speed_row, "1.0 = goc | >1 nhanh hon | <1 cham hon").pack(side=tk.LEFT, padx=8)

    font_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    font_row.pack(fill=tk.X, pady=6)
    _lbl(font_row, "Ti Le Co Chu:").pack(side=tk.LEFT)
    tk.Spinbox(font_row, from_=0.5, to=2.5, increment=0.1, textvariable=font_scale_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(font_row, "Dung khi ghi phu de vao video").pack(side=tk.LEFT, padx=8)

    font_size_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    font_size_row.pack(fill=tk.X, pady=6)
    _lbl(font_size_row, "Co Chu:").pack(side=tk.LEFT)
    tk.Spinbox(font_size_row, from_=0, to=96, increment=1, textvariable=font_size_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(font_size_row, "0 = tu dong theo ti le co chu").pack(side=tk.LEFT, padx=8)

    margin_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    margin_row.pack(fill=tk.X, pady=6)
    _lbl(margin_row, "Lech Vi Tri Doc:").pack(side=tk.LEFT)
    tk.Spinbox(margin_row, from_=-240, to=240, increment=4, textvariable=margin_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(margin_row, "So pixel lech so voi vi tri mac dinh").pack(side=tk.LEFT, padx=8)

    chars_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    chars_row.pack(fill=tk.X, pady=6)
    _lbl(chars_row, "Ky Tu Moi Dong:").pack(side=tk.LEFT)
    tk.Spinbox(chars_row, from_=20, to=80, increment=1, textvariable=chars_per_line_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(chars_row, "Dung khi xuat file SRT").pack(side=tk.LEFT, padx=8)

    blur_pad_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    blur_pad_row.pack(fill=tk.X, pady=6)
    _lbl(blur_pad_row, "Noi Vung Che (px):").pack(side=tk.LEFT)
    tk.Spinbox(blur_pad_row, from_=0, to=200, increment=2, textvariable=blur_padding_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(blur_pad_row, "Noi doi xung tu tam vung subtitle cu").pack(side=tk.LEFT, padx=8)

    blur_power_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    blur_power_row.pack(fill=tk.X, pady=6)
    _lbl(blur_power_row, "Do Mo:").pack(side=tk.LEFT)
    tk.Spinbox(blur_power_row, from_=1, to=10, increment=1, textvariable=blur_power_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(blur_power_row, "Chi ap dung khi chon che do Lam mo").pack(side=tk.LEFT, padx=8)

    cover_offset_row = tk.Frame(settings_container, bg=T.BG_LIGHT)
    cover_offset_row.pack(fill=tk.X, pady=6)
    _lbl(cover_offset_row, "Day Vung Che Len:").pack(side=tk.LEFT)
    tk.Spinbox(cover_offset_row, from_=-240, to=240, increment=2, textvariable=cover_offset_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(cover_offset_row, "Duong = keo vung che len, am = day xuong").pack(side=tk.LEFT, padx=8)

    settings_card.pack(fill=tk.X, pady=5)

    # ═══════════════════════════════════════════════════════════
    # SECTION 6: Dub Tab - TTS Configuration
    # ═══════════════════════════════════════════════════════════
    # Dubbing tab
    dub_card = Card(dub_tab, title="Long Tieng Tieng Viet")
    dub_container = dub_card.get_container()

    tts_status_var = tk.StringVar(value="VieNeu-TTS chua duoc kiem tra.")
    tts_status_label = tk.Label(dub_container, textvariable=tts_status_var,
                                anchor="w", justify=tk.LEFT,
                                fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT,
                                font=T.FONT_SMALL)
    tts_status_label.pack(fill=tk.X, pady=(0, 8))

    enable_dub_check = Checkbox(dub_container, text="Bat long tieng tieng Viet", default=enable_dub_state.get())
    enable_dub_check.var = enable_dub_state.var
    enable_dub_check.pack(anchor=tk.W, pady=(0, 8))

    dub_mode_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    dub_mode_row.pack(fill=tk.X, pady=4)
    _lbl(dub_mode_row, "Che Do Giong:").pack(side=tk.LEFT)
    tk.Radiobutton(dub_mode_row, text="Giong mau", variable=dub_mode_state.var, value="preset",
                   font=T.FONT_BODY, bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                   activebackground=T.BG_LIGHT, selectcolor=T.BG_WHITE,
                   relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=4)
    tk.Radiobutton(dub_mode_row, text="Clone tu file", variable=dub_mode_state.var, value="clone",
                   font=T.FONT_BODY, bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                   activebackground=T.BG_LIGHT, selectcolor=T.BG_WHITE,
                   relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=4)

    dub_backend_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    dub_backend_row.pack(fill=tk.X, pady=4)
    _lbl(dub_backend_row, "Backend VieNeu:").pack(side=tk.LEFT)
    dub_backend_combo = ttk.Combobox(
        dub_backend_row, textvariable=dub_backend_mode_state.var,
        values=["turbo", "turbo_gpu", "standard", "fast", "remote", "xpu"],
        width=18, state="readonly",
    )
    dub_backend_combo.pack(side=tk.LEFT)
    _hint(dub_backend_row, "turbo=CPU nhanh | turbo_gpu/fast=GPU | remote=server").pack(side=tk.LEFT, padx=8)

    dub_remote_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    dub_remote_row.pack(fill=tk.X, pady=4)
    _lbl(dub_remote_row, "Remote API:").pack(side=tk.LEFT)
    dub_remote_entry = tk.Entry(dub_remote_row, textvariable=dub_remote_api_base_state.var, width=48,
                                font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
                                relief=tk.FLAT, borderwidth=1,
                                insertbackground=T.ACCENT)
    dub_remote_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    preset_voice_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    preset_voice_row.pack(fill=tk.X, pady=4)
    _lbl(preset_voice_row, "Giong Mau:").pack(side=tk.LEFT)
    preset_voice_combo = ttk.Combobox(
        preset_voice_row, textvariable=dub_preset_voice_state.var,
        values=[], width=28, state="readonly",
    )
    preset_voice_combo.pack(side=tk.LEFT)
    dub_refresh_voice_btn = tk.Button(preset_voice_row, text="Tai Danh Sach Giong",
                                      bg=T.BG_LIGHT, fg=T.ACCENT,
                                      font=T.FONT_BODY, relief=tk.FLAT,
                                      cursor="hand2", width=18)
    dub_refresh_voice_btn.pack(side=tk.LEFT, padx=(8, 0))

    ref_audio_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    ref_audio_row.pack(fill=tk.X, pady=4)
    _lbl(ref_audio_row, "File Giong Mau:").pack(side=tk.LEFT)
    ref_audio_entry = tk.Entry(ref_audio_row, textvariable=dub_ref_audio_state.var, width=56,
                               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
                               relief=tk.FLAT, borderwidth=1,
                               insertbackground=T.ACCENT)
    ref_audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    dub_browse_ref_btn = tk.Button(ref_audio_row, text="Chon File",
                                   bg=T.SURFACE_DARK_2, fg=T.BG_WHITE,
                                   font=T.FONT_BODY, relief=tk.FLAT,
                                   cursor="hand2", width=12)
    dub_browse_ref_btn.pack(side=tk.LEFT, padx=(8, 0))

    ref_text_label = tk.Label(dub_container, text="Noi Dung File Mau:", anchor="w",
                              font=T.FONT_BODY, fg=T.TEXT_PRIMARY, bg=T.BG_LIGHT)
    ref_text_label.pack(fill=tk.X, pady=(8, 0))
    ref_text_box = tk.Text(dub_container, height=3, font=T.FONT_BODY,
                           bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
                           relief=tk.FLAT, borderwidth=1,
                           insertbackground=T.ACCENT, padx=6, pady=4)
    ref_text_box.pack(fill=tk.X, pady=(0, 8))
    ref_text_box.insert("1.0", dub_ref_text_state.get())

    dub_mix_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    dub_mix_row.pack(fill=tk.X, pady=4)
    _lbl(dub_mix_row, "Am Luong Giong:").pack(side=tk.LEFT)
    tk.Spinbox(dub_mix_row, from_=0.5, to=3.0, increment=0.05, textvariable=dub_voice_volume_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(dub_mix_row, "1.0 = giu nguyen | tang neu giong doc con nho").pack(side=tk.LEFT, padx=8)

    dub_source_mix_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    dub_source_mix_row.pack(fill=tk.X, pady=4)
    _lbl(dub_source_mix_row, "Am Luong Goc:").pack(side=tk.LEFT)
    tk.Spinbox(dub_source_mix_row, from_=0.0, to=1.0, increment=0.05, textvariable=dub_source_volume_state.var, width=8,
               font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
    _hint(dub_source_mix_row, "0 = tat tieng goc, 0.18 = nen nho phia sau").pack(side=tk.LEFT, padx=8)

    dub_mix_mode_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
    dub_mix_mode_row.pack(fill=tk.X, pady=4)
    _lbl(dub_mix_mode_row, "Cach Mix Audio:").pack(side=tk.LEFT)
    dub_mix_mode_combo = ttk.Combobox(
        dub_mix_mode_row, textvariable=dub_mix_mode_state.var,
        values=["nen_nho", "tat_goc"], width=18, state="readonly",
    )
    dub_mix_mode_combo.pack(side=tk.LEFT)
    _hint(dub_mix_mode_row, "nen_nho = giu nhac nen nho | tat_goc = tat audio goc").pack(side=tk.LEFT, padx=8)

    preview_tts_label = tk.Label(dub_container, text="Text Nghe Thu:", anchor="w",
                                 font=T.FONT_BODY, fg=T.TEXT_PRIMARY, bg=T.BG_LIGHT)
    preview_tts_label.pack(fill=tk.X, pady=(10, 0))
    tts_preview_box = tk.Text(dub_container, height=4, font=T.FONT_BODY,
                              bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
                              relief=tk.FLAT, borderwidth=1,
                              insertbackground=T.ACCENT, padx=6, pady=4)
    tts_preview_box.pack(fill=tk.X, pady=(0, 8))
    tts_preview_box.insert("1.0", tts_preview_text_state.get())

    dub_preview_controls = tk.Frame(dub_container, bg=T.BG_LIGHT)
    dub_preview_controls.pack(fill=tk.X, pady=(0, 8))
    dub_preview_btn = tk.Button(dub_preview_controls, text="Nghe Thu Giong",
                                bg=T.ACCENT, fg=T.BG_WHITE,
                                font=T.FONT_BODY, relief=tk.FLAT,
                                cursor="hand2", width=16)
    dub_preview_btn.pack(side=tk.LEFT)
    dub_stop_preview_btn = tk.Button(dub_preview_controls, text="Dung Nghe Thu",
                                     bg=T.SURFACE_DARK_2, fg=T.BG_WHITE,
                                     font=T.FONT_BODY, relief=tk.FLAT,
                                     cursor="hand2", width=14)
    dub_stop_preview_btn.pack(side=tk.LEFT, padx=(8, 0))

    dub_help = tk.Label(
        dub_container,
        text=(
            "Giong mau: dung nhanh, khong can file mau.\n"
            "Clone giong: nen dung file 3-5 giay, 1 nguoi noi ro, it nhac nen, it vang.\n"
            "Mode VieNeu: turbo=CPU GGUF, turbo_gpu=GPU, standard=CPU/GPU, "
            "fast=LMDeploy, remote=server API, xpu=Intel GPU."
        ),
        anchor="w",
        justify=tk.LEFT,
        fg=T.TEXT_SECONDARY,
    )
    dub_help.pack(fill=tk.X)

    dub_card.pack(fill=tk.BOTH, expand=True, pady=5)

    # Adjust/preview tab
    preview_card = Card(adjust_right, title="Xem Truoc Va Can Chinh")
    preview_container = preview_card.get_container()

    preview_info_var = tk.StringVar(value="")
    preview_info = tk.Label(preview_container, textvariable=preview_info_var,
                            anchor="w", justify=tk.LEFT,
                            fg=T.TEXT_PRIMARY, bg=T.BG_LIGHT,
                            font=T.FONT_SMALL)
    preview_info.pack(fill=tk.X, pady=(0, 8))

    preview_status_var = tk.StringVar(value="Chua tai xem truoc.")
    tk.Label(preview_container, textvariable=preview_status_var,
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

    preview_play_btn = _ctrl_btn(preview_controls, "Phat", 10, accent=True)
    preview_play_btn.pack(side=tk.LEFT)

    preview_refresh_btn = _ctrl_btn(preview_controls, "Tai Lai Khung", 12)
    preview_refresh_btn.pack(side=tk.LEFT, padx=(8, 0))

    preview_reset_pos_btn = _ctrl_btn(preview_controls, "Dat Lai Vi Tri", 14)
    preview_reset_pos_btn.pack(side=tk.LEFT, padx=(8, 0))

    preview_reset_style_btn = _ctrl_btn(preview_controls, "Dat Lai Kieu", 12)
    preview_reset_style_btn.pack(side=tk.LEFT, padx=(8, 0))

    preview_time_label_var = tk.StringVar(value="00:00 / 00:00")
    tk.Label(preview_controls, textvariable=preview_time_label_var,
             fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT,
             font=T.FONT_SMALL).pack(side=tk.RIGHT)

    preview_seek = tk.Scale(
        preview_container,
        from_=0, to=100, orient=tk.HORIZONTAL,
        showvalue=False, resolution=0.1, length=860,
        bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
        troughcolor=T.BORDER, highlightthickness=0,
        activebackground=T.ACCENT,
    )
    preview_seek.pack(fill=tk.X, pady=(0, 10))

    preview_marker_canvas = tk.Canvas(preview_container, height=54,
                                      bg=T.BG_CARD_DARK,
                                      highlightthickness=1,
                                      highlightbackground=T.SURFACE_DARK_1)
    preview_marker_canvas.pack(fill=tk.X, pady=(0, 10))

    preview_text_box = tk.Text(preview_container, height=2, font=T.FONT_BODY,
                               bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
                               relief=tk.FLAT, borderwidth=0,
                               insertbackground=T.ACCENT,
                               padx=6, pady=4)
    preview_text_box.pack(fill=tk.X, pady=(0, 10))
    preview_text_box.insert("1.0", preview_text_state.get())

    preview_canvas = tk.Canvas(preview_container, width=900, height=360,
                               bg=T.BG_CARD_DARK, highlightthickness=0)
    preview_canvas.pack(fill=tk.BOTH, expand=True)

    preview_card.pack(fill=tk.BOTH, expand=True, pady=5)

    output_card = Card(adjust_left, title="Output Gan Nhat")
    output_container = output_card.get_container()
    last_output_var = tk.StringVar(value=app_config.get("last_render_dir", ""))
    tk.Label(output_container, textvariable=last_output_var, anchor="w",
             justify=tk.LEFT, fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT,
             font=T.FONT_SMALL).pack(fill=tk.X)
    open_output_btn = tk.Button(output_container, text="Mo Thu Muc Render",
                                bg=T.ACCENT, fg=T.BG_WHITE,
                                font=T.FONT_BODY, relief=tk.FLAT,
                                cursor="hand2", width=18)
    open_output_btn.pack(anchor=tk.W, pady=(8, 0))
    output_card.pack(fill=tk.X, pady=5)

    # ═══════════════════════════════════════════════════════════
    # SECTION 7: Log Tab - Output & Status
    # ═══════════════════════════════════════════════════════════
    # Log section
    log_card = Card(log_tab, title="Nhat Ky Xu Ly")
    log_container = log_card.get_container()

    log_area = TextArea(log_container, height=12, font=T.FONT_MONO)
    log_area.widget.config(bg=T.BG_LOG, fg=T.FG_LOG,
                           insertbackground=T.ACCENT)
    log_area.pack(fill=tk.BOTH, expand=True)

    log_card.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Helper functions
    def paste_clipboard():
        try:
            source_state.set(root.clipboard_get().strip())
            load_source_preview(force=True)
        except:
            pass
    
    def browse_file():
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=[("File video", "*.mp4 *.avi *.mkv *.mov *.flv"), ("Tất cả file", "*.*")]
        )
        if filename:
            source_state.set(filename)
            load_source_preview(force=True)

    def browse_ref_audio():
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Chọn file audio mẫu",
            filetypes=[("File audio", "*.wav *.mp3 *.m4a *.flac *.aac *.ogg"), ("Tất cả file", "*.*")]
        )
        if filename:
            dub_ref_audio_state.set(filename)

    def open_render_folder():
        render_dir = last_output_var.get().strip()
        if not render_dir:
            preview_status_var.set("Chưa có thư mục render để mở.")
            return
        render_path = Path(render_dir)
        if not render_path.exists():
            preview_status_var.set("Thư mục render hiện không tồn tại.")
            return
        try:
            subprocess.Popen(["explorer.exe", str(render_path)])
            preview_status_var.set(f"Đã mở thư mục render: {render_path.name}")
        except Exception as exc:
            preview_status_var.set(f"Mở thư mục render thất bại: {exc}")

    def log(*parts):
        msg = " | ".join(str(part) for part in parts if part is not None)
        if not msg:
            return
        _write_app_log_line(msg)
        log_area.append(msg + "\n")
        root.update()

    _write_app_log_line("=" * 72)
    _write_app_log_line("GUI session started")

    preset_guard = {"applying": False}
    preview_guard = {
        "source": None,
        "image": None,
        "live_render": False,
        "render_after_id": None,
        "render_signature": None,
        "kind": None,
        "duration": 0.0,
        "path": None,
        "playing": False,
        "after_id": None,
        "updating_seek": False,
        "drag_margin_start": 0,
        "drag_offset_start": 0.0,
        "drag_x_start": 0,
        "drag_y_start": 0,
        "drag_active": False,
        "segments": [],
        "selected_segment": None,
        "over_preview": False,
        "video_rect": (0, 0, 0, 0),
        "subtitle_rect": (0, 0, 0, 0),
        "render_meta": {},
    }

    voice_guard = {
        "options": [],
        "preview_path": HERE / "output" / "_preview_cache" / "tts_preview.wav",
    }

    def mark_preset_custom(*_args):
        if preset_guard["applying"]:
            return
        if preset_state.get() != "Tùy Chỉnh":
            preset_state.set("Tùy Chỉnh")

    def apply_selected_preset(*_args):
        preset_name = preset_state.get()
        values = SUBTITLE_PRESETS.get(preset_name)
        if not values:
            update_preview()
            return
        preset_guard["applying"] = True
        subtitle_offset_state.set(values["subtitle_offset_sec"])
        subtitle_scale_state.set(values["subtitle_timing_scale"])
        font_scale_state.set(values["subtitle_font_scale"])
        font_size_state.set(values["subtitle_font_size"])
        margin_state.set(values["subtitle_margin_px"])
        chars_per_line_state.set(values["srt_max_chars_per_line"])
        preset_guard["applying"] = False
        update_preview()

    def _format_duration(seconds: float) -> str:
        total = int(seconds or 0)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def _wrap_preview_text(text: str, max_chars: int) -> str:
        text = (text or "").strip()
        if not text:
            return "Dòng phụ đề mẫu số 1\nDòng phụ đề mẫu số 2"
        if "\n" in text:
            return text
        if len(text) <= max_chars:
            return text
        words = text.split()
        lines = []
        current = []
        current_len = 0
        for word in words:
            next_len = current_len + len(word) + (1 if current else 0)
            if next_len <= max_chars:
                current.append(word)
                current_len = next_len
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
                current_len = len(word)
        if current:
            lines.append(" ".join(current))
        return "\n".join(lines[:2])

    def _current_preview_text() -> str:
        return _wrap_preview_text(preview_text_box.get("1.0", tk.END).strip(), int(chars_per_line_state.get()))

    def on_preview_text_changed(_event=None):
        if preview_guard.get("selected_segment") is not None:
            preview_guard["selected_segment"] = None
            _render_segment_markers()
        update_preview()

    def _load_render_meta(output_dir: str) -> dict:
        if not output_dir:
            return {}
        meta_path = Path(output_dir) / "render_meta.json"
        if not meta_path.exists():
            return {}
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _update_tts_status(message: str, color: str = "#445"):
        tts_status_var.set(message)
        tts_status_label.config(fg=color)

    def refresh_voice_list():
        backend_mode = dub_backend_mode_state.get()
        remote_api_base = dub_remote_api_base_state.get().strip()
        if not is_vieneu_available(engine_mode=backend_mode, remote_api_base=remote_api_base):
            _update_tts_status(
                f"VieNeu-TTS chưa sẵn sàng: {get_vieneu_error(engine_mode=backend_mode, remote_api_base=remote_api_base)}",
                "#a33",
            )
            preset_voice_combo.configure(values=[])
            return
        try:
            voices = list_preset_voices(engine_mode=backend_mode, remote_api_base=remote_api_base)
            voice_guard["options"] = voices
            preset_voice_combo.configure(values=voices)
            if voices and not dub_preset_voice_state.get():
                dub_preset_voice_state.set(voices[0])
            _update_tts_status(f"VieNeu-TTS sẵn sàng | mode={backend_mode} | {len(voices)} giọng mẫu", "#275")
        except Exception as exc:
            _update_tts_status(f"Tải danh sách giọng thất bại: {exc}", "#a33")
        finally:
            release_tts_resources()

    def sync_dub_mode(*_args):
        preset_enabled = dub_mode_state.get() == "preset"
        clone_enabled = dub_mode_state.get() == "clone"
        remote_enabled = dub_backend_mode_state.get() == "remote"
        preset_voice_combo.configure(state="readonly" if preset_enabled else "disabled")
        dub_refresh_voice_btn.configure(state=tk.NORMAL if preset_enabled else tk.DISABLED)
        ref_audio_entry.configure(state=tk.NORMAL if clone_enabled else tk.DISABLED)
        dub_browse_ref_btn.configure(state=tk.NORMAL if clone_enabled else tk.DISABLED)
        ref_text_box.configure(state=tk.NORMAL if clone_enabled else tk.DISABLED)
        dub_remote_entry.configure(state=tk.NORMAL if remote_enabled else tk.DISABLED)

    def stop_preview_audio():
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    def play_tts_preview():
        stop_preview_audio()
        backend_mode = dub_backend_mode_state.get()
        remote_api_base = dub_remote_api_base_state.get().strip()
        if not is_vieneu_available(engine_mode=backend_mode, remote_api_base=remote_api_base):
            _update_tts_status(
                f"VieNeu-TTS chưa sẵn sàng: {get_vieneu_error(engine_mode=backend_mode, remote_api_base=remote_api_base)}",
                "#a33",
            )
            return
        text = tts_preview_box.get("1.0", tk.END).strip()
        ref_text = ref_text_box.get("1.0", tk.END).strip()
        tts_preview_text_state.set(text)
        dub_ref_text_state.set(ref_text)
        try:
            voice_guard["preview_path"].parent.mkdir(parents=True, exist_ok=True)
            synthesize_speech(
                text=text,
                out_path=voice_guard["preview_path"],
                mode=dub_mode_state.get(),
                engine_mode=backend_mode,
                remote_api_base=remote_api_base,
                preset_voice=dub_preset_voice_state.get(),
                ref_audio=dub_ref_audio_state.get(),
                ref_text=ref_text,
                log_cb=log,
            )
            winsound.PlaySound(str(voice_guard["preview_path"]), winsound.SND_FILENAME | winsound.SND_ASYNC)
            _update_tts_status(f"Đã tạo và phát mẫu nghe thử | mode={backend_mode}", "#275")
        except Exception as exc:
            _update_tts_status(f"Nghe thử thất bại: {exc}", "#a33")
        finally:
            release_tts_resources()

    def _extract_local_preview_frame(video_path: str, timestamp: float) -> Path:
        preview_dir = HERE / "output" / "_preview_cache"
        preview_dir.mkdir(parents=True, exist_ok=True)
        out_path = preview_dir / "local_preview.png"
        cmd = [
            ffmpeg_cmd(), "-y",
            "-ss", f"{max(0.0, timestamp):.2f}",
            "-i", video_path,
            "-frames:v", "1",
            "-update", "1",
            "-vf", "scale=480:-1",
            str(out_path),
        ]
        import subprocess
        subprocess.run(cmd, capture_output=True, check=True)
        return out_path

    def _write_preview_srt(text: str) -> Path:
        preview_dir = HERE / "output" / "_preview_cache"
        preview_dir.mkdir(parents=True, exist_ok=True)
        srt_path = preview_dir / "preview_overlay.srt"
        safe_text = (text or "").strip() or " "
        srt_path.write_text(
            "1\n00:00:00,000 --> 23:59:59,000\n" + safe_text + "\n",
            encoding="utf-8",
        )
        return srt_path

    def _escape_sub_path(path: Path) -> str:
        return str(path).replace("\\", "\\\\").replace(":", "\\:")

    def _render_local_preview_composite(video_path: str, timestamp: float) -> Path:
        preview_dir = HERE / "output" / "_preview_cache"
        preview_dir.mkdir(parents=True, exist_ok=True)
        out_path = preview_dir / "local_preview_rendered.png"
        render_meta = preview_guard.get("render_meta") or {}
        dims = get_dims(Path(video_path))
        src_w, src_h = dims
        meta_top_y = render_meta.get("subtitle_top_y")
        meta_bottom_y = render_meta.get("subtitle_bottom_y")
        layout = compute_subtitle_layout(
            src_h,
            meta_top_y,
            meta_bottom_y,
            font_scale=float(font_scale_state.get()),
            font_size_override=int(font_size_state.get()),
            margin_offset=int(margin_state.get()),
        )
        srt_path = _write_preview_srt(_current_preview_text())
        style = (
            f"FontName=Arial,"
            f"FontSize={layout['font_size']},"
            f"PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,"
            f"BackColour=&H60000000,"
            f"Bold=1,"
            f"Outline=2,"
            f"Shadow=1,"
            f"Alignment=2,"
            f"MarginV={layout['margin_v']}"
        )

        filter_parts = []
        current_label = "[0:v]"
        blur_padding = max(0, int(blur_padding_state.get()))
        cover_offset = int(cover_offset_state.get())
        cover_mode = cover_mode_state.get()
        if cover_mode in ("blur", "blackbar"):
            cover_top_y = render_meta.get("cover_top_y")
            cover_bottom_y = render_meta.get("cover_bottom_y")
            if cover_top_y is not None and cover_bottom_y is not None:
                top_y, bottom_y = shift_band(int(cover_top_y), int(cover_bottom_y), src_h, cover_offset)
            elif meta_top_y is not None and meta_bottom_y is not None:
                top_y, bottom_y = expand_band_from_center(meta_top_y, meta_bottom_y, src_h, blur_padding)
                top_y, bottom_y = shift_band(top_y, bottom_y, src_h, cover_offset)
            else:
                approx_bottom = src_h - layout["margin_v"]
                approx_height = max(layout["font_size"] * 2 + 24, int(src_h * 0.10))
                top_y, bottom_y = expand_band_from_center(
                    int(approx_bottom - approx_height),
                    int(approx_bottom),
                    src_h,
                    blur_padding,
                )
                top_y, bottom_y = shift_band(top_y, bottom_y, src_h, cover_offset)
            band_h = max(2, bottom_y - top_y + 1)
            if cover_mode == "blur":
                power = max(1, min(10, int(blur_power_state.get())))
                luma_r = min(25, max(1, (band_h - 1) // 2))
                chroma_r = min(25, max(1, (band_h // 2 - 1) // 2))
                filter_parts.append(f"{current_label}split=2[base][src]")
                filter_parts.append(
                    f"[src]crop=iw:{band_h}:0:{top_y},"
                    f"boxblur=luma_radius={luma_r}:luma_power={power}:"
                    f"chroma_radius={chroma_r}:chroma_power={power}[blur]"
                )
                filter_parts.append(f"[base][blur]overlay=0:{top_y}[covered]")
                current_label = "[covered]"
            else:
                filter_parts.append(
                    f"{current_label}drawbox=x=0:y={top_y}:w=iw:h={band_h}:color=black:t=fill[covered]"
                )
                current_label = "[covered]"

        filter_parts.append(
            f"{current_label}subtitles='{_escape_sub_path(srt_path)}':force_style='{style}',scale=480:-1[out]"
        )
        cmd = [
            ffmpeg_cmd(), "-y",
            "-ss", f"{max(0.0, timestamp):.2f}",
            "-i", video_path,
            "-frames:v", "1",
            "-filter_complex", ";".join(filter_parts),
            "-map", "[out]",
            str(out_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return out_path

    def _request_live_preview_render():
        if preview_guard.get("kind") != "local":
            return
        video_path = preview_guard.get("path")
        if not video_path:
            return
        signature = repr((
            video_path,
            round(float(preview_time_state.get()), 2),
            cover_mode_state.get(),
            int(blur_padding_state.get()),
            int(cover_offset_state.get()),
            int(blur_power_state.get()),
            float(font_scale_state.get()),
            int(font_size_state.get()),
            int(margin_state.get()),
            _current_preview_text(),
            tuple(preview_guard.get("render_meta", {}).items()),
        ))
        if signature == preview_guard.get("render_signature"):
            return
        preview_guard["render_signature"] = signature
        if preview_guard.get("render_after_id") is not None:
            root.after_cancel(preview_guard["render_after_id"])
        preview_guard["render_after_id"] = root.after(
            140,
            lambda: _render_live_preview_if_current(signature),
        )

    def _render_live_preview_if_current(signature: str):
        preview_guard["render_after_id"] = None
        if signature != preview_guard.get("render_signature"):
            return
        video_path = preview_guard.get("path")
        if not video_path:
            return
        try:
            rendered_path = _render_local_preview_composite(video_path, float(preview_time_state.get()))
            _set_preview_image(rendered_path, live_render=True)
        except Exception:
            pass

    def _set_preview_image(preview_path: Path, live_render: bool = False):
        photo = tk.PhotoImage(file=str(preview_path))
        preview_guard["image"] = photo
        preview_guard["live_render"] = live_render
        update_preview()

    def _update_preview_time_label():
        preview_time_label_var.set(
            f"{_format_duration(preview_time_state.get())} / {_format_duration(preview_guard['duration'])}"
        )

    def _parse_srt_segments(srt_path: Path) -> list[dict]:
        if not srt_path.exists():
            return []

        def _parse_time(value: str) -> float:
            hh, mm, rest = value.split(":")
            ss, ms = rest.split(",")
            return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000

        content = srt_path.read_text(encoding="utf-8", errors="ignore").strip()
        blocks = [block.strip() for block in content.split("\n\n") if block.strip()]
        segments = []
        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if len(lines) < 3 or "-->" not in lines[1]:
                continue
            start_text, end_text = [part.strip() for part in lines[1].split("-->")]
            segments.append({
                "start": _parse_time(start_text),
                "end": _parse_time(end_text),
                "text": "\n".join(lines[2:]),
            })
        return segments

    def _resolve_latest_srt_output(preferred_output_dir: str) -> str:
        preferred = Path(preferred_output_dir) if preferred_output_dir else None
        if preferred and (preferred / "file_sub_viet.srt").exists():
            return str(preferred)

        output_root = HERE / "output"
        if not output_root.exists():
            return ""

        candidates = [
            path for path in output_root.iterdir()
            if path.is_dir() and (path / "file_sub_viet.srt").exists()
        ]
        if not candidates:
            return ""
        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        return str(latest)

    def _render_segment_markers():
        preview_marker_canvas.delete("all")
        width = max(preview_marker_canvas.winfo_width(), 860)
        height = max(preview_marker_canvas.winfo_height(), 54)
        preview_marker_canvas.create_rectangle(0, 0, width, height, fill="#101820", outline="")

        segments = preview_guard.get("segments") or []
        duration = max(float(preview_guard.get("duration") or 0.0), 0.1)
        if not segments:
            preview_marker_canvas.create_text(
                12, height / 2,
                anchor="w",
                text="Chưa có đoạn phụ đề để xem trước. Sau khi render SRT, marker sẽ hiện ở đây.",
                fill="#7f93a8",
                font=("Arial", 10),
            )
            return

        preview_marker_canvas.create_text(
            12, 12,
            anchor="w",
            text=f"{len(segments)} đoạn phụ đề",
            fill="#7f93a8",
            font=("Arial", 10, "bold"),
        )
        for idx, seg in enumerate(segments):
            x0 = int((seg["start"] / duration) * max(width - 24, 1)) + 12
            x1 = int((seg["end"] / duration) * max(width - 24, 1)) + 12
            x1 = max(x0 + 3, x1)
            fill = "#f2b134" if idx == preview_guard.get("selected_segment") else "#53a7ff"
            preview_marker_canvas.create_rectangle(
                x0, 24, x1, height - 12,
                fill=fill,
                outline="",
                tags=(f"segment_{idx}", "segment_marker"),
            )
            preview_marker_canvas.tag_bind(f"segment_{idx}", "<Button-1>", lambda _e, i=idx: jump_to_segment(i))

    def load_preview_segments(output_dir: str):
        resolved_output_dir = _resolve_latest_srt_output(output_dir)
        output_path = Path(resolved_output_dir) if resolved_output_dir else Path("")
        srt_path = output_path / "file_sub_viet.srt"
        preview_guard["segments"] = _parse_srt_segments(srt_path)
        preview_guard["selected_segment"] = None
        preview_guard["render_meta"] = _load_render_meta(resolved_output_dir)
        if resolved_output_dir:
            last_output_var.set(resolved_output_dir)
        if preview_guard["segments"]:
            preview_text_box.delete("1.0", tk.END)
            preview_text_box.insert("1.0", preview_guard["segments"][0]["text"])
        root.after(10, _render_segment_markers)

    def _stop_preview_playback():
        preview_guard["playing"] = False
        if preview_guard["after_id"] is not None:
            root.after_cancel(preview_guard["after_id"])
            preview_guard["after_id"] = None
        preview_play_btn.config(text="Phát")

    def _render_local_preview_frame(timestamp: float):
        video_path = preview_guard.get("path")
        if not video_path:
            return
        clamped = max(0.0, min(timestamp, preview_guard["duration"]))
        preview_path = _extract_local_preview_frame(video_path, clamped)
        _set_preview_image(preview_path, live_render=False)
        preview_time_state.set(clamped)
        preview_guard["updating_seek"] = True
        preview_seek.set(clamped)
        preview_guard["updating_seek"] = False
        _update_preview_time_label()
        _request_live_preview_render()

    def _preview_tick():
        if not preview_guard["playing"] or preview_guard.get("kind") != "local":
            return
        next_time = preview_time_state.get() + 0.5
        if next_time >= preview_guard["duration"]:
            _render_local_preview_frame(preview_guard["duration"])
            _stop_preview_playback()
            return
        _render_local_preview_frame(next_time)
        preview_guard["after_id"] = root.after(500, _preview_tick)

    def toggle_preview_playback():
        if preview_guard.get("kind") != "local":
            preview_status_var.set("Link online hiện tại chỉ xem trước bằng ảnh đại diện. Nút Phát chỉ hỗ trợ file local.")
            return
        if preview_guard["playing"]:
            _stop_preview_playback()
            return
        preview_guard["playing"] = True
        preview_play_btn.config(text="Tạm Dừng")
        _preview_tick()

    def refresh_preview_frame():
        if preview_guard.get("kind") == "local":
            _render_local_preview_frame(preview_time_state.get())
        else:
            load_source_preview(force=True)

    def jump_to_segment(index: int):
        segments = preview_guard.get("segments") or []
        if index < 0 or index >= len(segments):
            return
        segment = segments[index]
        preview_guard["selected_segment"] = index
        preview_text_box.delete("1.0", tk.END)
        preview_text_box.insert("1.0", segment["text"])
        preview_time_state.set(float(segment["start"]))
        _update_preview_time_label()
        _render_segment_markers()
        if preview_guard.get("kind") == "local":
            _stop_preview_playback()
            _render_local_preview_frame(float(segment["start"]))
        preview_status_var.set(
            f"Đã nhảy tới phụ đề {index + 1} | {_format_duration(segment['start'])} -> {_format_duration(segment['end'])}"
        )
        update_preview()

    def reset_preview_position():
        margin_state.set(0)
        subtitle_offset_state.set(0.0)
        preview_status_var.set("Đã đặt lại vị trí phụ đề và độ lệch thời gian.")

    def reset_preview_style():
        preset_guard["applying"] = True
        preset_state.set("Mặc Định")
        preset_guard["applying"] = False
        apply_selected_preset()
        blur_padding_state.set(12)
        cover_offset_state.set(0)
        blur_power_state.set(4)
        preview_status_var.set("Đã đặt lại kiểu phụ đề và vùng che về mặc định.")

    def on_seek_changed(value):
        if preview_guard["updating_seek"]:
            return
        if preview_guard.get("kind") != "local":
            return
        _stop_preview_playback()
        _render_local_preview_frame(float(value))

    def _extract_remote_preview_frame(image_url: str) -> Path:
        preview_dir = HERE / "output" / "_preview_cache"
        preview_dir.mkdir(parents=True, exist_ok=True)
        out_path = preview_dir / "remote_preview.png"
        cmd = [
            ffmpeg_cmd(), "-y",
            "-i", image_url,
            "-frames:v", "1",
            "-update", "1",
            "-vf", "scale=480:-1",
            str(out_path),
        ]
        import subprocess
        subprocess.run(cmd, capture_output=True, check=True)
        return out_path

    def load_source_preview(force: bool = False):
        source = source_state.get().strip()
        if not source:
            preview_status_var.set("Chưa tải xem trước.")
            preview_guard["image"] = None
            preview_guard["kind"] = None
            preview_guard["source"] = None
            preview_guard["duration"] = 0.0
            preview_guard["path"] = None
            preview_guard["segments"] = []
            preview_seek.config(state=tk.DISABLED, to=100)
            preview_seek.set(0)
            _update_preview_time_label()
            _render_segment_markers()
            _stop_preview_playback()
            return
        if not force and preview_guard["source"] == source:
            return

        _stop_preview_playback()
        preview_status_var.set("Đang tải preview...")
        root.update_idletasks()
        try:
            if is_local_file(source):
                dims = get_dims(Path(source))
                duration = probe_duration(Path(source))
                preview_guard["kind"] = "local"
                preview_guard["duration"] = duration
                preview_guard["path"] = source
                preview_seek.config(state=tk.NORMAL, from_=0, to=max(duration, 0.1))
                _render_local_preview_frame(min(1.0, duration))
                preview_status_var.set(
                    f"Xem trước file local | {_format_duration(duration)} | {dims[0]}x{dims[1]} | {Path(source).name}"
                )
            else:
                info = fetch_preview_info(source)
                thumb = info.get("thumbnail")
                preview_guard["kind"] = "remote"
                preview_guard["duration"] = float(info.get("duration", 0) or 0)
                preview_guard["path"] = None
                preview_seek.config(state=tk.DISABLED, from_=0, to=max(preview_guard["duration"], 0.1))
                preview_seek.set(0)
                preview_time_state.set(0.0)
                _update_preview_time_label()
                if thumb:
                    preview_path = _extract_remote_preview_frame(thumb)
                    _set_preview_image(preview_path)
                else:
                    preview_guard["image"] = None
                preview_status_var.set(
                    f"{info.get('title','video')} | {_format_duration(info.get('duration', 0))} | "
                    f"{info.get('uploader','')} | {info.get('view_count', 0):,} lượt xem"
                )
        except Exception as exc:
            preview_guard["image"] = None
            preview_guard["kind"] = None
            preview_guard["duration"] = 0.0
            preview_guard["path"] = None
            preview_guard["segments"] = []
            preview_status_var.set(f"Tải preview thất bại: {exc}")
        finally:
            preview_guard["source"] = source
            preview_play_btn.config(text="Phát")
            _render_segment_markers()
            update_preview()

    def update_preview(*_args):
        if preview_guard.get("kind") == "local":
            _request_live_preview_render()
        preview_canvas.delete("all")
        preview_canvas.update_idletasks()
        width = max(preview_canvas.winfo_width(), 900)
        height = max(preview_canvas.winfo_height(), 320)
        font_scale = max(0.5, float(font_scale_state.get()))
        font_size = int(font_size_state.get())
        margin = int(margin_state.get())
        offset = float(subtitle_offset_state.get())
        timing_scale = max(0.5, float(subtitle_scale_state.get()))
        chars = int(chars_per_line_state.get())
        preview_text = _current_preview_text()
        preview_text_state.set(preview_text)
        preview_lines = preview_text.splitlines()[:2]
        while len(preview_lines) < 2:
            preview_lines.append("")

        preview_canvas.create_rectangle(0, 0, width, height, fill="#151515", outline="")
        image = preview_guard.get("image")
        side_pad = 24
        if image:
            img_w = image.width()
            img_h = image.height()
            img_x = width // 2
            img_y = height // 2
            preview_canvas.create_image(img_x, img_y, image=image, anchor="center", tags=("video_image",))
            video_left = img_x - img_w // 2
            video_top = img_y - img_h // 2
            video_right = video_left + img_w
            video_bottom = video_top + img_h
            if video_left < side_pad or video_right > width - side_pad:
                shift_x = 0
                if video_left < side_pad:
                    shift_x = side_pad - video_left
                elif video_right > width - side_pad:
                    shift_x = (width - side_pad) - video_right
                video_left += shift_x
                video_right += shift_x
                img_x += shift_x
                preview_canvas.coords("video_image", img_x, img_y)
            preview_guard["video_rect"] = (video_left, video_top, video_right, video_bottom)
            preview_canvas.create_rectangle(video_left, video_top, video_right, video_bottom, outline="#2d2d2d", width=2)
        else:
            video_left, video_top, video_right, video_bottom = 80, 36, width - 80, height - 70
            preview_guard["video_rect"] = (video_left, video_top, video_right, video_bottom)
            preview_canvas.create_rectangle(video_left, video_top, video_right, video_bottom, fill="#1d1d1d", outline="#2d2d2d", width=2)
            preview_canvas.create_text(width / 2, (video_top + video_bottom) / 2, text="Chưa có khung hình preview", fill="#94a3b8", font=("Arial", 13, "bold"))

        preview_canvas.create_text(
            video_left + 18, video_top + 18,
            anchor="nw",
            text="Kéo trực tiếp khung phụ đề trên video để căn vị trí. Lăn chuột để đổi cỡ chữ.",
            fill="#9ab",
            font=("Arial", 11),
        )

        render_meta = preview_guard.get("render_meta") or {}
        meta_video_w = int(render_meta.get("video_width") or 0)
        meta_video_h = int(render_meta.get("video_height") or 0)
        meta_top_y = render_meta.get("subtitle_top_y")
        meta_bottom_y = render_meta.get("subtitle_bottom_y")
        cover_top_y = render_meta.get("cover_top_y")
        cover_bottom_y = render_meta.get("cover_bottom_y")
        canvas_video_h = max(video_bottom - video_top, 1)
        canvas_video_w = max(video_right - video_left, 1)

        layout_video_h = meta_video_h if meta_video_h > 0 else max(int(canvas_video_h), 1)
        layout = compute_subtitle_layout(
            layout_video_h,
            meta_top_y,
            meta_bottom_y,
            font_scale=font_scale,
            font_size_override=font_size,
            margin_offset=margin,
        )
        font_px = max(12, int((layout["font_size"] / layout_video_h) * canvas_video_h))
        line_height = max(font_px + 3, int(font_px * 1.12))
        active_lines = [line for line in preview_lines if line.strip()]
        if not active_lines:
            active_lines = [preview_lines[0]]
        line_count = len(active_lines)
        text_padding_x = max(10, int(font_px * 0.45))
        text_padding_y = max(6, int(font_px * 0.22))
        text_block_height = max(line_height * line_count, font_px)
        subtitle_bottom_canvas = video_bottom - (layout["margin_v"] / layout_video_h) * canvas_video_h
        subtitle_bottom_canvas = max(
            video_top + text_block_height + text_padding_y * 2 + 8,
            min(video_bottom - 4, subtitle_bottom_canvas),
        )
        subtitle_top_canvas = max(video_top + 8, subtitle_bottom_canvas - text_block_height - text_padding_y * 2)

        blur_padding = max(0, int(blur_padding_state.get()))
        cover_offset = int(cover_offset_state.get())
        if meta_video_h > 0 and cover_top_y is not None and cover_bottom_y is not None:
            preview_cover_top, preview_cover_bottom = shift_band(int(cover_top_y), int(cover_bottom_y), meta_video_h, cover_offset)
            blur_top = video_top + (int(preview_cover_top) / meta_video_h) * canvas_video_h
            blur_bottom = video_top + (int(preview_cover_bottom) / meta_video_h) * canvas_video_h
        elif meta_video_h > 0 and meta_top_y is not None and meta_bottom_y is not None:
            preview_cover_top, preview_cover_bottom = expand_band_from_center(meta_top_y, meta_bottom_y, meta_video_h, blur_padding)
            preview_cover_top, preview_cover_bottom = shift_band(preview_cover_top, preview_cover_bottom, meta_video_h, cover_offset)
            blur_top = video_top + (int(preview_cover_top) / meta_video_h) * canvas_video_h
            blur_bottom = video_top + (int(preview_cover_bottom) / meta_video_h) * canvas_video_h
        else:
            preview_cover_top, preview_cover_bottom = expand_band_from_center(
                int(subtitle_top_canvas),
                int(subtitle_bottom_canvas),
                int(canvas_video_h),
                blur_padding,
            )
            preview_cover_top, preview_cover_bottom = shift_band(preview_cover_top, preview_cover_bottom, int(canvas_video_h), cover_offset)
            blur_top = video_top + int(preview_cover_top)
            blur_bottom = video_top + int(preview_cover_bottom)
        blur_top = max(video_top + 6, blur_top)
        blur_bottom = min(video_bottom - 6, blur_bottom)
        if meta_video_w > 0:
            blur_side_pad = max(8, int((28 / meta_video_w) * canvas_video_w))
            sub_side_pad = max(12, int((36 / meta_video_w) * canvas_video_w))
        else:
            blur_side_pad = 28
            sub_side_pad = 36
        blur_power = max(1, int(blur_power_state.get()))
        blur_stipple = {1: "gray12", 2: "gray25", 3: "gray25", 4: "gray50", 5: "gray50", 6: "gray50", 7: "gray75", 8: "gray75", 9: "gray75", 10: "gray75"}.get(blur_power, "gray50")
        cover_mode = cover_mode_state.get()
        live_render = bool(preview_guard.get("live_render"))
        if cover_mode == "blur" and not live_render:
            preview_canvas.create_rectangle(
                video_left,
                blur_top,
                video_right,
                blur_bottom,
                fill="#7c8aa0",
                stipple=blur_stipple,
                outline="#f59e0b",
                dash=(8, 5),
                width=max(2, min(4, 1 + blur_power // 3)),
            )
        elif cover_mode == "blackbar" and not live_render:
            preview_canvas.create_rectangle(
                video_left,
                blur_top,
                video_right,
                blur_bottom,
                fill="#000000",
                outline="#64748b",
                width=2,
            )
        text_item_ids = []
        first_line_bottom = subtitle_bottom_canvas - text_padding_y
        for idx, line in enumerate(reversed(active_lines)):
            y = first_line_bottom - idx * line_height
            item_id = preview_canvas.create_text(
                (video_left + video_right) / 2,
                y,
                text=line,
                fill="" if live_render else "white",
                anchor="s",
                font=("Arial", font_px, "bold"),
            )
            text_item_ids.append(item_id)
        bbox = None
        for item_id in text_item_ids:
            item_bbox = preview_canvas.bbox(item_id)
            if not item_bbox:
                continue
            if bbox is None:
                bbox = list(item_bbox)
            else:
                bbox[0] = min(bbox[0], item_bbox[0])
                bbox[1] = min(bbox[1], item_bbox[1])
                bbox[2] = max(bbox[2], item_bbox[2])
                bbox[3] = max(bbox[3], item_bbox[3])
        if bbox is None:
            bbox = [
                int((video_left + video_right) / 2 - 140),
                int(subtitle_top_canvas),
                int((video_left + video_right) / 2 + 140),
                int(subtitle_bottom_canvas),
            ]
        subtitle_rect = (
            max(video_left + 8, bbox[0] - text_padding_x),
            max(video_top + 8, bbox[1] - text_padding_y),
            min(video_right - 8, bbox[2] + text_padding_x),
            min(video_bottom - 4, bbox[3] + text_padding_y),
        )
        preview_canvas.create_rectangle(
            *subtitle_rect,
            fill="" if live_render else "#000000",
            stipple="" if live_render else "gray50",
            outline="#4ea1ff",
            width=2,
            tags=("subtitle_preview",),
        )
        preview_canvas.create_line(
            subtitle_rect[0],
            subtitle_rect[3],
            subtitle_rect[2],
            subtitle_rect[3],
            fill="#7dd3fc",
            dash=(4, 3),
            tags=("subtitle_preview",),
        )
        preview_guard["subtitle_rect"] = subtitle_rect
        for item_id in text_item_ids:
            preview_canvas.addtag_withtag("subtitle_preview", item_id)
        preview_canvas.create_text(
            video_right - 72,
            max(video_top + 14, subtitle_rect[1] - 14),
            text="Kéo / Lăn",
            fill="#7fb6ff",
            font=("Arial", 10, "bold"),
            tags=("subtitle_preview",),
        )
        preview_info_var.set(
            f"Mẫu: {preset_state.get()} | Lệch thời gian: {offset:+.1f}s | Tỉ lệ tốc độ: {timing_scale:.2f} | "
            f"Tỉ lệ chữ: {font_scale:.2f} | Cỡ chữ: {font_size or 'tự động'} | "
            f"Lệch vị trí dọc: {margin}px | Ký tự mỗi dòng: {chars} | "
            f"Nới vùng che: {blur_padding}px | Đẩy vùng che lên: {cover_offset}px | Độ mờ: {int(blur_power_state.get())} | "
            f"Font render: {layout['font_size']} | MarginV render: {layout['margin_v']}"
        )

        preview_canvas.tag_bind("subtitle_preview", "<ButtonPress-1>", start_subtitle_drag)
        preview_canvas.tag_bind("subtitle_preview", "<B1-Motion>", drag_subtitle_preview)
        preview_canvas.tag_bind("subtitle_preview", "<ButtonRelease-1>", stop_subtitle_drag)

    def _margin_from_canvas_y(y: int) -> int:
        _video_left, video_top, _video_right, video_bottom = preview_guard.get("video_rect", (0, 0, 0, 0))
        render_meta = preview_guard.get("render_meta") or {}
        meta_video_h = int(render_meta.get("video_height") or 0)
        meta_top_y = render_meta.get("subtitle_top_y")
        meta_bottom_y = render_meta.get("subtitle_bottom_y")
        if video_bottom <= video_top:
            return int(margin_state.get())
        layout_video_h = meta_video_h if meta_video_h > 0 else max(int(video_bottom - video_top), 1)
        base_layout = compute_subtitle_layout(
            layout_video_h,
            meta_top_y,
            meta_bottom_y,
            font_scale=float(font_scale_state.get()),
            font_size_override=int(font_size_state.get()),
            margin_offset=0,
        )
        dragged_bottom = max(video_top + 48, min(video_bottom - 12, y))
        dragged_margin_v = ((video_bottom - dragged_bottom) / max(video_bottom - video_top, 1)) * layout_video_h
        new_margin = int(round(dragged_margin_v - base_layout["margin_v"]))
        return max(-240, min(240, new_margin))

    def _point_in_rect(x: int, y: int, rect: tuple[int, int, int, int], padding: int = 0) -> bool:
        left, top, right, bottom = rect
        return left - padding <= x <= right + padding and top - padding <= y <= bottom + padding

    def start_subtitle_drag(event):
        preview_guard["drag_x_start"] = event.x
        preview_guard["drag_y_start"] = event.y
        preview_guard["drag_margin_start"] = int(margin_state.get())
        preview_guard["drag_active"] = True
        preview_canvas.config(cursor="fleur")

    def drag_subtitle_preview(event):
        if not preview_guard.get("drag_active"):
            return
        margin_state.set(_margin_from_canvas_y(event.y))

    def stop_subtitle_drag(_event):
        preview_guard["drag_active"] = False
        preview_canvas.config(cursor="hand2")
        preview_status_var.set(
            f"Đã kéo phụ đề trên video: lệch vị trí dọc = {int(margin_state.get())} px"
        )

    def start_canvas_drag(event):
        video_rect = preview_guard.get("video_rect", (0, 0, 0, 0))
        subtitle_rect = preview_guard.get("subtitle_rect", (0, 0, 0, 0))
        if _point_in_rect(event.x, event.y, subtitle_rect, padding=42) or _point_in_rect(event.x, event.y, video_rect):
            start_subtitle_drag(event)
            margin_state.set(_margin_from_canvas_y(event.y))

    def drag_canvas_subtitle(event):
        if preview_guard.get("drag_active"):
            drag_subtitle_preview(event)

    def stop_canvas_drag(event):
        if preview_guard.get("drag_active"):
            stop_subtitle_drag(event)

    def _adjust_font_size(delta: int):
        current = int(font_size_state.get())
        if current <= 0:
            current = max(18, int(24 * max(0.5, float(font_scale_state.get()))))
        font_size_state.set(max(10, min(96, current + delta)))
        preview_status_var.set(f"Đã đổi cỡ chữ xem trước = {int(font_size_state.get())} pt")

    def on_subtitle_wheel(event):
        preview_guard["over_preview"] = True
        if event.delta > 0:
            _adjust_font_size(2)
        elif event.delta < 0:
            _adjust_font_size(-2)
        return "break"

    def on_subtitle_wheel_linux(event):
        preview_guard["over_preview"] = True
        if getattr(event, "num", None) == 4:
            _adjust_font_size(2)
        elif getattr(event, "num", None) == 5:
            _adjust_font_size(-2)
        return "break"

    for state in (cover_mode_state, subtitle_offset_state, subtitle_scale_state, font_scale_state, font_size_state, margin_state, chars_per_line_state, blur_padding_state, cover_offset_state, blur_power_state):
        state.trace(mark_preset_custom)
        state.trace(update_preview)
    preset_state.trace(apply_selected_preset)
    dub_mode_state.trace(sync_dub_mode)
    dub_backend_mode_state.trace(sync_dub_mode)
    dub_backend_mode_state.trace(lambda *_args: refresh_voice_list())
    preview_text_box.bind("<KeyRelease>", on_preview_text_changed)
    preview_play_btn.config(command=toggle_preview_playback)
    preview_refresh_btn.config(command=refresh_preview_frame)
    preview_reset_pos_btn.config(command=reset_preview_position)
    preview_reset_style_btn.config(command=reset_preview_style)
    open_output_btn.config(command=open_render_folder)
    dub_refresh_voice_btn.config(command=refresh_voice_list)
    dub_browse_ref_btn.config(command=browse_ref_audio)
    dub_preview_btn.config(command=play_tts_preview)
    dub_stop_preview_btn.config(command=stop_preview_audio)
    preview_seek.config(command=on_seek_changed)
    preview_marker_canvas.bind("<Configure>", lambda _e: _render_segment_markers())
    preview_canvas.bind("<Configure>", update_preview)
    preview_canvas.bind("<ButtonPress-1>", start_canvas_drag)
    preview_canvas.bind("<B1-Motion>", drag_canvas_subtitle)
    preview_canvas.bind("<ButtonRelease-1>", stop_canvas_drag)
    preview_canvas.bind("<MouseWheel>", on_subtitle_wheel)
    preview_canvas.bind("<Button-4>", on_subtitle_wheel_linux)
    preview_canvas.bind("<Button-5>", on_subtitle_wheel_linux)
    preview_canvas.bind("<Enter>", lambda _e: preview_guard.__setitem__("over_preview", True))
    preview_canvas.bind("<Leave>", lambda _e: preview_guard.__setitem__("over_preview", False))
    preview_canvas.config(cursor="hand2")
    _bind_scroll_recursive(adjust_left)
    notebook.bind("<<NotebookTabChanged>>", lambda e: load_source_preview(force=False) if notebook.tab(notebook.select(), "text") == "Căn Chỉnh" else None)
    sync_dub_mode()
    root.after(150, refresh_voice_list)
    root.after(100, update_preview)
    load_preview_segments(app_config.get("last_render_dir", ""))
    
    def start_processing():
        source = source_state.get()
        if not source:
            log("[ERROR] Vui lòng nhập link video hoặc đường dẫn file")
            return

        if not is_local_file(source):
            ok, preflight_msg = check_source_preconditions(source)
            if preflight_msg:
                level = "[INFO]" if ok else "[ERROR]"
                log(f"{level} Preflight: {preflight_msg}")
            if not ok:
                return

        if enable_dub_state.get():
            backend_mode = dub_backend_mode_state.get()
            remote_api_base = dub_remote_api_base_state.get().strip()
            if not is_vieneu_available(engine_mode=backend_mode, remote_api_base=remote_api_base):
                log(f"[ERROR] VieNeu-TTS chưa sẵn sàng: {get_vieneu_error(engine_mode=backend_mode, remote_api_base=remote_api_base)}")
                notebook.select(dub_tab)
                return
            if backend_mode == "remote" and not remote_api_base:
                log("[ERROR] Vui lòng nhập Remote API Base khi dùng mode remote")
                notebook.select(dub_tab)
                return
            if dub_mode_state.get() == "preset" and not dub_preset_voice_state.get():
                log("[ERROR] Vui lòng chọn giọng mẫu để lồng tiếng")
                notebook.select(dub_tab)
                return
            if dub_mode_state.get() == "clone" and not Path(dub_ref_audio_state.get()).exists():
                log("[ERROR] Vui lòng chọn file audio mẫu hợp lệ để clone giọng")
                notebook.select(dub_tab)
                return
        
        # Save settings
        save_app_config({
            "source_input": source,
            "cover_mode": cover_mode_state.get(),
            "whisper_model": whisper_model_state.get(),
            "burn_sub": burn_sub_state.get(),
            "subtitle_offset_sec": float(subtitle_offset_state.get()),
            "subtitle_timing_scale": float(subtitle_scale_state.get()),
            "video_speed": float(video_speed_state.get()),
            "subtitle_font_scale": float(font_scale_state.get()),
            "subtitle_font_size": int(font_size_state.get()),
            "subtitle_margin_px": int(margin_state.get()),
            "srt_max_chars_per_line": int(chars_per_line_state.get()),
            "blur_padding_px": int(blur_padding_state.get()),
            "cover_offset_px": int(cover_offset_state.get()),
            "blur_power": int(blur_power_state.get()),
            "subtitle_preset": preset_state.get(),
            "preview_text": preview_text_box.get("1.0", tk.END).strip(),
            "enable_dub": bool(enable_dub_state.get()),
            "dub_mode": dub_mode_state.get(),
            "dub_backend_mode": dub_backend_mode_state.get(),
            "dub_remote_api_base": dub_remote_api_base_state.get().strip(),
            "dub_preset_voice": dub_preset_voice_state.get(),
            "dub_ref_audio": dub_ref_audio_state.get(),
            "dub_ref_text": ref_text_box.get("1.0", tk.END).strip(),
            "dub_voice_volume": float(dub_voice_volume_state.get()),
            "dub_source_volume": float(dub_source_volume_state.get()),
            "dub_mix_mode": dub_mix_mode_state.get(),
            "tts_preview_text": tts_preview_box.get("1.0", tk.END).strip(),
        })
        
        # Update config
        config["whisper_model"] = whisper_model_state.get()
        config["video_speed"] = float(video_speed_state.get())
        config["blur_padding_px"] = int(blur_padding_state.get())
        config["cover_offset_px"] = int(cover_offset_state.get())
        config["blur_power"] = int(blur_power_state.get())
        
        log("[INFO] Starting processing...")
        log(f"[INFO] Nguồn: {source}")
        log(f"[INFO] Cover mode: {cover_mode_state.get()}")
        log(f"[INFO] Whisper model: {whisper_model_state.get()}")
        log(
            "[INFO] Chỉnh phụ đề:",
            f"offset={float(subtitle_offset_state.get()):+.1f}s",
            f"timing_scale={float(subtitle_scale_state.get()):.2f}",
            f"video_speed={float(video_speed_state.get()):.2f}x",
            f"font_scale={float(font_scale_state.get()):.2f}",
            f"font_size={int(font_size_state.get()) or 'auto'}",
            f"margin={int(margin_state.get())}px",
            f"chars={int(chars_per_line_state.get())}",
            f"preset={preset_state.get()}",
            f"blur_padding={int(blur_padding_state.get())}px",
            f"cover_offset={int(cover_offset_state.get())}px",
            f"blur_power={int(blur_power_state.get())}",
        )
        log(
            "[INFO] Lồng tiếng:",
            f"bat={bool(enable_dub_state.get())}",
            f"mode={dub_mode_state.get()}",
            f"backend={dub_backend_mode_state.get()}",
            f"voice={dub_preset_voice_state.get() or '(clone)'}",
            f"voice_volume={float(dub_voice_volume_state.get()):.2f}",
            f"source_volume={float(dub_source_volume_state.get()):.2f}",
            f"mix={dub_mix_mode_state.get()}",
        )
        
        try:
            # Disable buttons during processing
            start_btn.config(state=tk.DISABLED)
            
            # Process video
            result = process_video(
                source_input=source,
                cover_mode=cover_mode_state.get(),
                burn_sub=burn_sub_state.get(),
                log_cb=log,
                subtitle_offset_sec=float(subtitle_offset_state.get()),
                subtitle_timing_scale=float(subtitle_scale_state.get()),
                video_speed=float(video_speed_state.get()),
                srt_max_chars_per_line=int(chars_per_line_state.get()),
                subtitle_font_scale=float(font_scale_state.get()),
                subtitle_font_size=int(font_size_state.get()),
                subtitle_margin_px=int(margin_state.get()),
                blur_padding_px=int(blur_padding_state.get()),
                cover_offset_px=int(cover_offset_state.get()),
                blur_power=int(blur_power_state.get()),
                enable_dub=bool(enable_dub_state.get()),
                dub_mode=dub_mode_state.get(),
                dub_backend_mode=dub_backend_mode_state.get(),
                dub_remote_api_base=dub_remote_api_base_state.get().strip(),
                dub_preset_voice=dub_preset_voice_state.get(),
                dub_ref_audio=dub_ref_audio_state.get(),
                dub_ref_text=ref_text_box.get("1.0", tk.END).strip(),
                dub_voice_volume=float(dub_voice_volume_state.get()),
                dub_source_volume=float(dub_source_volume_state.get()),
                dub_mix_mode=dub_mix_mode_state.get(),
            )
            
            if result:
                save_app_config({"last_render_dir": result})
                last_output_var.set(result)
                load_preview_segments(result)
                log(f"[SUCCESS] Processing complete!")
                log(f"[INFO] Output: {result}")
                notebook.select(adjust_tab)
            else:
                log("[ERROR] Processing failed")
                notebook.select(log_tab)
        
        except Exception as e:
            log(f"[ERROR] {str(e)}")
        
        finally:
            start_btn.config(state=tk.NORMAL)

    # ═══════════════════════════════════════════════════════════
    # SECTION 8: Controller Initialization & Event Wiring
    # ═══════════════════════════════════════════════════════════
    # Create SourceController and wire to UI
    source_ctrl = SourceController(
        start_processing_fn=start_processing,
        run_step_fn=run_up_to_step
    )

    # Wire start button to controller
    start_btn.config(command=source_ctrl.on_start_clicked)

    # Wire step buttons to controller
    for i, btn in enumerate(step_btn_widgets):
        step_num = i + 1
        btn.config(command=lambda n=step_num: source_ctrl.on_step_clicked(n))

    # Create SubtitleController and TtsController
    subtitle_ctrl = SubtitleController(
        on_cover_mode_changed_fn=None,  # Cover mode handled by state binding
        on_preset_changed_fn=apply_selected_preset,
        on_param_changed_fn=None  # Params handled by state bindings
    )

    tts_ctrl = TtsController(
        on_dub_mode_changed_fn=sync_dub_mode,
        on_voice_changed_fn=None,  # Voice handled by state binding
        play_tts_preview_fn=play_tts_preview,
        stop_preview_audio_fn=stop_preview_audio
    )

    # Create AppController
    app_ctrl = AppController(
        save_config_fn=save_app_config,
        load_config_fn=load_app_config
    )

    # ═══════════════════════════════════════════════════════════
    # SECTION 9: Start Application
    # ═══════════════════════════════════════════════════════════
    root.mainloop()

if __name__ == "__main__":
    # Initialize logging
    logger = setup_logging()
    logger.info("Application started")

    launch_gui()
