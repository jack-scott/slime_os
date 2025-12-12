"""
Simulator Battery Driver

Returns fake battery data for simulator testing.
Simulates a slowly draining battery that charges when plugged in.
"""

import time
from .abstract import AbstractBattery


class SimBattery(AbstractBattery):
    """
    Simulator battery driver

    Returns simulated battery data for testing on desktop.
    Battery slowly drains over time and can be toggled to charging mode.
    """

    def __init__(self, initial_level=85, is_charging=False, drain_rate=0.001):
        """
        Initialize the simulator battery driver

        Args:
            initial_level: Starting battery percentage (0-100)
            is_charging: Whether battery starts in charging mode
            drain_rate: How fast battery drains per second (percentage)
        """
        self._level = float(initial_level)
        self._is_charging = is_charging
        self._drain_rate = drain_rate
        self._last_update = time.time()

    def _update_battery(self):
        """Update battery level based on time elapsed"""
        current_time = time.time()
        elapsed = current_time - self._last_update

        if self._is_charging:
            # Charge at 2x drain rate
            self._level = min(100.0, self._level + (self._drain_rate * elapsed * 2))
        else:
            # Drain battery
            self._level = max(0.0, self._level - (self._drain_rate * elapsed))

        self._last_update = current_time

    def get_battery_level(self):
        """
        Get the current battery level.

        Returns:
            int: Battery level as percentage (0-100)
        """
        self._update_battery()
        return int(self._level)

    def get_is_charging(self):
        """
        Check if the battery is currently charging.

        Returns:
            bool: True if charging, False otherwise
        """
        return self._is_charging

    def set_charging(self, charging):
        """
        Set charging state (for simulator testing).

        Args:
            charging: True to enable charging, False to disable
        """
        self._update_battery()  # Update before changing state
        self._is_charging = charging

    def set_level(self, level):
        """
        Set battery level directly (for simulator testing).

        Args:
            level: Battery percentage (0-100)
        """
        self._level = max(0.0, min(100.0, float(level)))
        self._last_update = time.time()
