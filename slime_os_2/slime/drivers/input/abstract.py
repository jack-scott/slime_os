"""
Abstract input interface for Slime OS 2

All input drivers must implement this interface.
"""


class AbstractInput:
    """
    Abstract input interface

    Defines the contract that all input drivers must implement.
    """

    def get_key(self, keycode, case_sensitive=False):
        """
        Check if a specific key is currently pressed.

        Args:
            keycode: Keycode constant (from lib.keycode)
            case_sensitive: If True, only check exact keycode. If False (default),
                          for letter keycodes, check both upper and lower variants.

        Returns:
            True if key is pressed, False otherwise
        """
        raise NotImplementedError("Subclasses must implement get_key()")

    def get_keys(self, keycodes, case_sensitive=False):
        """
        Check multiple keys at once.

        Args:
            keycodes: List of keycode constants
            case_sensitive: If True, only check exact keycodes. If False (default),
                          for letter keycodes, check both upper and lower variants.

        Returns:
            Dict mapping each keycode to True/False
        """
        raise NotImplementedError("Subclasses must implement get_keys()")
