"""Hooks - State management and side effects (React-like)."""
import tkinter as tk
from typing import Any, Callable, Optional, Tuple

class State:
    """State hook - Manage component state."""
    
    def __init__(self, initial_value: Any = None):
        self._value = initial_value
        self._listeners = []
    
    def get(self) -> Any:
        """Get current state value."""
        return self._value
    
    def set(self, value: Any):
        """Set state value and notify listeners."""
        self._value = value
        for listener in self._listeners:
            listener(value)
    
    def subscribe(self, listener: Callable):
        """Subscribe to state changes."""
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

class TkState:
    """Tkinter variable wrapper for state management."""
    
    def __init__(self, var_type: str = "string", initial_value: Any = None):
        if var_type == "string":
            self.var = tk.StringVar(value=initial_value or "")
        elif var_type == "int":
            self.var = tk.IntVar(value=initial_value or 0)
        elif var_type == "bool":
            self.var = tk.BooleanVar(value=initial_value or False)
        elif var_type == "double":
            self.var = tk.DoubleVar(value=initial_value or 0.0)
        else:
            raise ValueError(f"Unknown var_type: {var_type}")
    
    def get(self) -> Any:
        return self.var.get()
    
    def set(self, value: Any):
        self.var.set(value)
    
    def trace(self, callback: Callable):
        """Trace variable changes."""
        self.var.trace_add("write", lambda *args: callback(self.get()))

class Effect:
    """Effect hook - Run side effects."""
    
    def __init__(self, effect_fn: Callable, dependencies: list = None):
        self.effect_fn = effect_fn
        self.dependencies = dependencies or []
        self.cleanup_fn = None
        self.prev_deps = None
    
    def run(self):
        """Run effect if dependencies changed."""
        if self._should_run():
            if self.cleanup_fn:
                self.cleanup_fn()
            self.cleanup_fn = self.effect_fn()
            self.prev_deps = self.dependencies.copy()
    
    def _should_run(self) -> bool:
        if self.prev_deps is None:
            return True
        return self.dependencies != self.prev_deps
    
    def cleanup(self):
        if self.cleanup_fn:
            self.cleanup_fn()

class Ref:
    """Ref hook - Hold mutable reference."""
    
    def __init__(self, initial_value: Any = None):
        self.current = initial_value

class Memo:
    """Memo hook - Memoize expensive computations."""
    
    def __init__(self, compute_fn: Callable, dependencies: list):
        self.compute_fn = compute_fn
        self.dependencies = dependencies
        self.cached_value = None
        self.prev_deps = None
    
    def get(self) -> Any:
        if self._should_recompute():
            self.cached_value = self.compute_fn()
            self.prev_deps = self.dependencies.copy()
        return self.cached_value
    
    def _should_recompute(self) -> bool:
        if self.prev_deps is None:
            return True
        return self.dependencies != self.prev_deps

class Callback:
    """Callback hook - Memoize callbacks."""
    
    def __init__(self, callback_fn: Callable, dependencies: list):
        self.callback_fn = callback_fn
        self.dependencies = dependencies
        self.cached_callback = None
        self.prev_deps = None
    
    def get(self) -> Callable:
        if self._should_recreate():
            self.cached_callback = self.callback_fn
            self.prev_deps = self.dependencies.copy()
        return self.cached_callback
    
    def _should_recreate(self) -> bool:
        if self.prev_deps is None:
            return True
        return self.dependencies != self.prev_deps

class Context:
    """Context - Share data across components."""
    
    def __init__(self, default_value: Any = None):
        self.value = default_value
        self.subscribers = []
    
    def provide(self, value: Any):
        """Provide value to context."""
        self.value = value
        for subscriber in self.subscribers:
            subscriber(value)
    
    def consume(self, callback: Callable):
        """Consume context value."""
        self.subscribers.append(callback)
        callback(self.value)
        return lambda: self.subscribers.remove(callback)

# Helper functions
def use_state(initial_value: Any = None) -> Tuple[Callable, Callable]:
    """Create state with getter and setter."""
    state = State(initial_value)
    return state.get, state.set

def use_tk_state(var_type: str = "string", initial_value: Any = None) -> TkState:
    """Create Tkinter state."""
    return TkState(var_type, initial_value)

def use_effect(effect_fn: Callable, dependencies: list = None) -> Effect:
    """Create effect."""
    return Effect(effect_fn, dependencies)

def use_ref(initial_value: Any = None) -> Ref:
    """Create ref."""
    return Ref(initial_value)

def use_memo(compute_fn: Callable, dependencies: list) -> Callable:
    """Create memoized value."""
    memo = Memo(compute_fn, dependencies)
    return memo.get

def use_callback(callback_fn: Callable, dependencies: list) -> Callable:
    """Create memoized callback."""
    callback = Callback(callback_fn, dependencies)
    return callback.get

def use_context(context: Context) -> Any:
    """Consume context."""
    return context.value
