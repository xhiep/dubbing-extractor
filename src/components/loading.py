"""Loading spinner widget for Tkinter.

Provides animated loading indicators with smooth rotation.
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Optional
from .theme import T
from .animations import AnimationEngine


class LoadingSpinner(tk.Canvas):
    """Animated loading spinner widget."""

    def __init__(self, parent, size: int = 32, color: str = T.ACCENT, **kwargs):
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
        self.color = color
        self.rotation = 0
        self.animation_id = None
        self.running = False

        self._draw_spinner()

    def _draw_spinner(self):
        """Draw the spinner arc."""
        self.delete('all')

        # Draw circular arc
        margin = 4
        self.create_arc(
            margin, margin,
            self.size - margin, self.size - margin,
            start=self.rotation,
            extent=270,
            outline=self.color,
            width=3,
            style=tk.ARC
        )

    def start(self):
        """Start spinning animation."""
        if not self.running:
            self.running = True
            self._animate()

    def stop(self):
        """Stop spinning animation."""
        self.running = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None

    def _animate(self):
        """Animation loop."""
        if not self.running:
            return

        self.rotation = (self.rotation + 10) % 360
        self._draw_spinner()

        self.animation_id = self.after(16, self._animate)  # ~60fps


class LoadingDots(tk.Frame):
    """Animated loading dots indicator."""

    def __init__(self, parent, color: str = T.ACCENT, **kwargs):
        bg_color = kwargs.pop('bg', T.BG_LIGHT)
        super().__init__(parent, bg=bg_color)

        self.color = color
        self.dots = []
        self.animation_id = None
        self.running = False
        self.phase = 0

        # Create 3 dots
        bg_color = self.cget('bg')
        for i in range(3):
            dot = tk.Label(
                self,
                text='●',
                font=T.FONT_BODY,
                fg=self.color,
                bg=bg_color
            )
            dot.pack(side=tk.LEFT, padx=2)
            self.dots.append(dot)

    def start(self):
        """Start dots animation."""
        if not self.running:
            self.running = True
            self._animate()

    def stop(self):
        """Stop dots animation."""
        self.running = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None

        # Reset all dots to normal
        for dot in self.dots:
            dot.configure(fg=self.color)

    def _animate(self):
        """Animation loop - fade dots in sequence."""
        if not self.running:
            return

        # Reset all dots
        for i, dot in enumerate(self.dots):
            if i == self.phase:
                dot.configure(fg=self.color)
            else:
                dot.configure(fg=T.TEXT_DISABLED)

        self.phase = (self.phase + 1) % 3
        self.animation_id = self.after(400, self._animate)


class LoadingOverlay(tk.Frame):
    """Full-screen loading overlay with spinner and message."""

    def __init__(self, parent, message: str = "Loading...", **kwargs):
        super().__init__(
            parent,
            bg='#f0f0f0',  # Light gray background instead of transparent
            **kwargs
        )

        self.message = message

        # Center container
        container = tk.Frame(self, bg=T.BG_WHITE, padx=T.SPACE_XL, pady=T.SPACE_LG,
                            relief=tk.RAISED, borderwidth=2)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Spinner
        self.spinner = LoadingSpinner(container, size=48, bg=T.BG_WHITE)
        self.spinner.pack(pady=(0, T.SPACE_MD))

        # Message
        self.label = tk.Label(
            container,
            text=message,
            font=T.FONT_BODY,
            fg=T.TEXT_PRIMARY,
            bg=T.BG_WHITE
        )
        self.label.pack()

    def show(self):
        """Show overlay and start spinner."""
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.spinner.start()
        self.lift()

    def hide(self):
        """Hide overlay and stop spinner."""
        self.spinner.stop()
        self.place_forget()

    def update_message(self, message: str):
        """Update loading message."""
        self.message = message
        self.label.configure(text=message)


class ProgressSpinner(tk.Frame):
    """Spinner with progress percentage."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=kwargs.get('bg', T.BG_LIGHT))

        # Spinner
        self.spinner = LoadingSpinner(self, size=32, bg=kwargs.get('bg', T.BG_LIGHT))
        self.spinner.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))

        # Progress label
        self.progress_var = tk.StringVar(value="0%")
        self.label = tk.Label(
            self,
            textvariable=self.progress_var,
            font=T.FONT_BODY_SEMIBOLD,
            fg=T.TEXT_PRIMARY,
            bg=kwargs.get('bg', T.BG_LIGHT)
        )
        self.label.pack(side=tk.LEFT)

    def start(self):
        """Start spinner."""
        self.spinner.start()

    def stop(self):
        """Stop spinner."""
        self.spinner.stop()

    def update_progress(self, percentage: float):
        """Update progress percentage."""
        self.progress_var.set(f"{percentage:.0f}%")


# Convenience functions
def show_loading_overlay(parent: tk.Widget, message: str = "Loading...") -> LoadingOverlay:
    """Show a loading overlay on parent widget."""
    overlay = LoadingOverlay(parent, message)
    overlay.show()
    return overlay
