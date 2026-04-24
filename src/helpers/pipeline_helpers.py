"""Pipeline management helper functions."""
from pathlib import Path
from typing import Callable, Optional


def collect_params(state_getters: dict) -> dict:
    """Collect all parameters from UI state."""
    return dict(
        source_input=state_getters['source_state'].get().strip(),
        cover_mode=state_getters['cover_mode_state'].get(),
        whisper_model=state_getters['whisper_model_state'].get(),
        burn_sub=state_getters['burn_sub_state'].get(),
        subtitle_offset_sec=float(state_getters['subtitle_offset_state'].get()),
        subtitle_timing_scale=float(state_getters['subtitle_scale_state'].get()),
        video_speed=float(state_getters['video_speed_state'].get()),
        srt_max_chars_per_line=int(state_getters['chars_per_line_state'].get()),
        subtitle_font_scale=float(state_getters['font_scale_state'].get()),
        subtitle_font_size=int(state_getters['font_size_state'].get()),
        subtitle_margin_px=int(state_getters['margin_state'].get()),
        blur_padding_px=int(state_getters['blur_padding_state'].get()),
        cover_offset_px=int(state_getters['cover_offset_state'].get()),
        blur_power=int(state_getters['blur_power_state'].get()),
        enable_dub=bool(state_getters['enable_dub_state'].get()),
        dub_mode=state_getters['dub_mode_state'].get(),
        dub_backend_mode=state_getters['dub_backend_mode_state'].get(),
        dub_remote_api_base=state_getters['dub_remote_api_base_state'].get().strip(),
        dub_preset_voice=state_getters['dub_preset_voice_state'].get(),
        dub_ref_audio=state_getters['dub_ref_audio_state'].get(),
        dub_ref_text=state_getters['ref_text_box'].get("1.0", "end").strip(),
        dub_voice_volume=float(state_getters['dub_voice_volume_state'].get()),
        dub_source_volume=float(state_getters['dub_source_volume_state'].get()),
        dub_mix_mode=state_getters['dub_mix_mode_state'].get(),
    )


class PipelineManager:
    """Manages pipeline state and step execution."""

    def __init__(
        self,
        pipeline_state: dict,
        step_btn_widgets: list,
        status_var,
        status_label,
        srt_editor,
        srt_file_label_var,
        open_srt_btn,
        reload_srt_btn,
        save_srt_btn,
        step_colors: dict,
    ):
        self.pipeline_state = pipeline_state
        self.step_btn_widgets = step_btn_widgets
        self.status_var = status_var
        self.status_label = status_label
        self.srt_editor = srt_editor
        self.srt_file_label_var = srt_file_label_var
        self.open_srt_btn = open_srt_btn
        self.reload_srt_btn = reload_srt_btn
        self.save_srt_btn = save_srt_btn
        self.step_colors = step_colors

    def set_status(self, msg: str, color: str = "#7f8c8d"):
        """Set pipeline status message."""
        self.status_var.set(msg)
        self.status_label.config(fg=color)

    def update_step_buttons(self, running_step: int = -1):
        """Update step button colors based on pipeline state."""
        done = self.pipeline_state["current_step"]
        for i, btn in enumerate(self.step_btn_widgets):
            step_num = i + 1
            if step_num == running_step:
                btn.config(bg=self.step_colors['running'], state="disabled")
            elif step_num <= done:
                btn.config(bg=self.step_colors['done'], state="normal")
            else:
                btn.config(bg=self.step_colors['idle'], state="normal")

    def mark_step_error(self, step_num: int):
        """Mark a step as errored."""
        if 1 <= step_num <= len(self.step_btn_widgets):
            self.step_btn_widgets[step_num - 1].config(
                bg=self.step_colors['error'],
                state="normal"
            )

    def enable_srt_editor(self, srt_path: str):
        """Enable SRT editor with file content."""
        self.srt_editor.config(state="normal", bg="white")
        self.srt_editor.delete("1.0", "end")
        try:
            content = Path(srt_path).read_text(encoding="utf-8")
            self.srt_editor.insert("1.0", content)
        except Exception as exc:
            self.srt_editor.insert("1.0", f"[Không đọc được file: {exc}]")
        self.open_srt_btn.config(state="normal")
        self.reload_srt_btn.config(state="normal")
        self.save_srt_btn.config(state="normal")
        self.srt_file_label_var.set(Path(srt_path).name)

    def disable_srt_editor(self):
        """Disable SRT editor."""
        self.srt_editor.config(state="disabled", bg="#f8f9fa")
        self.open_srt_btn.config(state="disabled")
        self.reload_srt_btn.config(state="disabled")
        self.save_srt_btn.config(state="disabled")
        self.srt_file_label_var.set("(Chưa có file SRT)")

    def reset(self):
        """Reset pipeline state."""
        self.pipeline_state.update({
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
            "current_step": 0,
        })
        self.update_step_buttons()
        self.disable_srt_editor()
        self.set_status("● Đã reset. Sẵn sàng chạy lại.", "#7f8c8d")
