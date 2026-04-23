"""Source Controller - Source tab event handlers.

Handles:
- Start processing button
- Source input changes
- Video preview
- Metadata fetching

Note: This is a thin wrapper controller. The actual implementation
delegates to functions in main.py scope to avoid complex refactoring
of state variables and closures.
"""
from typing import Dict, Any, Optional, Callable


class SourceController:
    """Source tab controller - thin wrapper pattern."""

    def __init__(self,
                 start_processing_fn: Callable,
                 run_step_fn: Callable = None):
        """Initialize source controller.

        Args:
            start_processing_fn: Function to call for monolithic processing
            run_step_fn: Function to call for step-by-step processing (optional)
        """
        self.start_processing_fn = start_processing_fn
        self.run_step_fn = run_step_fn

    def on_start_clicked(self) -> None:
        """Handle start processing button click."""
        self.start_processing_fn()

    def on_step_clicked(self, step_num: int) -> None:
        """Handle step button click.

        Args:
            step_num: Step number (1-7)
        """
        if self.run_step_fn:
            self.run_step_fn(step_num)
