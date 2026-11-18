"""PC/GEOS 2.x DESK moniker GString bitmap extraction (Alpha101)."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from geoviewplus_gstring_bitmap import DrawBitmapCP, GStringBitmapError, decode_draw_bitmap_cp

GR_FILL_BITMAP_CP = 0x4D
GR_DRAW_BITMAP_CP = 0x51

@dataclass(frozen=True)
class DeskMonikerBitmap:
    opcode: int
    opcode_name: str
    bitmap: DrawBitmapCP
    raw_sha256: str

def decode_desk_moniker_gstring(gstring: bytes) -> DeskMonikerBitmap:
    """Decode one current-position fill/draw bitmap GString plus terminator."""
    if not gstring:
        raise GStringBitmapError("Leerer Moniker-GString")
    opcode = gstring[0]
    if opcode == GR_FILL_BITMAP_CP:
        name = "GR_FILL_BITMAP_CP"
    elif opcode == GR_DRAW_BITMAP_CP:
        name = "GR_DRAW_BITMAP_CP"
    else:
        raise GStringBitmapError(f"Nicht unterstützter Moniker-Opcode 0x{opcode:02X}")
    # Both original C structures are opcode + WORD size + bitmap block.
    normalized = bytes([GR_DRAW_BITMAP_CP]) + gstring[1:]
    decoded = decode_draw_bitmap_cp(normalized)
    return DeskMonikerBitmap(opcode, name, decoded,
                             hashlib.sha256(decoded.bitmap_data).hexdigest())
