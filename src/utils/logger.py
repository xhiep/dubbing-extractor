"""Logging utilities."""
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

class Logger:
    """Simple logger with callback support."""
    
    def __init__(self, log_file: Optional[Path] = None, callback: Optional[Callable] = None):
        self.log_file = log_file
        self.callback = callback
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        
        # Print to console
        print(formatted)
        
        # Write to file if specified
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(formatted + "\n")
            except Exception:
                pass
        
        # Call callback if specified
        if self.callback:
            try:
                self.callback(message)
            except Exception:
                pass
    
    def info(self, message: str):
        self.log(message, "INFO")
    
    def warning(self, message: str):
        self.log(message, "WARNING")
    
    def error(self, message: str):
        self.log(message, "ERROR")
    
    def debug(self, message: str):
        self.log(message, "DEBUG")

# Default logger instance
default_logger = Logger()
