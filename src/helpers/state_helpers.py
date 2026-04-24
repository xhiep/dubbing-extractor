"""State management and preset helpers."""
from typing import Callable, Optional


class PresetManager:
    """Manages subtitle preset application."""

    def __init__(
        self,
        preset_state,
        subtitle_offset_state,
        subtitle_scale_state,
        font_scale_state,
        font_size_state,
        margin_state,
        chars_per_line_state,
        preset_guard: dict,
        presets: dict,
        update_preview_fn: Callable,
    ):
        self.preset_state = preset_state
        self.subtitle_offset_state = subtitle_offset_state
        self.subtitle_scale_state = subtitle_scale_state
        self.font_scale_state = font_scale_state
        self.font_size_state = font_size_state
        self.margin_state = margin_state
        self.chars_per_line_state = chars_per_line_state
        self.preset_guard = preset_guard
        self.presets = presets
        self.update_preview_fn = update_preview_fn

    def mark_custom(self, *_args):
        """Mark preset as custom when user changes values."""
        if self.preset_guard["applying"]:
            return
        if self.preset_state.get() != "Tùy Chỉnh":
            self.preset_state.set("Tùy Chỉnh")

    def apply_selected(self, *_args):
        """Apply selected preset values."""
        preset_name = self.preset_state.get()
        values = self.presets.get(preset_name)
        if not values:
            self.update_preview_fn()
            return
        self.preset_guard["applying"] = True
        self.subtitle_offset_state.set(values["subtitle_offset_sec"])
        self.subtitle_scale_state.set(values["subtitle_timing_scale"])
        self.font_scale_state.set(values["subtitle_font_scale"])
        self.font_size_state.set(values["subtitle_font_size"])
        self.margin_state.set(values["subtitle_margin_px"])
        self.chars_per_line_state.set(values["srt_max_chars_per_line"])
        self.preset_guard["applying"] = False
        self.update_preview_fn()


def setup_state_traces(
    states: list,
    mark_custom_fn: Callable,
    update_preview_fn: Callable,
):
    """Setup state variable traces."""
    for state in states:
        state.trace(mark_custom_fn)
        state.trace(update_preview_fn)
