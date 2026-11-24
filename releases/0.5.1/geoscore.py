"""GeoViewPlus core: GEOS file headers, VM/DB files, token databases, monikers.

Supports GeoWorks 1.x (signature C7 45 CF 53) and GEOS 2.x .. FreeGEOS
(signature C7 45 C1 53).  Read-only; never modifies files.

Structures follow the FreeGEOS sources (Tools/utils/vmInt.h,
Include/Internal/dbaseInt.def, Include/token.def, Include/Objects/visC.def,
Include/graphics.def); 1.x offsets were verified against real 1.2x files.
"""
from __future__ import annotations

import os
import struct
from dataclasses import dataclass, field

SIG_V1 = b'\xC7\x45\xCF\x53'      # GeoWorks 1.x
SIG_V2 = b'\xC7\x45\xC1\x53'      # GEOS 2.x / Ensemble / NewDeal / Breadbox / FreeGEOS

# ---------------------------------------------------------------------------
# File header
# ---------------------------------------------------------------------------

TYPES_V1 = {0: 'Programm (Geode)', 1: 'Dokument (VM-Datei)', 2: 'Daten-Datei'}
TYPES_V2 = {0: 'DOS-Datei', 1: 'Programm (Geode)', 2: 'Dokument (VM-Datei)',
            3: 'Daten-Datei', 4: 'Verzeichnis', 5: 'Verknüpfung'}

# GEOS character set -> Unicode for the upper half (PC/GEOS uses a
# Mac-Roman-like layout).  Verified: 0x8A=ä 0x9A=ö 0x9F=ü 0x86=Ü 0xA7=ß.
_GEOS_HIGH = (
    'ÄÅÇÉÑÖÜáàâäãåçéèêëíìîïñóòôöõúùûü'      # 80-9F
    '†°¢£§•¶ß®©™´¨≠ÆØ∞±≤≥¥µ∂∑∏π∫ªºΩæø'      # A0-BF
    '¿¡¬√ƒ≈∆«»… ÀÃÕŒœ–—“”‘’÷◊ÿŸ⁄€‹›ﬁﬂ'      # C0-DF
    '‡·‚„‰ÂÊÁËÈÍÎÏÌÓÔÒÚÛÙıˆ˜¯˘˙˚¸˝˛ˇ'  # E0-FF
)


def geos_text(raw: bytes) -> str:
    raw = raw.split(b'\0', 1)[0]
    return ''.join(chr(b) if b < 0x80 else _GEOS_HIGH[b - 0x80] for b in raw)


def _fmt_dt(v: int) -> str:
    """FileDateAndTime (dword): low word date, high word time (DOS bit layout)."""
    if not v:
        return ''
    date, time = v & 0xFFFF, v >> 16
    y, m, d = 1980 + (date >> 9), (date >> 5) & 15, date & 31
    hh, mm, ss = time >> 11, (time >> 5) & 63, (time & 31) * 2
    if not (1 <= m <= 12 and 1 <= d <= 31 and hh < 24 and mm < 60):
        return ''
    return f'{d:02}.{m:02}.{y} {hh:02}:{mm:02}:{ss:02}'


@dataclass
class GeosHeader:
    version: int                     # 1 or 2
    long_name: str
    type_id: int
    type_name: str
    flags: int
    release: tuple
    protocol: tuple
    token: str
    token_manuf: int
    creator: str
    creator_manuf: int
    notes: str
    notice: str
    created: str = ''
    modified: str = ''

    @property
    def release_str(self):
        return '.'.join(str(x) for x in self.release)

    @property
    def protocol_str(self):
        return '.'.join(str(x) for x in self.protocol)


def parse_header(data: bytes) -> GeosHeader | None:
    if len(data) < 0xC8:
        return None
    sig = data[:4]
    if sig == SIG_V2 and len(data) >= 0x100:
        # GeosFileHeader2 (0x100 bytes)
        ftype, flags = struct.unpack_from('<HH', data, 0x28)
        return GeosHeader(
            version=2,
            long_name=geos_text(data[0x04:0x28]),
            type_id=ftype, type_name=TYPES_V2.get(ftype, f'Typ {ftype}'),
            flags=flags,
            release=struct.unpack_from('<4H', data, 0x2C),
            protocol=struct.unpack_from('<2H', data, 0x34),
            token=data[0x38:0x3C].decode('latin-1'),
            token_manuf=struct.unpack_from('<H', data, 0x3C)[0],
            creator=data[0x3E:0x42].decode('latin-1'),
            creator_manuf=struct.unpack_from('<H', data, 0x42)[0],
            notes=geos_text(data[0x44:0xA8]),
            notice=geos_text(data[0xA8:0xC8]),
            created=_fmt_dt(struct.unpack_from('<I', data, 0xC8)[0]),
        )
    if sig == SIG_V1:
        # GeoWorks 1.x header (0xC8 bytes), offsets verified on 1.2x files
        ftype, flags = struct.unpack_from('<HH', data, 0x04)
        return GeosHeader(
            version=1,
            long_name=geos_text(data[0x20:0x44]),
            type_id=ftype, type_name=TYPES_V1.get(ftype, f'Typ {ftype}'),
            flags=flags,
            release=struct.unpack_from('<4H', data, 0x08),
            protocol=struct.unpack_from('<2H', data, 0x10),
            token=data[0x14:0x18].decode('latin-1'),
            token_manuf=struct.unpack_from('<H', data, 0x18)[0],
            creator=data[0x1A:0x1E].decode('latin-1'),
            creator_manuf=struct.unpack_from('<H', data, 0x1E)[0],
            notes=geos_text(data[0x44:0xA8]),
            notice=geos_text(data[0xA8:0xC8]),
        )
    return None


def read_header(path: str) -> GeosHeader | None:
    try:
        with open(path, 'rb') as f:
            return parse_header(f.read(0x100))
    except OSError:
        return None

# ---------------------------------------------------------------------------
# VM files and the DB layer
# ---------------------------------------------------------------------------


class VMFile:
    def __init__(self, data: bytes):
        self.d = data
        self.v2 = data[:4] == SIG_V2
        gfh = 0x100 if self.v2 else 0xC8
        sig, hsize, hpos = struct.unpack_from('<HHI', data, gfh)
        if sig != 0xADEB:
            raise ValueError('keine VM-Datei')
        # 2.x: file positions are counted after the 256-byte GEOS header
        self.base = 0x100 if self.v2 else 0
        self.h = data[self.base + hpos:self.base + hpos + hsize]
        if struct.unpack_from('<H', self.h, 0)[0] != 0xFB:
            raise ValueError('VM-Kopfblock ungültig')
        self.last_handle = struct.unpack_from('<H', self.h, 8)[0]
        self.map_block = struct.unpack_from('<H', self.h, 0x14)[0]
        # 1.x has no separate DB map field: the VM map block is the DB map
        self.db_map = struct.unpack_from('<H', self.h, 0x1E)[0] if self.v2 else self.map_block

    def info(self, hid):
        _, sig, flags, uid, size, pos = struct.unpack_from('<HBBHHI', self.h, hid)
        return sig, flags, uid, size, pos

    def handles(self):
        for hid in range(0x20, self.last_handle, 12):
            sig, flags, uid, size, pos = self.info(hid)
            if sig >= 0xFE:
                yield hid, uid

    def block(self, hid):
        if not (0x20 <= hid < self.last_handle) or (hid - 0x20) % 12:
            raise KeyError(hid)
        sig, flags, uid, size, pos = self.info(hid)
        if sig < 0xFE:
            raise KeyError(hid)
        p = self.base + pos
        return self.d[p:p + size]

    def db_item(self, group, item) -> bytes:
        g = self.block(group)
        ibi, chunk = struct.unpack_from('<HH', g, item)
        iblock = struct.unpack_from('<H', g, ibi + 2)[0]
        ib = self.block(iblock)
        ptr = struct.unpack_from('<H', ib, chunk)[0]
        if ptr in (0, 0xFFFF) or ptr >= len(ib):
            return b''
        size = struct.unpack_from('<H', ib, ptr - 2)[0] - 2
        return ib[ptr:ptr + size]

    def db_map_item(self) -> bytes:
        m = self.block(self.db_map)
        _, _, group, item = struct.unpack_from('<HHHH', m, 0)
        return self.db_item(group, item)

# ---------------------------------------------------------------------------
# Monikers
# ---------------------------------------------------------------------------

SIZES = {0: 'tiny', 1: 'standard', 2: 'large', 3: 'huge'}
STYLES = {0: 'Text', 1: 'Text kurz', 2: 'Grafiktext', 3: 'Icon', 4: 'Werkzeug'}
ASPECTS = {0: 'VGA', 1: 'EGA', 2: 'CGA', 3: '?'}
COLORS = {0: '?', 1: 'S/W', 2: 'Grau 2', 3: 'Grau 4', 4: 'Grau 8',
          5: 'Farbe 2', 6: 'Farbe 4', 7: 'Farbe 8', 8: 'Farbe 24'}

PALETTE16 = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
    (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
    (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
]


def _default_palette256():
    """GEOS default 256-colour palette: 16 EGA colours, 16 greys, 6x6x6 cube."""
    pal = list(PALETTE16)
    pal += [(int(i * 255 / 15),) * 3 for i in range(16)]
    lv = (0, 51, 102, 153, 204, 255)
    pal += [(r, g, b) for r in lv for g in lv for b in lv]
    return (pal + [(0, 0, 0)] * 256)[:256]


PALETTE256 = _default_palette256()


def describe_entry_type(t: int) -> str:
    size = SIZES[(t >> 12) & 3]
    style = STYLES.get((t >> 8) & 15, str((t >> 8) & 15))
    if not t & 0x40:
        return f'Text ({style})'
    return f'{size}, {COLORS.get(t & 15, t & 15)}, {ASPECTS[(t >> 4) & 3]}'


def unpackbits(src: bytes, need: int) -> bytes:
    out = bytearray()
    i = 0
    while i < len(src) and len(out) < need:
        c = src[i]
        i += 1
        if c < 128:
            out += src[i:i + c + 1]
            i += c + 1
        elif c > 128:
            out += src[i:i + 1] * (257 - c)
            i += 1
    return bytes(out[:need]).ljust(need, b'\0')


@dataclass
class Moniker:
    entry_type: int
    kind: int               # VM_type byte
    width: int
    height: int
    text: str = ''
    bitmap: tuple | None = None   # (w, h, fmt, has_mask, rows: list[(mask,row)])
    raw: bytes = b''
    palette: list | None = None

    @property
    def is_graphic(self):
        return self.bitmap is not None

    @property
    def blank(self):
        """True for placeholder icons without visible pixels."""
        if not self.bitmap:
            return True
        w, h, fmt, has_mask, rows = self.bitmap
        if has_mask:
            return not any(any(mask) for mask, _ in rows)
        if fmt == 0:
            return not any(any(data) for _, data in rows)
        return len({data for _, data in rows}) <= 1 and len(set(rows[0][1])) <= 1

    def describe(self):
        if self.bitmap:
            w, h, fmt, mask, _ = self.bitmap
            f = {0: 'mono', 1: '16 Farben', 2: '256 Farben', 3: '24 Bit'}.get(fmt, fmt)
            return f'{w}×{h} {f}{" +Maske" if mask else ""} – {describe_entry_type(self.entry_type)}'
        return f'Text „{self.text}“'


def _find_bitmap(m: bytes, w: int, h: int):
    """Locate the bitmap element inside the moniker's gstring."""
    for off in range(5, min(len(m) - 8, 64)):
        bw, bh, comp, btype = struct.unpack_from('<HHBB', m, off + 3)
        if (bw, bh) == (w, h) and comp in (0, 1) and btype & 0x20 == 0 and (btype & 7) < 4:
            length = struct.unpack_from('<H', m, off + 1)[0]
            return off + 3, length
    return None, None


def parse_moniker(entry_type: int, m: bytes, version: int = 2) -> Moniker:
    if len(m) < 5:
        return Moniker(entry_type, 0, 0, 0, raw=m)
    kind, w, h = struct.unpack_from('<BHH', m, 0)
    mon = Moniker(entry_type, kind, w, h, raw=m)
    if not kind & 0x40:              # text moniker: VMT_mnemonicOffset + text
        # 1.x: type, width, height, mnemonic, text; 2.x: type, width, mnemonic, text
        mon.text = geos_text(m[6:] if version == 1 else m[4:])
        mon.width = mon.height = 0
        return mon
    off, length = _find_bitmap(m, w, h)
    if off is None:
        return mon
    bw, bh, comp, btype = struct.unpack_from('<HHBB', m, off)
    fmt, has_mask = btype & 7, bool(btype & 0x10)
    palette = None
    payload_off = off + 6
    if btype & 0x08 and len(m) >= off + 20:          # complex bitmap (CBitmap)
        data_off, pal_off = struct.unpack_from('<HH', m, off + 12)
        if btype & 0x40 and pal_off:
            n = struct.unpack_from('<H', m, off + pal_off)[0]
            p = off + pal_off + 2
            palette = [tuple(m[p + 3 * i:p + 3 * i + 3]) for i in range(min(n, 256))]
        payload_off = off + data_off
    mask_bytes = (bw + 7) // 8 if has_mask else 0
    data_bytes = {0: (bw + 7) // 8, 1: (bw + 1) // 2, 2: bw, 3: bw * 3}[fmt]
    row = mask_bytes + data_bytes
    payload = m[payload_off:]
    pixels = unpackbits(payload, row * bh) if comp == 1 else payload[:row * bh].ljust(row * bh, b'\0')
    rows = [(pixels[y * row:y * row + mask_bytes], pixels[y * row + mask_bytes:(y + 1) * row])
            for y in range(bh)]
    mon.bitmap = (bw, bh, fmt, has_mask, rows)
    mon.palette = palette
    return mon


def moniker_rgba(mon: Moniker):
    """Return (w, h, bytes RGBA) for a graphic moniker."""
    w, h, fmt, has_mask, rows = mon.bitmap
    out = bytearray(w * h * 4)
    for y, (mask, data) in enumerate(rows):
        for x in range(w):
            opaque = (mask[x >> 3] >> (7 - (x & 7))) & 1 if has_mask else 1
            if fmt == 0:
                bit = (data[x >> 3] >> (7 - (x & 7))) & 1
                rgb = (0, 0, 0) if bit else (255, 255, 255)
                if not has_mask and not bit:
                    opaque = 1
            elif fmt == 1:
                b = data[x >> 1]
                rgb = PALETTE16[(b >> 4) if not x & 1 else (b & 15)]
            elif fmt == 2:
                v = data[x]
                if mon.palette and v < len(mon.palette):
                    rgb = mon.palette[v]
                else:
                    rgb = PALETTE16[v] if v < 16 else PALETTE256[v]
            else:
                rgb = tuple(data[x * 3:x * 3 + 3])
            i = (y * w + x) * 4
            out[i:i + 4] = bytes((*rgb, 255 if opaque else 0))
    return w, h, bytes(out)

# ---------------------------------------------------------------------------
# Token database
# ---------------------------------------------------------------------------


@dataclass
class TokenEntry:
    token: str
    manuf: int
    group: int
    item: int
    monikers: list = field(default_factory=list)

    @property
    def key(self):
        return (self.token, self.manuf)

    def name(self):
        for m in self.monikers:
            if m.text:
                return m.text
        return ''

    def best_icon(self, prefer=(1, 2, 0, 3)):
        """Pick a graphic moniker: colour first, preferred size order, VGA aspect."""
        g = [m for m in self.monikers if m.is_graphic]
        if not g:
            return None
        g = [m for m in g if not m.blank] or g

        def score(m):
            t = m.entry_type
            size = (t >> 12) & 3
            return (prefer.index(size) if size in prefer else 9,
                    (t >> 4) & 3,                    # VGA aspect first
                    0 if m.bitmap[2] >= 1 else 1)    # colour before mono
        return sorted(g, key=score)[0]


class TokenDB:
    def __init__(self, path: str):
        self.path = path
        with open(path, 'rb') as f:
            self.vm = VMFile(f.read())
        self.version = 2 if self.vm.v2 else 1
        self.groups = {h for h, uid in self.vm.handles()}
        self.entries: dict[tuple, TokenEntry] = {}
        self._load()

    def _moniker_list(self, group, item):
        ml = self.vm.db_item(group, item)
        if not ml or len(ml) % 6:
            raise ValueError
        mons = []
        for i in range(0, len(ml), 6):
            t, g, it = struct.unpack_from('<HHH', ml, i)
            mons.append(parse_moniker(t, self.vm.db_item(g, it), self.version))
        return mons

    def _try(self, data, off):
        tok = data[off:off + 4]
        if not all(32 <= c < 127 for c in tok):
            return None
        manuf, group, item = struct.unpack_from('<HHH', data, off + 4)
        if group not in self.groups or item < 0x0E or item & 1:
            return None
        try:
            mons = self._moniker_list(group, item)
        except Exception:
            return None
        if not mons:
            return None
        return TokenEntry(tok.decode('latin-1'), manuf, group, item, mons)

    def _load(self):
        data = self.vm.db_map_item()
        if self.version == 2:
            # Array of TokenEntry (24 bytes); first slot is unused
            for off in range(0, len(data) - 23, 24):
                e = self._try(data, off)
                if e:
                    self.entries.setdefault(e.key, e)
        else:
            # 1.x map item: 10-byte header, then 26-byte entries interleaved
            # with gaps whose meaning is not yet known -> validated scan
            off = 10
            while off < len(data) - 10:
                e = self._try(data, off)
                if e:
                    self.entries.setdefault(e.key, e)
                    off += 26
                else:
                    off += 2

    def lookup(self, token: str, manuf: int = 0):
        return self.entries.get((token, manuf)) or next(
            (e for k, e in self.entries.items() if k[0] == token), None)


def find_token_db(root: str):
    """Locate the token database of a GEOS installation."""
    for rel in ('SYSTEM/TOKEN.DB', 'TOKEN.DB', 'privdata/token_da.000', 'PRIVDATA/TOKEN_DA.000'):
        for cand in (os.path.join(root, rel), os.path.join(root, rel.lower())):
            if os.path.isfile(cand):
                return cand
    return None

# ---------------------------------------------------------------------------
# Icons stored inside applications (geodes)
# ---------------------------------------------------------------------------


def _lmem_chunks(r: bytes) -> dict:
    """Chunk handle -> chunk data of an LMem resource (empty dict if none)."""
    if len(r) < 0x14:
        return {}
    off = struct.unpack_from('<H', r, 2)[0]
    n = struct.unpack_from('<H', r, 10)[0]
    if off < 0x10 or off + 2 * n > len(r) or n > 4000:
        return {}
    out = {}
    for i in range(n):
        h = off + 2 * i
        p = struct.unpack_from('<H', r, h)[0]
        if p in (0, 0xFFFF) or p < 2 or p > len(r):
            continue
        size = struct.unpack_from('<H', r, p - 2)[0] - 2
        if 0 <= size and p + size <= len(r):
            out[h] = r[p:p + size]
    return out


def geode_resources(d: bytes):
    """Return (appObj (chunk, resource), [resource bytes]) for 1.x and 2.x geodes."""
    if d[:4] == SIG_V2:
        nres, nimp, nexp = struct.unpack_from('<HHH', d, 0x108)
        app = struct.unpack_from('<HH', d, 0x114)
        tab, base = 0x158 + 14 * nimp + 4 * nexp, 0x100
    elif d[:4] == SIG_V1:
        h = 0xC0
        nexp, nimp = struct.unpack_from('<HH', d, h + 0x52)
        nres = struct.unpack_from('<H', d, h + 0x58)[0]
        app = struct.unpack_from('<HH', d, h + 0x1C)
        tab, base = h + 0x60 + 14 * nimp + 4 * nexp, 0
    else:
        return None, []
    if tab + 6 * nres > len(d) or nres > 1000:
        return None, []
    sizes = struct.unpack_from(f'<{nres}H', d, tab)
    pos = struct.unpack_from(f'<{nres}I', d, tab + 2 * nres)
    return app, [d[base + p:base + p + s] for p, s in zip(pos, sizes)]


@dataclass
class GeodeIconList:
    resource: int
    chunk: int
    monikers: list
    in_app_object: bool = False

    @property
    def has_text(self):
        return any(m.text for m in self.monikers)

    @property
    def is_tool(self):
        return all(((m.entry_type >> 8) & 15) == 4 for m in self.monikers if m.is_graphic)

    best_icon = TokenEntry.best_icon
    name = TokenEntry.name


def geode_icon_lists(d: bytes):
    """Find all moniker lists in an application and resolve their monikers."""
    app, res = geode_resources(d)
    if not res:
        return []
    version = 2 if d[:4] == SIG_V2 else 1
    chunks = {}
    lists = []
    for ri, r in enumerate(res):
        ch = _lmem_chunks(r)
        chunks[ri] = ch
    for ri, ch in chunks.items():
        for h, c in ch.items():
            if len(c) < 6 or len(c) % 6:
                continue
            ents = [struct.unpack_from('<HHH', c, i) for i in range(0, len(c), 6)]
            if not all(t & 0x80 for t, _, _ in ents):
                continue
            mons = []
            for t, mchunk, mres in ents:
                target = ri if mres == 0x4000 else (mres & 0x0FFF)
                data = chunks.get(target, {}).get(mchunk)
                if data is None:
                    mons = None
                    break
                mons.append(parse_moniker(t, data, version))
            if mons and any(m.is_graphic or m.text for m in mons):
                lists.append(GeodeIconList(ri, h, mons, app is not None and ri == app[1]))
    return lists


@dataclass
class GeodeIcons:
    app: GeodeIconList | None
    documents: list          # GeodeIconList for document tokens (usually one)
    others: list
    document_tokens: list = field(default_factory=list)

    def for_token(self, token, manuf=0):
        for (t, mf), l in zip(self.document_tokens, self.documents):
            if t == token:
                return l
        return None


def classify_geode_icons(d: bytes) -> GeodeIcons:
    lists = [l for l in geode_icon_lists(d) if not l.is_tool]
    graphic = [l for l in lists if l.best_icon()]
    app = next((l for l in graphic if l.in_app_object and l.has_text), None) \
        or next((l for l in graphic if l.in_app_object), None) \
        or next((l for l in graphic if l.has_text), None)
    rest = [l for l in graphic if l is not app]
    doc_tokens = geode_document_tokens(d)
    # Candidate document icon sets: no text, standard icon dimensions
    cands = [l for l in rest if not l.has_text and any(
        m.is_graphic and (m.bitmap[0], m.bitmap[1]) in ICON_DIMS for m in l.monikers)]
    cands.sort(key=lambda l: -sum(1 for m in l.monikers
                                  if m.is_graphic and (m.bitmap[0], m.bitmap[1]) in ICON_DIMS))
    docs = cands[:len(doc_tokens)]
    others = [l for l in rest if l not in docs]
    return GeodeIcons(app, docs, others, doc_tokens)


ICON_DIMS = {(64, 40), (48, 30), (32, 20)}


def geode_document_tokens(d: bytes):
    """Document tokens declared by an application (GenDocumentControl data)."""
    import re
    toks = []
    if d[:4] == SIG_V1:
        app_tok = d[0x14:0x1A]
        pat = re.compile(rb'\x18\xe7(.{4})(..)' + re.escape(app_tok), re.S)
    else:
        pat = re.compile(rb'\x07\x6c\x0a\x00(.{4})(..)', re.S)
    for m in pat.finditer(d):
        tok, manuf = m.group(1), struct.unpack('<H', m.group(2))[0]
        if all(32 <= c < 127 for c in tok):
            k = (tok.decode('latin-1'), manuf)
            if k not in toks:
                toks.append(k)
    return toks
