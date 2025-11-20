"""
Extended gc module for simulator

Adds MicroPython-specific functions to standard Python's gc module.
"""

from gc import *  # Import everything from standard gc

# Add MicroPython-specific functions


def mem_free():
    """
    Get free memory (MicroPython function).

    In simulator, returns a fake value since Python doesn't track this.

    Returns:
        Fake free memory amount (bytes)
    """
    return 200_000  # Fake ~200KB free (similar to Pico)


def mem_alloc():
    """
    Get allocated memory (MicroPython function).

    In simulator, returns a fake value.

    Returns:
        Fake allocated memory amount (bytes)
    """
    return 64_000  # Fake ~64KB allocated
