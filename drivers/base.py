#LightCraft Driver Interface
#Made by Akash Samanta

"""Shared driver contract for every LED strip LightCraft can talk to.

Drivers are pure packet builders. They never touch BLE and never touch the
event loop, so they can be exercised offline. Each command returns an Effect:

    Packets   - write these once, in order, and stop
    Sequence  - replay these frames until something else is played

A driver whose hardware has a native pulse/flash opcode returns Packets for it
(see qhm.py). A driver whose hardware has no such opcode builds the effect out
of ordinary colour/brightness packets and returns a Sequence (see govee.py).
The GUI plays whatever comes back and never branches on the driver.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Packets:
    """Packets written back to back, then nothing further."""
    frames: list = field(default_factory=list)


@dataclass
class Sequence:
    """Frames replayed until cancelled. Each entry is (packet, delay_after)."""
    frames: list = field(default_factory=list)
    loop: bool = True


#Interval is the raw byte the app already works in: 0 is fastest, 10 is slowest.
FLASH_FAST = 0.08
FLASH_SLOW = 1.20
MIN_FRAME = 0.08


def flash_delay(interval):
    """How long one half of a flash cycle lasts, in seconds."""
    interval = max(0, min(10, int(interval)))
    return FLASH_FAST + (FLASH_SLOW - FLASH_FAST) * interval / 10


def pulse_period(interval):
    """How long one fade in (or out) lasts, in seconds."""
    return flash_delay(interval) * 2.5


#Colours behind each pulse/flash mode, for drivers that have to emulate them.
#These mirror the QHM's built-in modes rather than the app's colour swatches.
PALETTES = {
    'red': [(255, 0, 0)],
    'green': [(0, 255, 0)],
    'blue': [(0, 0, 255)],
    'white': [(255, 255, 255)],
    'yellow': [(255, 255, 0)],
    'cyan': [(0, 255, 255)],
    'purple': [(128, 0, 128)],
    'rg': [(255, 0, 0), (0, 255, 0)],
    'rb': [(255, 0, 0), (0, 0, 255)],
    'gb': [(0, 255, 0), (0, 0, 255)],
    'rgb': [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    'all': [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0),
            (0, 255, 255), (0, 0, 255), (128, 0, 255)],
    'eyesore': [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)],
}


def palette(colour_key):
    """Colours for a mode key such as 'all' or 'rb', falling back to white."""
    return PALETTES.get(colour_key, PALETTES['white'])


def sequence_from(effects, delay, loop=True):
    """Chain Packets effects into a Sequence, holding each one for `delay`.

    Only the last packet of each effect carries the delay - the rest are part
    of the same visual state and go out back to back.
    """
    frames = []
    for effect in effects:
        last = len(effect.frames) - 1
        for i, packet in enumerate(effect.frames):
            frames.append((packet, delay if i == last else 0.0))
    return Sequence(frames, loop=loop)


def hex_to_rgb(value):
    """'#RRGGBB' or 'RRGGBB' to an (r, g, b) tuple."""
    value = value.lstrip('#')
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


class LEDDriver(ABC):
    name = ""                 #Key stored in Settings.txt
    display_name = ""         #Label shown in the Settings tab
    default_char_uuid = ""    #Characteristic this strip listens on
    default_address = ""      #Prefilled on reset. Blank means the app supplies it
    write_with_response = True
    keepalive = None          #(packet, period_seconds) or None

    def __init__(self, opcodes=None):
        self.opcodes = opcodes or {}

    @abstractmethod
    def power(self, on):
        """Turn the strip on or off."""

    @abstractmethod
    def rgb(self, r, g, b):
        """Set a solid colour."""

    @abstractmethod
    def pulse(self, colour_key, interval):
        """Fade the strip in and out. `colour_key` indexes PALETTES."""

    @abstractmethod
    def flash(self, colour_key, interval):
        """Blink the strip hard on and off. `colour_key` indexes PALETTES."""

    def hex(self, value):
        """Set a solid colour from '#RRGGBB'."""
        return self.rgb(*hex_to_rgb(value))
