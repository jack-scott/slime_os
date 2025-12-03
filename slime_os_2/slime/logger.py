"""
Logging system for Slime OS 2

Provides simple logging with circular buffer for recent messages.
"""

import time


class Logger:
    """
    Simple logger for OS and apps

    Stores recent log messages in a circular buffer.
    Can also print to stdout (useful for simulator).
    """

    def __init__(self, max_messages=100, print_to_stdout=False):
        """
        Initialize logger.

        Args:
            max_messages: Maximum number of messages to keep
            print_to_stdout: If True, also print messages to stdout
        """
        self.max_messages = max_messages
        self.print_to_stdout = print_to_stdout
        self.messages = []  # List of (timestamp, level, message) tuples

    def _log(self, level, message):
        """Internal log method"""
        timestamp = time.time()
        entry = (timestamp, level, str(message))

        # Add to buffer
        self.messages.append(entry)

        # Trim if too many
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

        # Print if enabled
        if self.print_to_stdout:
            print(f"[{level}] {message}")

    def debug(self, message):
        """Log debug message"""
        self._log("DEBUG", message)

    def info(self, message):
        """Log info message"""
        self._log("INFO", message)

    def warn(self, message):
        """Log warning message"""
        self._log("WARN", message)

    def error(self, message):
        """Log error message"""
        self._log("ERROR", message)

    def get_recent(self, count=50):
        """
        Get recent log messages.

        Args:
            count: Number of recent messages to return

        Returns:
            List of (timestamp, level, message) tuples
        """
        return self.messages[-count:]

    def get_all(self):
        """Get all log messages"""
        return self.messages.copy()

    def clear(self):
        """Clear all log messages"""
        self.messages.clear()

    def format_message(self, entry):
        """
        Format a log entry for display.

        Args:
            entry: Tuple of (timestamp, level, message)

        Returns:
            Formatted string
        """
        timestamp, level, message = entry
        # Simple format: [LEVEL] message
        return f"[{level}] {message}"
