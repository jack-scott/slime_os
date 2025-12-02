"""
MicroPython compatibility shim for simulator

Provides stub implementations of MicroPython-specific functions.
"""

def const(value):
    """
    Compatibility stub for micropython.const()

    In MicroPython, const() marks a value as a compile-time constant.
    In CPython, we just return the value as-is.
    """
    return value


def viper(func):
    """
    Compatibility stub for @micropython.viper decorator

    In MicroPython, this compiles to native code for speed.
    In CPython, we just return the function unchanged.
    """
    return func


# Type hints for viper functions - in CPython these are just ignored
# In MicroPython viper mode, these become native pointer types
class ptr8:
    """Stub for 8-bit pointer type used in viper functions"""
    pass

class ptr16:
    """Stub for 16-bit pointer type used in viper functions"""
    pass

class ptr32:
    """Stub for 32-bit pointer type used in viper functions"""
    pass


# Make everything available
__all__ = ['const', 'viper', 'ptr8', 'ptr16', 'ptr32']
