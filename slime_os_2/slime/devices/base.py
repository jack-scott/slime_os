"""
Base device interface for Slime OS 2

All devices must inherit from BaseDevice and implement the required methods.
"""


class BaseDevice:
    """
    Base device interface

    Defines the contract that all hardware devices must implement.
    """

    # Device metadata
    name = "Unknown Device"
    display_width = 320
    display_height = 320

    # Device capabilities
    has_keyboard = True
    has_display = True
    has_sd_card = False
    has_battery = False

    def create_display(self):
        """
        Create and return a display driver instance.

        The display driver must implement the AbstractDisplay interface.

        Returns:
            Display driver instance

        Raises:
            NotImplementedError: If device has no display
        """
        raise NotImplementedError(f"{self.name} does not implement create_display()")

    def create_input(self):
        """
        Create and return an input driver instance.

        The input driver must implement the AbstractInput interface.

        Returns:
            Input driver instance

        Raises:
            NotImplementedError: If device has no input
        """
        raise NotImplementedError(f"{self.name} does not implement create_input()")

    def create_battery(self):
        """
        Create and return a battery driver instance.

        The battery driver must implement the AbstractBattery interface.

        Returns:
            Battery driver instance

        Raises:
            NotImplementedError: If device has no battery
        """
        raise NotImplementedError(f"{self.name} does not implement create_battery()")
