"""Demo application for new UI components.

Showcases animations, toast notifications, loading spinners, and enhanced progress bars.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.components.theme import T, DarkTheme, theme_manager
from src.components.toast import ToastManager
from src.components.loading import LoadingSpinner, LoadingDots, ProgressSpinner
from src.components.enhanced_progress import GradientProgressBar, EnhancedProgressBar, CircularProgress
from src.components.animations import HoverEffect


class ComponentDemo(tk.Tk):
    """Demo window for UI components."""

    def __init__(self):
        super().__init__()

        self.title("UI Components Demo")
        self.geometry("800x900")
        self.configure(bg=T.BG_LIGHT)

        # Toast manager
        self.toast_manager = ToastManager(self)

        # Current theme
        self.current_theme = T

        self._build_ui()

    def _build_ui(self):
        """Build demo UI."""
        # Main container with scrollbar
        main_frame = tk.Frame(self, bg=T.BG_LIGHT)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=T.SPACE_LG, pady=T.SPACE_LG)

        # Title
        title = tk.Label(
            main_frame,
            text="UI Components Demo",
            font=T.FONT_HERO,
            fg=T.TEXT_PRIMARY,
            bg=T.BG_LIGHT
        )
        title.pack(pady=(0, T.SPACE_LG))

        # Dark mode toggle
        self._build_dark_mode_section(main_frame)

        # Toast notifications section
        self._build_toast_section(main_frame)

        # Loading spinners section
        self._build_loading_section(main_frame)

        # Progress bars section
        self._build_progress_section(main_frame)

        # Animations section
        self._build_animations_section(main_frame)

    def _build_dark_mode_section(self, parent):
        """Build dark mode toggle section."""
        section = tk.Frame(parent, bg=T.BG_WHITE, padx=T.SPACE_MD, pady=T.SPACE_MD)
        section.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        label = tk.Label(
            section,
            text="Theme",
            font=T.FONT_SECTION,
            fg=T.TEXT_PRIMARY,
            bg=T.BG_WHITE
        )
        label.pack(anchor=tk.W, pady=(0, T.SPACE_SM))

        # Toggle button
        self.theme_btn = tk.Button(
            section,
            text="🌙 Switch to Dark Mode",
            font=T.FONT_BODY_SEMIBOLD,
            fg=T.TEXT_ON_DARK,
            bg=T.ACCENT,
            activebackground=T.ACCENT_HOVER,
            relief=tk.FLAT,
            padx=T.SPACE_MD,
            pady=T.SPACE_SM,
            cursor="hand2",
            command=self._toggle_theme
        )
        self.theme_btn.pack(anchor=tk.W)

        # Add hover effect
        HoverEffect(self.theme_btn, T.ACCENT_HOVER, T.ACCENT)

    def _build_toast_section(self, parent):
        """Build toast notifications demo section."""
        section = tk.Frame(parent, bg=T.BG_WHITE, padx=T.SPACE_MD, pady=T.SPACE_MD)
        section.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        label = tk.Label(
            section,
            text="Toast Notifications",
            font=T.FONT_SECTION,
            fg=T.TEXT_PRIMARY,
            bg=T.BG_WHITE
        )
        label.pack(anchor=tk.W, pady=(0, T.SPACE_SM))

        # Button container
        btn_container = tk.Frame(section, bg=T.BG_WHITE)
        btn_container.pack(fill=tk.X)

        # Toast buttons
        buttons = [
            ("Info", lambda: self.toast_manager.info("This is an info message")),
            ("Success", lambda: self.toast_manager.success("Operation completed successfully!")),
            ("Warning", lambda: self.toast_manager.warning("This is a warning message")),
            ("Error", lambda: self.toast_manager.error("An error occurred!"))
        ]

        for text, command in buttons:
            btn = tk.Button(
                btn_container,
                text=text,
                font=T.FONT_BODY,
                fg=T.TEXT_PRIMARY,
                bg=T.BG_LIGHT,
                relief=tk.FLAT,
                padx=T.SPACE_MD,
                pady=T.SPACE_SM,
                cursor="hand2",
                command=command
            )
            btn.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))

    def _build_loading_section(self, parent):
        """Build loading indicators demo section."""
        section = tk.Frame(parent, bg=T.BG_WHITE, padx=T.SPACE_MD, pady=T.SPACE_MD)
        section.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        label = tk.Label(
            section,
            text="Loading Indicators",
            font=T.FONT_SECTION,
            fg=T.TEXT_PRIMARY,
            bg=T.BG_WHITE
        )
        label.pack(anchor=tk.W, pady=(0, T.SPACE_SM))

        # Spinners container
        spinners_container = tk.Frame(section, bg=T.BG_WHITE)
        spinners_container.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        # Loading spinner
        spinner_label = tk.Label(
            spinners_container,
            text="Spinner:",
            font=T.FONT_BODY,
            fg=T.TEXT_SECONDARY,
            bg=T.BG_WHITE
        )
        spinner_label.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))

        self.spinner = LoadingSpinner(spinners_container, size=32, bg=T.BG_WHITE)
        self.spinner.pack(side=tk.LEFT, padx=(0, T.SPACE_LG))

        # Loading dots
        dots_label = tk.Label(
            spinners_container,
            text="Dots:",
            font=T.FONT_BODY,
            fg=T.TEXT_SECONDARY,
            bg=T.BG_WHITE
        )
        dots_label.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))

        self.dots = LoadingDots(spinners_container, bg=T.BG_WHITE)
        self.dots.pack(side=tk.LEFT, padx=(0, T.SPACE_LG))

        # Progress spinner
        progress_label = tk.Label(
            spinners_container,
            text="Progress:",
            font=T.FONT_BODY,
            fg=T.TEXT_SECONDARY,
            bg=T.BG_WHITE
        )
        progress_label.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))

        self.progress_spinner = ProgressSpinner(spinners_container, bg=T.BG_WHITE)
        self.progress_spinner.pack(side=tk.LEFT)

        # Control buttons
        btn_container = tk.Frame(section, bg=T.BG_WHITE)
        btn_container.pack(fill=tk.X)

        start_btn = tk.Button(
            btn_container,
            text="Start",
            font=T.FONT_BODY,
            fg=T.TEXT_ON_DARK,
            bg=T.SUCCESS,
            relief=tk.FLAT,
            padx=T.SPACE_MD,
            pady=T.SPACE_SM,
            cursor="hand2",
            command=self._start_loading
        )
        start_btn.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))

        stop_btn = tk.Button(
            btn_container,
            text="Stop",
            font=T.FONT_BODY,
            fg=T.TEXT_ON_DARK,
            bg=T.ERROR,
            relief=tk.FLAT,
            padx=T.SPACE_MD,
            pady=T.SPACE_SM,
            cursor="hand2",
            command=self._stop_loading
        )
        stop_btn.pack(side=tk.LEFT)

    def _build_progress_section(self, parent):
        """Build progress bars demo section."""
        section = tk.Frame(parent, bg=T.BG_WHITE, padx=T.SPACE_MD, pady=T.SPACE_MD)
        section.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        label = tk.Label(
            section,
            text="Progress Bars",
            font=T.FONT_SECTION,
            fg=T.TEXT_PRIMARY,
            bg=T.BG_WHITE
        )
        label.pack(anchor=tk.W, pady=(0, T.SPACE_SM))

        # Gradient progress bar
        self.gradient_progress = GradientProgressBar(section, width=500, bg=T.BG_WHITE)
        self.gradient_progress.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        # Enhanced progress bar
        self.enhanced_progress = EnhancedProgressBar(
            section,
            label="Processing...",
            width=500,
            bg=T.BG_WHITE
        )
        self.enhanced_progress.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        # Circular progress
        circular_container = tk.Frame(section, bg=T.BG_WHITE)
        circular_container.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        self.circular_progress = CircularProgress(circular_container, size=80, bg=T.BG_WHITE)
        self.circular_progress.pack(side=tk.LEFT, padx=(0, T.SPACE_LG))

        # Control slider
        slider_container = tk.Frame(section, bg=T.BG_WHITE)
        slider_container.pack(fill=tk.X)

        slider_label = tk.Label(
            slider_container,
            text="Progress:",
            font=T.FONT_BODY,
            fg=T.TEXT_SECONDARY,
            bg=T.BG_WHITE
        )
        slider_label.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))

        self.progress_var = tk.DoubleVar(value=0)
        slider = tk.Scale(
            slider_container,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self._update_progress,
            bg=T.BG_WHITE,
            highlightthickness=0
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_animations_section(self, parent):
        """Build animations demo section."""
        section = tk.Frame(parent, bg=T.BG_WHITE, padx=T.SPACE_MD, pady=T.SPACE_MD)
        section.pack(fill=tk.X, pady=(0, T.SPACE_MD))

        label = tk.Label(
            section,
            text="Hover Effects",
            font=T.FONT_SECTION,
            fg=T.TEXT_PRIMARY,
            bg=T.BG_WHITE
        )
        label.pack(anchor=tk.W, pady=(0, T.SPACE_SM))

        info = tk.Label(
            section,
            text="Hover over the buttons to see smooth color transitions",
            font=T.FONT_SMALL,
            fg=T.TEXT_SECONDARY,
            bg=T.BG_WHITE
        )
        info.pack(anchor=tk.W, pady=(0, T.SPACE_SM))

        # Hover buttons
        btn_container = tk.Frame(section, bg=T.BG_WHITE)
        btn_container.pack(fill=tk.X)

        colors = [
            ("Primary", T.ACCENT, T.ACCENT_HOVER),
            ("Success", T.SUCCESS, "#30d158"),
            ("Warning", T.WARNING, "#ffb340"),
            ("Error", T.ERROR, "#ff6961")
        ]

        for text, normal_color, hover_color in colors:
            btn = tk.Button(
                btn_container,
                text=text,
                font=T.FONT_BODY_SEMIBOLD,
                fg=T.TEXT_ON_DARK,
                bg=normal_color,
                relief=tk.FLAT,
                padx=T.SPACE_MD,
                pady=T.SPACE_SM,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=(0, T.SPACE_SM))
            HoverEffect(btn, hover_color, normal_color)

    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        theme_manager.toggle()

        if theme_manager.is_dark:
            self.toast_manager.info("Dark mode enabled (demo only - full implementation needed)")
            self.theme_btn.configure(text="☀️ Switch to Light Mode")
        else:
            self.toast_manager.info("Light mode enabled")
            self.theme_btn.configure(text="🌙 Switch to Dark Mode")

    def _start_loading(self):
        """Start all loading indicators."""
        self.spinner.start()
        self.dots.start()
        self.progress_spinner.start()
        self.toast_manager.info("Loading indicators started")

    def _stop_loading(self):
        """Stop all loading indicators."""
        self.spinner.stop()
        self.dots.stop()
        self.progress_spinner.stop()
        self.toast_manager.info("Loading indicators stopped")

    def _update_progress(self, value):
        """Update all progress bars."""
        progress = float(value) / 100.0
        self.gradient_progress.set_progress(progress)
        self.enhanced_progress.set_progress(progress)
        self.circular_progress.set_progress(progress)
        self.progress_spinner.update_progress(float(value))


if __name__ == "__main__":
    app = ComponentDemo()
    app.mainloop()
