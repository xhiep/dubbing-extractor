"""Animation helpers for Tkinter.

Provides smooth transitions and effects using Tkinter's after() scheduling.
Designed to maintain 60fps performance without blocking the main thread.
"""

import tkinter as tk
from typing import Callable, Optional
import math


class AnimationEngine:
    """Manages animation scheduling and easing functions."""

    # Standard animation durations (ms)
    DURATION_FAST = 150
    DURATION_NORMAL = 250
    DURATION_SLOW = 400

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out: fast start, slow end."""
        return 1 - pow(1 - t, 3)

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out: smooth acceleration and deceleration."""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def ease_out_expo(t: float) -> float:
        """Exponential ease-out: very fast start, gradual slow."""
        return 1 if t == 1 else 1 - pow(2, -10 * t)

    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation (no easing)."""
        return t


class FadeAnimation:
    """Fade in/out animation for widgets."""

    def __init__(self, widget: tk.Widget, duration: int = AnimationEngine.DURATION_NORMAL):
        self.widget = widget
        self.duration = duration
        self.start_time = None
        self.animation_id = None

    def fade_in(self, callback: Optional[Callable] = None):
        """Fade widget from transparent to opaque."""
        self.start_time = self.widget.tk.call('clock', 'milliseconds')
        self._animate_fade(0.0, 1.0, callback)

    def fade_out(self, callback: Optional[Callable] = None):
        """Fade widget from opaque to transparent."""
        self.start_time = self.widget.tk.call('clock', 'milliseconds')
        self._animate_fade(1.0, 0.0, callback)

    def _animate_fade(self, start_alpha: float, end_alpha: float, callback: Optional[Callable]):
        """Internal fade animation loop."""
        current_time = self.widget.tk.call('clock', 'milliseconds')
        elapsed = current_time - self.start_time
        progress = min(elapsed / self.duration, 1.0)

        # Apply easing
        eased = AnimationEngine.ease_out_cubic(progress)
        alpha = start_alpha + (end_alpha - start_alpha) * eased

        # Update widget opacity (simulate with state)
        try:
            if alpha <= 0.01:
                self.widget.state(['disabled'])
            else:
                self.widget.state(['!disabled'])
        except:
            pass  # Widget doesn't support state

        if progress < 1.0:
            self.animation_id = self.widget.after(16, lambda: self._animate_fade(start_alpha, end_alpha, callback))
        else:
            if callback:
                callback()


class SlideAnimation:
    """Slide animation for widgets."""

    def __init__(self, widget: tk.Widget, duration: int = AnimationEngine.DURATION_NORMAL):
        self.widget = widget
        self.duration = duration
        self.start_time = None
        self.animation_id = None

    def slide_in(self, direction: str = 'left', callback: Optional[Callable] = None):
        """Slide widget in from specified direction."""
        self.start_time = self.widget.tk.call('clock', 'milliseconds')
        self._animate_slide(direction, True, callback)

    def slide_out(self, direction: str = 'left', callback: Optional[Callable] = None):
        """Slide widget out to specified direction."""
        self.start_time = self.widget.tk.call('clock', 'milliseconds')
        self._animate_slide(direction, False, callback)

    def _animate_slide(self, direction: str, slide_in: bool, callback: Optional[Callable]):
        """Internal slide animation loop."""
        current_time = self.widget.tk.call('clock', 'milliseconds')
        elapsed = current_time - self.start_time
        progress = min(elapsed / self.duration, 1.0)

        eased = AnimationEngine.ease_out_expo(progress)

        # Calculate offset based on direction
        if not slide_in:
            eased = 1.0 - eased

        # Note: Actual position changes would require place() geometry manager
        # This is a simplified version

        if progress < 1.0:
            self.animation_id = self.widget.after(16, lambda: self._animate_slide(direction, slide_in, callback))
        else:
            if callback:
                callback()


class ProgressAnimation:
    """Smooth progress bar animation."""

    def __init__(self, progress_var: tk.DoubleVar, duration: int = AnimationEngine.DURATION_NORMAL):
        self.progress_var = progress_var
        self.duration = duration
        self.start_time = None
        self.animation_id = None
        self.widget = None

    def animate_to(self, target_value: float, widget: tk.Widget, callback: Optional[Callable] = None):
        """Animate progress from current value to target."""
        self.widget = widget
        self.start_value = self.progress_var.get()
        self.target_value = target_value
        self.start_time = widget.tk.call('clock', 'milliseconds')
        self._animate_progress(callback)

    def _animate_progress(self, callback: Optional[Callable]):
        """Internal progress animation loop."""
        if not self.widget:
            return

        current_time = self.widget.tk.call('clock', 'milliseconds')
        elapsed = current_time - self.start_time
        progress = min(elapsed / self.duration, 1.0)

        eased = AnimationEngine.ease_out_cubic(progress)
        current_value = self.start_value + (self.target_value - self.start_value) * eased
        self.progress_var.set(current_value)

        if progress < 1.0:
            self.animation_id = self.widget.after(16, lambda: self._animate_progress(callback))
        else:
            if callback:
                callback()


class HoverEffect:
    """Hover effect for buttons and interactive elements."""

    def __init__(self, widget, hover_bg: str, normal_bg: str):
        # Handle both tk.Widget and custom wrapper classes (like Button)
        if hasattr(widget, 'widget'):
            self.widget = widget.widget  # Custom wrapper class
        else:
            self.widget = widget  # Standard tk.Widget

        self.hover_bg = hover_bg
        self.normal_bg = normal_bg
        self.is_hovering = False

        self.widget.bind('<Enter>', self._on_enter)
        self.widget.bind('<Leave>', self._on_leave)

    def _on_enter(self, event):
        """Mouse enters widget."""
        if not self.is_hovering:
            self.is_hovering = True
            try:
                self.widget.configure(background=self.hover_bg)
            except:
                pass

    def _on_leave(self, event):
        """Mouse leaves widget."""
        if self.is_hovering:
            self.is_hovering = False
            try:
                self.widget.configure(background=self.normal_bg)
            except:
                pass


class PulseAnimation:
    """Pulse animation for loading indicators."""

    def __init__(self, widget: tk.Widget, duration: int = 1000):
        self.widget = widget
        self.duration = duration
        self.start_time = None
        self.animation_id = None
        self.running = False

    def start(self):
        """Start pulsing animation."""
        if not self.running:
            self.running = True
            self.start_time = self.widget.tk.call('clock', 'milliseconds')
            self._animate_pulse()

    def stop(self):
        """Stop pulsing animation."""
        self.running = False
        if self.animation_id:
            self.widget.after_cancel(self.animation_id)
            self.animation_id = None

    def _animate_pulse(self):
        """Internal pulse animation loop."""
        if not self.running:
            return

        current_time = self.widget.tk.call('clock', 'milliseconds')
        elapsed = (current_time - self.start_time) % self.duration
        progress = elapsed / self.duration

        # Sine wave for smooth pulse
        alpha = (math.sin(progress * 2 * math.pi) + 1) / 2

        # Apply visual effect (simplified)
        # In practice, you'd modify widget appearance here

        self.animation_id = self.widget.after(16, self._animate_pulse)


def animate_widget_fade_in(widget: tk.Widget, duration: int = AnimationEngine.DURATION_NORMAL, callback: Optional[Callable] = None):
    """Convenience function to fade in a widget."""
    anim = FadeAnimation(widget, duration)
    anim.fade_in(callback)


def animate_widget_fade_out(widget: tk.Widget, duration: int = AnimationEngine.DURATION_NORMAL, callback: Optional[Callable] = None):
    """Convenience function to fade out a widget."""
    anim = FadeAnimation(widget, duration)
    anim.fade_out(callback)
