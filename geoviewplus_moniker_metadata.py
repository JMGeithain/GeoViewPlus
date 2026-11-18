"""PC/GEOS 2.x VisMoniker metadata decoding informed by IconEd source.

Only fields whose bit positions are established by the local token DB parser
and IconEd's MonikerAnalyseResult are exposed. Unknown values stay numeric.
"""
from __future__ import annotations
from dataclasses import dataclass

# Symbolic enum names are deliberately not guessed yet.
SIZE_CODES = {}
STYLE_CODES = {}
ASPECT_CODES = {}
COLOR_CODES = {}

@dataclass(frozen=True)
class MonikerMetadata:
    type_word: int
    size_code: int
    style_code: int
    aspect_ratio_code: int
    color_code: int
    is_gstring: bool
    is_moniker_list: bool
    cached_width: int | None
    cached_height: int | None

    @property
    def size_name(self) -> str:
        return SIZE_CODES.get(self.size_code, f"code {self.size_code}")
    @property
    def style_name(self) -> str:
        return STYLE_CODES.get(self.style_code, f"code {self.style_code}")
    @property
    def aspect_name(self) -> str:
        return ASPECT_CODES.get(self.aspect_ratio_code, f"code {self.aspect_ratio_code}")
    @property
    def color_name(self) -> str:
        return COLOR_CODES.get(self.color_code, f"code {self.color_code}")

def decode_moniker_metadata(type_word: int, cached_width: int | None = None,
                            cached_height: int | None = None) -> MonikerMetadata:
    if not 0 <= type_word <= 0xFFFF:
        raise ValueError("VisMonikerListEntryType muss ein WORD sein")
    if (cached_width is None) != (cached_height is None):
        raise ValueError("cached_width und cached_height müssen gemeinsam vorliegen")
    return MonikerMetadata(type_word, (type_word & 0x3000) >> 12,
        (type_word & 0x0F00) >> 8, (type_word & 0x0030) >> 4,
        type_word & 0x000F, bool(type_word & 0x0040), bool(type_word & 0x0080),
        cached_width, cached_height)

def moniker_metadata_for_resolved(resolved) -> MonikerMetadata:
    h = resolved.header
    return decode_moniker_metadata(resolved.list_entry.type_word,
        h.width if h else None, h.height if h else None)
