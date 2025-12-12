"""
Class for reading battery information
"""

class AbstractBattery:
    """
    Abstract battery interface

    Defines the contract that all battery drivers must implement.
    """

    def get_battery_level(self):
        """
        Get the current battery level.
        """
        raise NotImplementedError("Subclasses must implement get_battery_level()")

    def get_is_charging(self):
        """
        Check if the battery is currently charging.
        """
        raise NotImplementedError("Subclasses must implement get_is_charging()")