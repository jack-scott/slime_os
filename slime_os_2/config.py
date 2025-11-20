"""
Slime OS 2 Configuration

This is the only file you need to edit to configure your device.
"""

# Device Selection
# Available devices: "pico_calc", "simulator"
DEVICE = "simulator"  # Use "simulator" for desktop, "pico_calc" for hardware

# Watchdog Timer (optional)
# Set to None to disable (development mode)
# Set to number of seconds for timeout (production mode)
# If an app hangs/crashes, system will reset after this timeout
WATCHDOG_TIMEOUT = None  # Disabled by default
# WATCHDOG_TIMEOUT = 10  # Enable in production (10 second timeout)

# Display Configuration
# Theme colors (RGB tuples)
THEME = {
    "background": (0, 0, 0),        # Black
    "foreground": (255, 255, 255),  # White
    "accent": (255, 255, 0),        # Yellow
    "error": (255, 0, 0),           # Red
    "success": (0, 255, 0),         # Green
}
