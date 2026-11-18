"""PC/GEOS 2.x VGA16 driver's default 16-color RGB palette.

Values transcribed from vga16Palette.asm in the pinned PC/GEOS source.
This is specifically the VGA16 driver's palette, not a universal palette
for every PC/GEOS video driver.
"""
from __future__ import annotations

VGA16_DEFAULT_PALETTE = (
    (0x00, 0x00, 0x00),  # 0 black
    (0x00, 0x00, 0xAA),  # 1 dark blue
    (0x00, 0xAA, 0x00),  # 2 dark green
    (0x00, 0xAA, 0xAA),  # 3 dark cyan
    (0xAA, 0x00, 0x00),  # 4 dark red
    (0xAA, 0x00, 0xAA),  # 5 dark violet
    (0xAA, 0x55, 0x00),  # 6 brown
    (0xAA, 0xAA, 0xAA),  # 7 dark grey
    (0x55, 0x55, 0x55),  # 8 light grey
    (0x55, 0x55, 0xFF),  # 9 light blue
    (0x55, 0xFF, 0x55),  # 10 light green
    (0x55, 0xFF, 0xFF),  # 11 light cyan
    (0xFF, 0x55, 0x55),  # 12 light red
    (0xFF, 0x55, 0xFF),  # 13 light violet
    (0xFF, 0xFF, 0x55),  # 14 yellow
    (0xFF, 0xFF, 0xFF),  # 15 white
)


def palette_rgb(index: int) -> tuple[int, int, int]:
    if not 0 <= index < len(VGA16_DEFAULT_PALETTE):
        raise ValueError(f"VGA16 color index outside 0..15: {index}")
    return VGA16_DEFAULT_PALETTE[index]
