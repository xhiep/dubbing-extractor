"""Dub tab view - TTS configuration and voice selection."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable

from ..components.ui import Checkbox
from ..components.layout import Card
from ..components.theme import T
from ..modules.tts import list_preset_voices, is_vieneu_available, get_vieneu_error


class DubView:
    """Dub tab view - TTS configuration, voice selection, and dubbing controls."""

    def __init__(self,
                 parent: tk.Widget,
                 state: Dict[str, Any],
                 callbacks: Dict[str, Callable]):
        """Initialize dub view.

        Args:
            parent: Parent widget (notebook)
            state: Dictionary of tk state variables
                - enable_dub_state: BooleanVar for enable dubbing
                - dub_mode_state: StringVar for TTS mode (preset/clone)
                - dub_backend_mode_state: StringVar for VieNeu backend
                - dub_remote_api_base_state: StringVar for remote API URL
                - dub_preset_voice_state: StringVar for preset voice selection
                - dub_ref_audio_state: StringVar for reference audio path
                - dub_ref_text_state: StringVar for reference text
                - dub_voice_volume_state: DoubleVar for voice volume
                - dub_source_volume_state: DoubleVar for source volume
                - dub_mix_mode_state: StringVar for mix mode
                - tts_preview_text_state: StringVar for preview text
            callbacks: Dictionary of callback functions
                - browse_ref_audio: Function to open file dialog for reference audio
                - log: Function to log messages
        """
        self.parent = parent
        self.state = state
        self.callbacks = callbacks
        self.widgets = {}

    def build(self) -> tk.Frame:
        """Build and return the dub tab frame.

        Returns:
            Configured tk.Frame ready to add to notebook
        """
        # Create tab frame
        frame = tk.Frame(self.parent, padx=16, pady=16, bg=T.BG_WHITE)

        # Helper functions for consistent styling
        def _lbl(parent, text):
            return tk.Label(parent, text=text, anchor="w",
                          font=T.FONT_BODY, fg=T.TEXT_PRIMARY, bg=T.BG_LIGHT)

        def _hint(parent, text):
            return tk.Label(parent, text=text, anchor="w",
                          font=T.FONT_SMALL, fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT)

        # Dubbing card
        dub_card = Card(frame, title="Long Tieng Tieng Viet")
        dub_container = dub_card.get_container()

        tts_status_var = tk.StringVar(value="VieNeu-TTS chua duoc kiem tra.")
        tts_status_label = tk.Label(dub_container, textvariable=tts_status_var,
                                    anchor="w", justify=tk.LEFT,
                                    fg=T.TEXT_SECONDARY, bg=T.BG_LIGHT,
                                    font=T.FONT_SMALL)
        tts_status_label.pack(fill=tk.X, pady=(0, 8))

        enable_dub_check = Checkbox(dub_container, text="Bat long tieng tieng Viet",
                                    default=self.state['enable_dub_state'].get())
        enable_dub_check.var = self.state['enable_dub_state'].var
        enable_dub_check.pack(anchor=tk.W, pady=(0, 8))

        dub_mode_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
        dub_mode_row.pack(fill=tk.X, pady=4)
        _lbl(dub_mode_row, "Che Do Giong:").pack(side=tk.LEFT)
        tk.Radiobutton(dub_mode_row, text="Giong mau", variable=self.state['dub_mode_state'].var, value="preset",
                       font=T.FONT_BODY, bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                       activebackground=T.BG_LIGHT, selectcolor=T.BG_WHITE,
                       relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=4)
        tk.Radiobutton(dub_mode_row, text="Clone tu file", variable=self.state['dub_mode_state'].var, value="clone",
                       font=T.FONT_BODY, bg=T.BG_LIGHT, fg=T.TEXT_PRIMARY,
                       activebackground=T.BG_LIGHT, selectcolor=T.BG_WHITE,
                       relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=4)

        dub_backend_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
        dub_backend_row.pack(fill=tk.X, pady=4)
        _lbl(dub_backend_row, "Backend VieNeu:").pack(side=tk.LEFT)
        dub_backend_combo = ttk.Combobox(
            dub_backend_row, textvariable=self.state['dub_backend_mode_state'].var,
            values=["turbo", "turbo_gpu", "standard", "fast", "remote", "xpu"],
            width=18, state="readonly",
        )
        dub_backend_combo.pack(side=tk.LEFT)
        _hint(dub_backend_row, "turbo=CPU nhanh | turbo_gpu/fast=GPU | remote=server").pack(side=tk.LEFT, padx=8)

        dub_remote_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
        dub_remote_row.pack(fill=tk.X, pady=4)
        _lbl(dub_remote_row, "Remote API:").pack(side=tk.LEFT)
        dub_remote_entry = tk.Entry(dub_remote_row, textvariable=self.state['dub_remote_api_base_state'].var, width=48,
                                    font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY,
                                    relief=tk.FLAT, borderwidth=1,
                                    insertbackground=T.ACCENT)
        dub_remote_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        preset_voice_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
        preset_voice_row.pack(fill=tk.X, pady=4)
        _lbl(preset_voice_row, "Giong Mau:").pack(side=tk.LEFT)
        preset_voice_combo = ttk.Combobox(
            preset_voice_row, textvariable=self.state['dub_preset_voice_state'].var,
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
        ref_audio_entry = tk.Entry(ref_audio_row, textvariable=self.state['dub_ref_audio_state'].var, width=56,
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
        ref_text_box.insert("1.0", self.state['dub_ref_text_state'].get())

        dub_mix_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
        dub_mix_row.pack(fill=tk.X, pady=4)
        _lbl(dub_mix_row, "Am Luong Giong:").pack(side=tk.LEFT)
        tk.Spinbox(dub_mix_row, from_=0.5, to=3.0, increment=0.05, textvariable=self.state['dub_voice_volume_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(dub_mix_row, "1.0 = giu nguyen | tang neu giong doc con nho").pack(side=tk.LEFT, padx=8)

        dub_source_mix_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
        dub_source_mix_row.pack(fill=tk.X, pady=4)
        _lbl(dub_source_mix_row, "Am Luong Goc:").pack(side=tk.LEFT)
        tk.Spinbox(dub_source_mix_row, from_=0.0, to=1.0, increment=0.05, textvariable=self.state['dub_source_volume_state'].var, width=8,
                   font=T.FONT_BODY, bg=T.BG_WHITE, fg=T.TEXT_PRIMARY, relief=tk.FLAT, borderwidth=1).pack(side=tk.LEFT)
        _hint(dub_source_mix_row, "0 = tat tieng goc, 0.18 = nen nho phia sau").pack(side=tk.LEFT, padx=8)

        dub_mix_mode_row = tk.Frame(dub_container, bg=T.BG_LIGHT)
        dub_mix_mode_row.pack(fill=tk.X, pady=4)
        _lbl(dub_mix_mode_row, "Cach Mix Audio:").pack(side=tk.LEFT)
        dub_mix_mode_combo = ttk.Combobox(
            dub_mix_mode_row, textvariable=self.state['dub_mix_mode_state'].var,
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
        tts_preview_box.insert("1.0", self.state['tts_preview_text_state'].get())

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

        # Store widget references for controller access
        self.widgets['tts_status_var'] = tts_status_var
        self.widgets['tts_status_label'] = tts_status_label
        self.widgets['enable_dub_check'] = enable_dub_check
        self.widgets['dub_backend_combo'] = dub_backend_combo
        self.widgets['dub_remote_entry'] = dub_remote_entry
        self.widgets['preset_voice_combo'] = preset_voice_combo
        self.widgets['dub_refresh_voice_btn'] = dub_refresh_voice_btn
        self.widgets['ref_audio_entry'] = ref_audio_entry
        self.widgets['dub_browse_ref_btn'] = dub_browse_ref_btn
        self.widgets['ref_text_box'] = ref_text_box
        self.widgets['tts_preview_box'] = tts_preview_box
        self.widgets['dub_preview_btn'] = dub_preview_btn
        self.widgets['dub_stop_preview_btn'] = dub_stop_preview_btn

        return frame

    def get_widgets(self) -> Dict[str, Any]:
        """Get widget references for controller access.

        Returns:
            Dictionary of widget references
        """
        return self.widgets
