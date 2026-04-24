"""Enhanced progress bar with gradient colors and smooth animations.

Provides visually appealing progress indicators with state-based colors.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Literal
from .theme import T
from .animations import ProgressAnimation, AnimationEngine


ProgressState = Literal['normal', 'success', 'warning', 'error']


class GradientProgressBar(tk.Canvas):
    """Progress bar with gradient fill and smooth animations."""

    STATE_COLORS = {
        'normal': T.ACCENT,
        'success': T.SUCCESS,
        'warning': T.WARNING,
        'error': T.ERROR
    }

    def __init__(self, parent, width: int = 300, height: int = 8, **kwargs):
        bg_color = kwargs.pop('bg', T.BG_LIGHT)
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )

        self.bar_width = width
        self.bar_height = height
        self.progress_value = 0.0
        self.state = 'normal'

        self._draw_background()
        self._draw_progress()

    def _draw_background(self):
        """Draw progress bar background."""
        # Background track
        self.create_rectangle(
            0, 0,
            self.bar_width, self.bar_height,
            fill=T.BORDER,
            outline='',
            tags='background'
        )

    def _draw_progress(self):
        """Draw progress fill."""
        self.delete('progress')

        if self.progress_value > 0:
            fill_width = int(self.bar_width * self.progress_value)
            color = self.STATE_COLORS.get(self.state, T.ACCENT)

            self.create_rectangle(
                0, 0,
                fill_width, self.bar_height,
                fill=color,
                outline='',
                tags='progress'
            )

    def set_progress(self, value: float, animate: bool = True):
        """Set progress value (0.0 to 1.0)."""
        value = max(0.0, min(1.0, value))

        if animate:
            # Smooth animation
            self._animate_to(value)
        else:
            self.progress_value = value
            self._draw_progress()

    def _animate_to(self, target_value: float):
        """Animate progress to target value."""
        start_value = self.progress_value
        steps = 20
        step_duration = AnimationEngine.DURATION_NORMAL // steps

        def step(current_step: int):
            if current_step <= steps:
                progress = current_step / steps
                # Ease out cubic
                eased = 1 - pow(1 - progress, 3)
                self.progress_value = start_value + (target_value - start_value) * eased
                self._draw_progress()
                self.after(step_duration, lambda: step(current_step + 1))

        step(0)

    def set_state(self, state: ProgressState):
        """Set progress bar state (changes color)."""
        self.state = state
        self._draw_progress()

    def reset(self):
        """Reset progress to 0."""
        self.set_progress(0.0, animate=False)
        self.set_state('normal')


class EnhancedProgressBar(tk.Frame):
    """Progress bar with label and percentage display."""

    def __init__(self, parent, label: str = "", width: int = 300, **kwargs):
        bg_color = kwargs.pop('bg', T.BG_LIGHT)
        super().__init__(parent, bg=bg_color)

        self.label_text = label

        # Label
        if label:
            self.label = tk.Label(
                self,
                text=label,
                font=T.FONT_SMALL,
                fg=T.TEXT_SECONDARY,
                bg=bg_color
            )
            self.label.pack(anchor=tk.W, pady=(0, T.SPACE_XS))

        # Progress bar container
        bar_container = tk.Frame(self, bg=bg_color)
        bar_container.pack(fill=tk.X)

        # Progress bar
        self.progress_bar = GradientProgressBar(
            bar_container,
            width=width,
            height=8,
            bg=bg_color
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Percentage label
        self.percentage_var = tk.StringVar(value="0%")
        self.percentage_label = tk.Label(
            bar_container,
            textvariable=self.percentage_var,
            font=T.FONT_SMALL,
            fg=T.TEXT_SECONDARY,
            bg=bg_color,
            width=5
        )
        self.percentage_label.pack(side=tk.LEFT, padx=(T.SPACE_SM, 0))

    def set_progress(self, value: float, animate: bool = True):
        """Set progress value (0.0 to 1.0)."""
        self.progress_bar.set_progress(value, animate)
        self.percentage_var.set(f"{value * 100:.0f}%")

    def set_state(self, state: ProgressState):
        """Set progress bar state."""
        self.progress_bar.set_state(state)

    def reset(self):
        """Reset progress."""
        self.progress_bar.reset()
        self.percentage_var.set("0%")

    def update_label(self, label: str):
        """Update label text."""
        if hasattr(self, 'label'):
            self.label.configure(text=label)


class CircularProgress(tk.Canvas):
    """Circular progress indicator."""

    def __init__(self, parent, size: int = 64, **kwargs):
        bg_color = kwargs.pop('bg', T.BG_LIGHT)
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )

        self.size = size
        self.progress_value = 0.0
        self.color = T.ACCENT

        self._draw_progress()

    def _draw_progress(self):
        """Draw circular progress."""
        self.delete('all')

        margin = 4
        line_width = 4

        # Background circle
        self.create_arc(
            margin, margin,
            self.size - margin, self.size - margin,
            start=90,
            extent=360,
            outline=T.BORDER,
            width=line_width,
            style=tk.ARC
        )

        # Progress arc
        if self.progress_value > 0:
            extent = -360 * self.progress_value
            self.create_arc(
                margin, margin,
                self.size - margin, self.size - margin,
                start=90,
                extent=extent,
                outline=self.color,
                width=line_width,
                style=tk.ARC
            )

        # Percentage text
        percentage = int(self.progress_value * 100)
        self.create_text(
            self.size / 2, self.size / 2,
            text=f"{percentage}%",
            font=T.FONT_BODY_SEMIBOLD,
            fill=T.TEXT_PRIMARY
        )

    def set_progress(self, value: float):
        """Set progress value (0.0 to 1.0)."""
        self.progress_value = max(0.0, min(1.0, value))
        self._draw_progress()

    def set_color(self, color: str):
        """Set progress color."""
        self.color = color
        self._draw_progress()
