"""
Simulator Device Configuration

Virtual device for running Slime OS on desktop (Linux/Mac/Windows).
Uses pygame for display and keyboard input.
"""

from .base import BaseDevice


class SimulatorDevice(BaseDevice):
    """
    Simulator device profile

    Runs Slime OS on desktop computer using pygame.
    Perfect for rapid development and testing without hardware.
    """

    # Metadata
    name = "Simulator"
    display_width = 320
    display_height = 320

    # Capabilities
    has_keyboard = True
    has_display = True
    has_sd_card = False  # Not simulated yet

    # Simulator-specific settings
    WINDOW_SCALE = 2  # 2x scale for better visibility (640x640 window)
    WINDOW_TITLE = "Slime OS Simulator"

    def create_display(self):
        """Create simulator display driver"""
        # Lazy import - only load when needed
        from slime.drivers.display.sim_display import SimDisplay

        return SimDisplay(
            width=self.display_width,
            height=self.display_height,
            scale=self.WINDOW_SCALE,
            title=self.WINDOW_TITLE
        )

    def create_input(self):
        """Create simulator keyboard driver"""
        # Lazy import
        from slime.drivers.input.sim_keyboard import SimKeyboard

        return SimKeyboard()
