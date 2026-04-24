"""Toast notification widget for Tkinter.

Provides non-blocking, auto-dismissing notifications with different severity levels.
"""

import tkinter as tk
from tkinter import ttk
from typing import Literal, Optional
from .theme import T
from .animations import AnimationEngine, FadeAnimation


ToastType = Literal['info', 'success', 'warning', 'error']


class ToastNotification(tk.Toplevel):
    """A toast notification that appears at the top of the window."""

    # Toast colors based on type
    COLORS = {
        'info': '#0071e3',
        'success': '#34c759',
        'warning': '#ff9500',
        'error': '#ff3b30'
    }

    def __init__(self, parent: tk.Widget, message: str, toast_type: ToastType = 'info', duration: int = 3000):
        super().__init__(parent)

        self.message = message
        self.toast_type = toast_type
        self.duration = duration

        # Configure window
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)  # Always on top

        # Make transparent background (Windows)
        try:
            self.attributes('-transparentcolor', 'white')
        except:
            pass

        self._build_ui()
        self._position_toast()
        self._show_toast()

    def _build_ui(self):
        """Build the toast UI."""
        # Main container with rounded corners effect
        container = tk.Frame(
            self,
            bg=self.COLORS[self.toast_type],
            padx=T.SPACE_MD,
            pady=T.SPACE_SM
        )
        container.pack(fill=tk.BOTH, expand=True)

        # Message label
        label = tk.Label(
            container,
            text=self.message,
            font=T.FONT_BODY_SEMIBOLD,
            fg=T.TEXT_ON_DARK,
            bg=self.COLORS[self.toast_type],
            wraplength=400
        )
        label.pack()

        # Update to get actual size
        self.update_idletasks()

    def _position_toast(self):
        """Position toast at top center of parent window."""
        # Get parent window position and size
        parent = self.master
        parent.update_idletasks()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()

        # Get toast size
        toast_width = self.winfo_reqwidth()
        toast_height = self.winfo_reqheight()

        # Calculate position (top center)
        x = parent_x + (parent_width - toast_width) // 2
        y = parent_y + T.SPACE_LG

        self.geometry(f'+{x}+{y}')

    def _show_toast(self):
        """Show toast with fade-in animation and auto-dismiss."""
        # Fade in
        fade_in = FadeAnimation(self, duration=AnimationEngine.DURATION_FAST)

        # Schedule fade out and destroy
        self.after(self.duration, self._dismiss_toast)

    def _dismiss_toast(self):
        """Dismiss toast with fade-out animation."""
        fade_out = FadeAnimation(self, duration=AnimationEngine.DURATION_FAST)
        fade_out.fade_out(callback=self.destroy)


class ToastManager:
    """Manages multiple toast notifications to prevent overlap."""

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.active_toasts = []
        self.toast_spacing = T.SPACE_SM

    def show(self, message: str, toast_type: ToastType = 'info', duration: int = 3000):
        """Show a toast notification."""
        toast = ToastNotification(self.parent, message, toast_type, duration)
        self.active_toasts.append(toast)

        # Reposition all toasts
        self._reposition_toasts()

        # Remove from list when destroyed
        toast.bind('<Destroy>', lambda e: self._on_toast_destroyed(toast))

    def _reposition_toasts(self):
        """Reposition all active toasts to stack vertically."""
        parent = self.parent
        parent.update_idletasks()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()

        current_y = parent_y + T.SPACE_LG

        for toast in self.active_toasts:
            if toast.winfo_exists():
                toast.update_idletasks()
                toast_width = toast.winfo_reqwidth()
                toast_height = toast.winfo_reqheight()

                x = parent_x + (parent_width - toast_width) // 2
                toast.geometry(f'+{x}+{current_y}')

                current_y += toast_height + self.toast_spacing

    def _on_toast_destroyed(self, toast: ToastNotification):
        """Handle toast destruction."""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            self._reposition_toasts()

    def info(self, message: str, duration: int = 3000):
        """Show info toast."""
        self.show(message, 'info', duration)

    def success(self, message: str, duration: int = 3000):
        """Show success toast."""
        self.show(message, 'success', duration)

    def warning(self, message: str, duration: int = 3000):
        """Show warning toast."""
        self.show(message, 'warning', duration)

    def error(self, message: str, duration: int = 3000):
        """Show error toast."""
        self.show(message, 'error', duration)


# Convenience functions for quick toast usage
def show_toast(parent: tk.Widget, message: str, toast_type: ToastType = 'info', duration: int = 3000):
    """Show a single toast notification."""
    ToastNotification(parent, message, toast_type, duration)


def show_info(parent: tk.Widget, message: str, duration: int = 3000):
    """Show info toast."""
    show_toast(parent, message, 'info', duration)


def show_success(parent: tk.Widget, message: str, duration: int = 3000):
    """Show success toast."""
    show_toast(parent, message, 'success', duration)


def show_warning(parent: tk.Widget, message: str, duration: int = 3000):
    """Show warning toast."""
    show_toast(parent, message, 'warning', duration)


def show_error(parent: tk.Widget, message: str, duration: int = 3000):
    """Show error toast."""
    show_toast(parent, message, 'error', duration)
