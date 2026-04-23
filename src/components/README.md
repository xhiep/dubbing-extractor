# Component-Based UI Architecture

React-like component system for Tkinter applications.

## Overview

This component library provides:
- **Reusable UI components** (Button, Input, Label, etc.)
- **Layout components** (Card, Section, Row, Column, Grid)
- **State management hooks** (useState, useEffect, useRef, etc.)
- **Composable architecture** (build complex UIs from simple components)

## Directory Structure

```
src/components/
├── ui/
│   ├── __init__.py
│   └── widgets.py          # Basic UI widgets
├── layout/
│   ├── __init__.py
│   └── containers.py       # Layout containers
├── hooks/
│   ├── __init__.py
│   └── state.py            # State management
├── examples.py             # Example components
└── __init__.py
```

## Quick Start

### Basic Components

```python
import tkinter as tk
from src.components.ui import Button, Input, Label
from src.components.layout import Card, Row

root = tk.Tk()

# Create a card
card = Card(root, title="My Card")
container = card.get_container()

# Add components
label = Label(container, text="Enter name:")
label.pack()

input_field = Input(container, placeholder="Your name...")
input_field.pack(pady=5)

button = Button(container, text="Submit", command=lambda: print(input_field.get_value()))
button.pack()

card.pack(padx=10, pady=10)
root.mainloop()
```

### Layout Components

```python
from src.components.layout import Row, Column, Grid

# Horizontal layout
row = Row(parent, spacing=10)
row.add(Button(parent, text="Button 1", command=lambda: None).widget)
row.add(Button(parent, text="Button 2", command=lambda: None).widget)
row.pack()

# Vertical layout
column = Column(parent, spacing=5)
column.add(Label(parent, text="Label 1").widget)
column.add(Label(parent, text="Label 2").widget)
column.pack()

# Grid layout
grid = Grid(parent, columns=2)
grid.add(Label(parent, text="Name:").widget)
grid.add(Input(parent).widget)
grid.add(Label(parent, text="Email:").widget)
grid.add(Input(parent).widget)
grid.pack()
```

### State Management

```python
from src.components.hooks import use_tk_state, use_effect

# Create state
count_state = use_tk_state("int", 0)

# Create label bound to state
label = Label(parent, text=f"Count: {count_state.get()}")
label.pack()

# Update label when state changes
count_state.trace(lambda value: label.set_text(f"Count: {value}"))

# Button to increment
Button(
    parent,
    text="Increment",
    command=lambda: count_state.set(count_state.get() + 1)
).pack()
```

### Reusable Components

```python
from src.components.examples import VideoInputComponent, SettingsComponent, LogViewerComponent

# Video input with paste and browse
video_input = VideoInputComponent(
    parent=root,
    on_change=lambda url: print(f"URL: {url}")
)
video_input.pack(fill=tk.X, padx=10, pady=10)

# Settings with radio buttons
settings = SettingsComponent(
    parent=root,
    options={
        "quality": ["low", "medium", "high"],
        "format": ["mp4", "avi", "mkv"]
    },
    on_change=lambda key, value: print(f"{key} = {value}")
)
settings.pack(fill=tk.X, padx=10, pady=10)

# Log viewer
log_viewer = LogViewerComponent(parent=root)
log_viewer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
log_viewer.append("Processing started...\n")
```

## Component API

### UI Components

#### Button
```python
Button(parent, text, command, bg="#4CAF50", fg="white", width=20, height=2)
```

#### Input
```python
input = Input(parent, placeholder="Enter text...", width=50)
value = input.get_value()
input.set_value("new value")
```

#### Label
```python
label = Label(parent, text="Hello", font=("Arial", 12))
label.set_text("New text")
```

#### TextArea
```python
text_area = TextArea(parent, width=80, height=20)
text_area.append("New line\n")
text_area.clear()
```

#### Checkbox
```python
checkbox = Checkbox(parent, text="Enable feature", default=True)
if checkbox.is_checked():
    print("Checked")
```

### Layout Components

#### Card
```python
card = Card(parent, title="My Card", bg="white", padding=10)
container = card.get_container()
# Add widgets to container
```

#### Section
```python
section = Section(parent, title="Settings")
container = section.get_container()
# Add widgets to container
```

#### Row
```python
row = Row(parent, spacing=10)
row.add(widget1)  # Fixed width
row.add(widget2, flex=1)  # Expands to fill space
```

#### Column
```python
column = Column(parent, spacing=5)
column.add(widget1)
column.add(widget2, flex=1)  # Expands to fill space
```

### Hooks

#### use_tk_state
```python
state = use_tk_state("string", "initial value")
value = state.get()
state.set("new value")
state.trace(lambda v: print(f"Changed to: {v}"))
```

#### use_effect
```python
effect = use_effect(
    lambda: print("Effect ran"),
    dependencies=[some_value]
)
effect.run()  # Run when dependencies change
```

#### use_ref
```python
ref = use_ref(initial_value)
ref.current = new_value
```

## Benefits

1. **Reusability**: Write once, use everywhere
2. **Composability**: Build complex UIs from simple components
3. **Maintainability**: Each component has single responsibility
4. **Testability**: Easy to test individual components
5. **Consistency**: Uniform look and feel
6. **Type Safety**: Clear interfaces and contracts

## Best Practices

1. **Keep components small**: < 100 lines per component
2. **Single responsibility**: Each component does one thing well
3. **Props over state**: Pass data down, events up
4. **Composition over inheritance**: Combine simple components
5. **Immutable props**: Don\'t modify props inside components

## Migration Guide

To migrate existing GUI code:

1. Identify reusable patterns
2. Extract into components
3. Replace inline code with component calls
4. Add state management where needed
5. Test each component individually

## Example: Before vs After

### Before (Inline)
```python
# 50 lines of inline Tkinter code
frame = tk.Frame(root)
label = tk.Label(frame, text="URL:")
label.pack()
entry = tk.Entry(frame, width=50)
entry.pack()
btn = tk.Button(frame, text="Submit", command=submit)
btn.pack()
frame.pack()
```

### After (Component-based)
```python
# 3 lines using components
video_input = VideoInputComponent(root, on_change=handle_url_change)
video_input.pack()
```

## Next Steps

1. Create more domain-specific components
2. Add theming support
3. Add animation/transition support
4. Create component library documentation
5. Add unit tests for components

---

**Created**: 2026-04-22
**Architecture**: Component-based (React-like)
**Framework**: Tkinter
