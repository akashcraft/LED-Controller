#LightCraft Drivers
#Made by Akash Samanta

from .base import (LEDDriver, Packets, Sequence, PALETTES, flash_delay,
                   hex_to_rgb, palette, pulse_period, sequence_from)
from .qhm import QHMDriver
from .govee import GoveeDriver

DRIVERS = {driver.name: driver for driver in (QHMDriver, GoveeDriver)}
DEFAULT_DRIVER = QHMDriver.name


def create_driver(name, opcodes=None):
    """Build a driver by its Settings.txt key, falling back to the default."""
    return DRIVERS.get(name, DRIVERS[DEFAULT_DRIVER])(opcodes)


def display_names():
    """Labels for the Settings tab dropdown, in registration order."""
    return [driver.display_name for driver in DRIVERS.values()]


def name_for_display(label):
    """Turn a dropdown label back into the key stored in Settings.txt."""
    for key, driver in DRIVERS.items():
        if driver.display_name == label:
            return key
    return DEFAULT_DRIVER


def display_for_name(name):
    """Turn a stored key into its dropdown label."""
    return DRIVERS.get(name, DRIVERS[DEFAULT_DRIVER]).display_name
