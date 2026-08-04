#LightCraft QHM Driver
#Made by Akash Samanta

"""The original QHM-0A9E / generic BLE strip.

Every packet is built from the operation codes in Settings.txt, so the custom
operation code editor keeps working exactly as it did before the refactor.
This hardware has native pulse and flash opcodes, so both return Packets.
"""

from .base import LEDDriver, Packets


class QHMDriver(LEDDriver):
    name = "qhm"
    display_name = "QHM / Generic BLE"
    default_char_uuid = "FFD9"
    write_with_response = True
    keepalive = None

    def power(self, on):
        trailing, main, leading = self.opcodes["on" if on else "off"]
        return Packets([bytearray([trailing, main, leading])])

    def rgb(self, r, g, b):
        trailing, order, leading = self.opcodes["single"]
        channels = {'r': r, 'g': g, 'b': b}
        ordered = [channels[c.lower()] for c in order]
        return Packets([bytearray(trailing + ordered + leading)])

    def pulse(self, colour_key, interval):
        return self._mode("pulse", colour_key, interval)

    def flash(self, colour_key, interval):
        return self._mode("flash", colour_key, interval)

    def _mode(self, kind, colour_key, interval):
        trailing, codes, leading = self.opcodes[kind]
        code = codes.get(f"{colour_key}_{kind}")
        if code is None:
            return None
        return Packets([bytearray([trailing, code, int(interval), leading])])
