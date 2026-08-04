#LightCraft Govee Driver
#Made by Akash Samanta

"""Govee H618F and other newer-generation RGBIC strips.

Packets are 20 bytes: a header byte, a command byte, the payload, zero padding
and an XOR of the first 19 bytes. Verified against an H618F for power (0x01),
brightness (0x04) and colour (0x05 / mode 0x15).

The hardware has no pulse or flash opcode we can drive from the interval slider
- its scene IDs carry no colour or speed parameter, and on this generation they
are per-SKU codes pulled from Govee's servers rather than a fixed table. So
both effects are built here out of ordinary packets and returned as a Sequence.
Pulse ramps the brightness byte with the colour set once, which costs a single
small packet per frame instead of a full colour packet.

govee_probe.py can test whether native scene or DIY effects work on real
hardware; see the notes there before swapping either of these to Packets.
"""

from .base import (LEDDriver, Packets, Sequence, MIN_FRAME, flash_delay,
                   palette, pulse_period)

#Dimmest level a pulse fades down to. Zero reads as a gap rather than a fade.
PULSE_FLOOR = 8
PULSE_PEAK = 255


def build_packet(head, cmd, payload=b""):
    """A 20 byte Govee packet with its trailing XOR checksum."""
    packet = bytearray(20)
    packet[0] = head
    packet[1] = cmd
    packet[2:2 + len(payload)] = bytes(payload)
    checksum = 0
    for byte in packet[:19]:
        checksum ^= byte
    packet[19] = checksum
    return packet


class GoveeDriver(LEDDriver):
    name = "govee"
    display_name = "Govee RGBIC (H618F)"
    default_char_uuid = "00010203-0405-0607-0809-0a0b0c0d2b11"
    #CoreBluetooth identifier for the H618F this driver was written against.
    #Windows addresses this strip by MAC instead, so override it there.
    default_address = "3E833910-AD80-439E-9FEA-EDFEE7E2EAC8"
    write_with_response = False
    #Some Govee strips drop the link without traffic. AA 01 ... AB, every 2s.
    keepalive = (build_packet(0xAA, 0x01), 2.0)

    def power(self, on):
        return Packets([build_packet(0x33, 0x01, [0x01 if on else 0x00])])

    def rgb(self, r, g, b):
        """Colour plus brightness.

        The app's colour picker has already scaled RGB by its value slider, so
        the raw values arrive dimmed. Splitting the peak back out into the
        brightness byte keeps the hue intact at low brightness instead of
        crushing it towards black.
        """
        peak = max(r, g, b)
        if peak == 0:
            return Packets([self._brightness(0), self._colour(0, 0, 0)])
        scaled = (r * 255 // peak, g * 255 // peak, b * 255 // peak)
        return Packets([self._brightness(peak), self._colour(*scaled)])

    def pulse(self, colour_key, interval):
        period = pulse_period(interval)
        steps = max(3, min(12, int(period / MIN_FRAME)))
        delay = period / steps
        levels = [PULSE_FLOOR + (PULSE_PEAK - PULSE_FLOOR) * i // (steps - 1)
                  for i in range(steps)]
        ramp = levels + levels[-2:0:-1]

        frames = []
        for r, g, b in palette(colour_key):
            frames.append((self._colour(r, g, b), 0.0))
            for level in ramp:
                frames.append((self._brightness(level), delay))
        return Sequence(frames)

    def flash(self, colour_key, interval):
        delay = flash_delay(interval)
        frames = []
        for r, g, b in palette(colour_key):
            frames.append((self._colour(r, g, b), 0.0))
            frames.append((self._brightness(PULSE_PEAK), delay))
            frames.append((self._brightness(0), delay))
        return Sequence(frames)

    def _brightness(self, level):
        return build_packet(0x33, 0x04, [max(0, min(255, int(level)))])

    def _colour(self, r, g, b):
        #Mode 0x15 sub-command 0x01, with every segment selected.
        return build_packet(0x33, 0x05, [0x15, 0x01, r, g, b,
                                         0x00, 0x00, 0x00, 0x00,
                                         0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
