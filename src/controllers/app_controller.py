"""App Controller - Application-level event handlers.

Handles:
- Config save/load (delegated to src.config)
- Window close
- Tab switching
- Cross-controller coordination

Note: Thin wrapper pattern. Most app-level functions already
exist in src.config module, so this controller is mainly a
placeholder for future app-level coordination logic.
"""
from typing import Dict, Any, Optional, Callable


class AppController:
    """Application-level controller - thin wrapper pattern."""

    def __init__(self,
                 save_config_fn: Callable = None,
                 load_config_fn: Callable = None):
        """Initialize app controller.

        Args:
            save_config_fn: Config save function
            load_config_fn: Config load function
        """
        self.save_config_fn = save_config_fn
        self.load_config_fn = load_config_fn

    def on_config_save(self, config_dict: Dict[str, Any]) -> None:
        """Handle config save request.

        Args:
            config_dict: Configuration dictionary to save
        """
        if self.save_config_fn:
            self.save_config_fn(config_dict)

    def on_config_load(self) -> Dict[str, Any]:
        """Handle config load request.

        Returns:
            Loaded configuration dictionary
        """
        if self.load_config_fn:
            return self.load_config_fn()
        return {}

    def on_window_close(self) -> None:
        """Handle window close event.

        Note: Currently no special cleanup needed.
        Future: Add cleanup logic here (release resources, etc.)
        """
        pass
