"""Conservative PC/GEOS 2.x GString bitmap extraction helpers.

Only GR_DRAW_BITMAP_CP is decoded here. The implementation preserves raw
bitmap bytes and does not claim to render palette/mask semantics.
"""
from __future__ import annotations

from dataclasses import dataclass


GR_END_GSTRING = 0x00
GR_DRAW_BITMAP_CP = 0x51
BMC_UNCOMPACTED = 0
BMC_PACKBITS = 1
BMC_LZG = 2
BMT_MASK = 0x10
BMT_COMPLEX = 0x08
BMT_FORMAT_MASK = 0x07


class GStringBitmapError(ValueError):
    """Malformed or unsupported GString bitmap payload."""


@dataclass(frozen=True)
class BitmapHeader:
    width: int
    height: int
    compact: int
    bitmap_type: int

    @property
    def format_code(self) -> int:
        return self.bitmap_type & BMT_FORMAT_MASK

    @property
    def has_mask(self) -> bool:
        return bool(self.bitmap_type & BMT_MASK)

    @property
    def is_complex(self) -> bool:
        return bool(self.bitmap_type & BMT_COMPLEX)


@dataclass(frozen=True)
class DrawBitmapCP:
    command_size: int
    header: BitmapHeader
    encoded_bitmap: bytes
    bitmap_data: bytes
    trailing_gstring: bytes
    expected_uncompressed_size: int | None


def unpack_packbits(data: bytes, expected_size: int | None = None) -> bytes:
    """Decode the PackBits byte-run format used by BMCompact=1."""
    out = bytearray()
    pos = 0
    while pos < len(data):
        control = data[pos]
        pos += 1
        if control <= 0x7F:
            count = control + 1
            if pos + count > len(data):
                raise GStringBitmapError("PackBits-Literal läuft über das Datenende")
            out.extend(data[pos:pos + count])
            pos += count
        elif control >= 0x81:
            count = 257 - control
            if pos >= len(data):
                raise GStringBitmapError("PackBits-Wiederholung ohne Folgbyte")
            out.extend([data[pos]] * count)
            pos += 1
        # 0x80 is the PackBits no-op control.
        if expected_size is not None and len(out) > expected_size:
            raise GStringBitmapError(
                f"PackBits-Ausgabe überschreitet Sollgröße ({len(out)} > {expected_size})"
            )
    if expected_size is not None and len(out) != expected_size:
        raise GStringBitmapError(
            f"PackBits-Ausgabe hat {len(out)} statt {expected_size} Bytes"
        )
    return bytes(out)


def expected_simple_bitmap_size(header: BitmapHeader) -> int | None:
    """Compute simple bitmap storage size; return None for unsupported formats."""
    if header.width <= 0 or header.height <= 0 or header.is_complex:
        return None
    bits_per_pixel = {0: 1, 1: 4, 2: 8, 3: 24}.get(header.format_code)
    if bits_per_pixel is None:
        return None
    image_row = (header.width * bits_per_pixel + 7) // 8
    mask_row = (header.width + 7) // 8 if header.has_mask else 0
    return (image_row + mask_row) * header.height


def decode_draw_bitmap_cp(gstring: bytes) -> DrawBitmapCP:
    """Decode a GString consisting of one GR_DRAW_BITMAP_CP and terminator."""
    if len(gstring) < 3:
        raise GStringBitmapError("GString zu kurz für GR_DRAW_BITMAP_CP")
    if gstring[0] != GR_DRAW_BITMAP_CP:
        raise GStringBitmapError(
            f"Erstes GString-Element 0x{gstring[0]:02X} ist nicht GR_DRAW_BITMAP_CP"
        )
    command_size = int.from_bytes(gstring[1:3], "little")
    if command_size < 6:
        raise GStringBitmapError("Bitmap-Block ist kürzer als sein 6-Byte-Header")
    end = 3 + command_size
    if end >= len(gstring):
        raise GStringBitmapError("Deklarierte Bitmapgröße reicht über das GString-Ende")
    bitmap = gstring[3:end]
    header = BitmapHeader(
        int.from_bytes(bitmap[0:2], "little"),
        int.from_bytes(bitmap[2:4], "little"),
        bitmap[4], bitmap[5],
    )
    expected = expected_simple_bitmap_size(header)
    encoded = bitmap[6:]
    if header.compact == BMC_UNCOMPACTED:
        decoded = encoded
        if expected is not None and len(decoded) != expected:
            raise GStringBitmapError(
                f"Unkomprimierte Bitmap hat {len(decoded)} statt {expected} Bytes"
            )
    elif header.compact == BMC_PACKBITS:
        decoded = unpack_packbits(encoded, expected)
    else:
        raise GStringBitmapError(
            f"Nicht unterstützte Komprimierung BMCompact={header.compact}"
        )
    trailing = gstring[end:]
    if trailing != bytes([GR_END_GSTRING]):
        raise GStringBitmapError(
            "Nach dem Bitmap-Befehl folgt nicht ausschließlich GR_END_GSTRING"
        )
    return DrawBitmapCP(command_size, header, encoded, decoded, trailing, expected)
