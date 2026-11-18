"""Verified PC/GEOS 2.x simple-bitmap scanline layout helpers (Alpha102).

The decoder splits per-scanline mask bytes from pixel bytes and expands
1-bit/4-bit/8-bit pixel indices. It deliberately does not assign RGB colors.
"""
from __future__ import annotations

from dataclasses import dataclass

from geoviewplus_gstring_bitmap import BitmapHeader, GStringBitmapError

BMF_MONO = 0
BMF_4BIT = 1
BMF_8BIT = 2
BMF_24BIT = 3


@dataclass(frozen=True)
class BitmapRaster:
    width: int
    height: int
    format_code: int
    pixel_rows: tuple[tuple[int, ...], ...]
    opacity_rows: tuple[tuple[bool, ...], ...] | None
    image_bytes_per_row: int
    mask_bytes_per_row: int


def decode_simple_bitmap_raster(header: BitmapHeader, data: bytes) -> BitmapRaster:
    """Split row-wise mask then image data; expand 1/4/8-bit pixel values."""
    if header.is_complex:
        raise GStringBitmapError("Alpha102 unterstützt nur einfache Bitmaps")
    if header.width <= 0 or header.height <= 0:
        raise GStringBitmapError("Ungültige Bitmap-Abmessungen")
    fmt = header.format_code
    if fmt not in (BMF_MONO, BMF_4BIT, BMF_8BIT):
        raise GStringBitmapError(f"Nicht unterstütztes Bitmapformat {fmt}")

    image_bpr = {
        BMF_MONO: (header.width + 7) // 8,
        BMF_4BIT: (header.width + 1) // 2,
        BMF_8BIT: header.width,
    }[fmt]
    mask_bpr = (header.width + 7) // 8 if header.has_mask else 0
    expected = (image_bpr + mask_bpr) * header.height
    if len(data) != expected:
        raise GStringBitmapError(
            f"Bitmap-Raster hat {len(data)} statt {expected} Bytes"
        )

    pixels: list[tuple[int, ...]] = []
    opacity: list[tuple[bool, ...]] = []
    pos = 0
    for _y in range(header.height):
        # GEOS source: mask plane precedes image plane on each scanline.
        mask = data[pos:pos + mask_bpr]
        pos += mask_bpr
        row_data = data[pos:pos + image_bpr]
        pos += image_bpr

        if fmt == BMF_MONO:
            row = tuple((row_data[x // 8] >> (7 - (x % 8))) & 1
                        for x in range(header.width))
        elif fmt == BMF_4BIT:
            # GEOS source reads the high nibble for the first pixel.
            row = tuple(((row_data[x // 2] >> 4) & 0xF) if x % 2 == 0
                        else (row_data[x // 2] & 0xF)
                        for x in range(header.width))
        else:
            row = tuple(row_data[:header.width])
        pixels.append(row)

        if header.has_mask:
            # Cleared mask bit masks the pixel; set bit retains/shows it.
            opacity.append(tuple(bool((mask[x // 8] >> (7 - (x % 8))) & 1)
                                  for x in range(header.width)))

    return BitmapRaster(
        header.width, header.height, fmt, tuple(pixels),
        tuple(opacity) if header.has_mask else None,
        image_bpr, mask_bpr,
    )
