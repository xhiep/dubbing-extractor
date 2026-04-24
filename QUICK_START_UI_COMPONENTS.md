# Quick Start: UI Components

Fast reference for using the new UI components in your code.

## 1. Toast Notifications

```python
from src.components.toast import ToastManager

# Initialize once in your app
toast = ToastManager(root_window)

# Show notifications
toast.info("Processing started...")
toast.success("File saved successfully!")
toast.warning("Low disk space")
toast.error("Failed to load file")

# Custom duration (default 3000ms)
toast.success("Done!", duration=5000)
```

## 2. Loading Spinners

```python
from src.components.loading import LoadingSpinner, LoadingDots

# Rotating spinner
spinner = LoadingSpinner(parent, size=32, color=T.ACCENT)
spinner.pack()
spinner.start()  # Start animation
spinner.stop()   # Stop animation

# Animated dots
dots = LoadingDots(parent)
dots.pack()
dots.start()
dots.stop()
```

## 3. Progress Bars

```python
from src.components.enhanced_progress import EnhancedProgressBar

# Create progress bar
progress = EnhancedProgressBar(
    parent,
    label="Downloading...",
    width=400
)
progress.pack()

# Update progress (0.0 to 1.0)
progress.set_progress(0.5, animate=True)  # 50%

# Change state/color
progress.set_state('success')  # green
progress.set_state('warning')  # orange
progress.set_state('error')    # red
progress.set_state('normal')   # blue

# Reset
progress.reset()
```

## 4. Hover Effects

```python
from src.components.animations import HoverEffect

button = tk.Button(parent, text="Click Me", bg=T.ACCENT)
button.pack()

# Add hover effect
HoverEffect(button, hover_bg=T.ACCENT_HOVER, normal_bg=T.ACCENT)
```

## 5. Theme Colors

```python
from src.components.theme import T

# State colors
success_btn.configure(bg=T.SUCCESS)  # Green
warning_btn.configure(bg=T.WARNING)  # Orange
error_btn.configure(bg=T.ERROR)      # Red
info_btn.configure(bg=T.INFO)        # Blue

# Dark mode (basic support)
from src.components.theme import theme_manager

theme_manager.toggle()
if theme_manager.is_dark:
    # Use DarkTheme colors
    frame.configure(bg=theme_manager.current.BG_LIGHT)
```

## 6. Circular Progress

```python
from src.components.enhanced_progress import CircularProgress

circular = CircularProgress(parent, size=80)
circular.pack()

# Update progress
circular.set_progress(0.75)  # 75%

# Change color
circular.set_color(T.SUCCESS)
```

## 7. Loading Overlay

```python
from src.components.loading import show_loading_overlay

# Show full-screen loading
overlay = show_loading_overlay(parent, "Processing files...")

# Hide when done
overlay.hide()
```

## Common Patterns

### Show progress during long operation

```python
def process_files(self):
    # Show loading
    self.progress.set_progress(0)
    
    total = len(files)
    for i, file in enumerate(files):
        # Process file
        process(file)
        
        # Update progress
        progress_value = (i + 1) / total
        self.progress.set_progress(progress_value)
    
    # Show success
    self.progress.set_state('success')
    self.toast.success("All files processed!")
```

### Loading with spinner

```python
def load_data(self):
    self.spinner.start()
    
    try:
        data = fetch_data()
        self.toast.success("Data loaded")
    except Exception as e:
        self.toast.error(f"Error: {e}")
    finally:
        self.spinner.stop()
```

### Animated button

```python
# Create button with hover effect
btn = tk.Button(
    parent,
    text="Submit",
    font=T.FONT_BODY_SEMIBOLD,
    fg=T.TEXT_ON_DARK,
    bg=T.ACCENT,
    relief=tk.FLAT,
    padx=T.SPACE_MD,
    pady=T.SPACE_SM,
    cursor="hand2",
    command=self.on_submit
)
btn.pack()

# Add hover animation
HoverEffect(btn, T.ACCENT_HOVER, T.ACCENT)
```

## Demo

Run the demo to see all components in action:

```bash
python demo_ui_components.py
```

## Import Summary

```python
# Notifications
from src.components.toast import ToastManager

# Loading
from src.components.loading import (
    LoadingSpinner,
    LoadingDots,
    ProgressSpinner,
    show_loading_overlay
)

# Progress
from src.components.enhanced_progress import (
    GradientProgressBar,
    EnhancedProgressBar,
    CircularProgress
)

# Animations
from src.components.animations import (
    HoverEffect,
    FadeAnimation,
    AnimationEngine
)

# Theme
from src.components.theme import T, theme_manager
```
