"""
Stub implementation of MicroPython 'machine' module

Allows hardware code to import 'machine' without errors when running in simulator.
All operations are no-ops or return safe default values.
"""


class Pin:
    """Stub Pin class"""

    IN = 0
    OUT = 1
    PULL_UP = 1
    PULL_DOWN = 2

    def __init__(self, pin_id, mode=None, pull=None, value=None):
        self.pin_id = pin_id
        self.mode = mode
        self.pull = pull
        self._value = value if value is not None else 0

    def value(self, val=None):
        if val is not None:
            self._value = val
        return self._value

    def on(self):
        self._value = 1

    def off(self):
        self._value = 0


class I2C:
    """Stub I2C class"""

    def __init__(self, id, scl=None, sda=None, freq=400000):
        self.id = id
        self.scl = scl
        self.sda = sda
        self.freq = freq

    def scan(self):
        return []

    def readfrom(self, addr, nbytes):
        return bytes(nbytes)

    def writeto(self, addr, buf):
        pass


class SPI:
    """Stub SPI class"""

    def __init__(self, id, baudrate=1000000, polarity=0, phase=0,
                 bits=8, sck=None, mosi=None, miso=None):
        self.id = id
        self.baudrate = baudrate

    def write(self, buf):
        pass

    def read(self, nbytes):
        return bytes(nbytes)


class WDT:
    """Stub Watchdog Timer"""

    def __init__(self, timeout=5000):
        self.timeout = timeout
        print(f"[Simulator] Watchdog disabled in simulator mode")

    def feed(self):
        pass  # No-op in simulator


def reset():
    """Reset the device (no-op in simulator)"""
    print("[Simulator] machine.reset() called (no-op)")


def freq(val=None):
    """Get/set CPU frequency"""
    if val is not None:
        print(f"[Simulator] machine.freq({val}) called (no-op)")
    return 133_000_000  # Fake RP2040 frequency


def unique_id():
    """Get unique device ID"""
    return b'SIMULATOR'
