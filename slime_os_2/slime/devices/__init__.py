"""
Device registry for Slime OS 2

Provides device discovery and instantiation.
"""

# Device registry - maps device names to module paths
_DEVICES = {
    "pico_calc": "slime.devices.pico_calc.PicoCalcDevice",
    "simulator": "slime.devices.simulator.SimulatorDevice",
    # "slime_deck": "slime.devices.slime_deck.SlimeDeckDevice",
}


def get_device(device_name):
    """
    Get a device instance by name.

    Args:
        device_name: Name of the device (e.g., "pico_calc")

    Returns:
        Device instance

    Raises:
        ValueError: If device name is unknown
    """
    if device_name not in _DEVICES:
        available = ", ".join(_DEVICES.keys())
        raise ValueError(
            f"Unknown device: '{device_name}'. "
            f"Available devices: {available}"
        )

    # Dynamic import - only load the device module we need
    module_path, class_name = _DEVICES[device_name].rsplit(".", 1)
    # MicroPython's __import__ doesn't accept keyword arguments
    module = __import__(module_path, None, None, [class_name])
    device_class = getattr(module, class_name)

    # Instantiate and return
    return device_class()


def list_devices():
    """
    Get list of available device names.

    Returns:
        List of device name strings
    """
    return list(_DEVICES.keys())
