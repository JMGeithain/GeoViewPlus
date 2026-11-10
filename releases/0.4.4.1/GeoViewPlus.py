#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoViewPlus – GEOS / GeoWorks File Information Viewer
=====================================================
Erweiterte Version des klassischen GeoView von Rainer Bettsteller (RABE-Soft).

Unterstützt:
  • GeoWorks Ensemble 1.x  (Signatur C7 45 CF 53)
  • GEOS 2.x / NewDeal / Breadbox (Signatur C7 45 C1 53)

Zusatzfeatures:
  • Icon extrahieren und anzeigen (soweit im Header vorhanden)
  • Icon als .bmp / .png speichern
  • Drag & Drop / Kommandozeilen-Parameter
  • Moderne GUI

Projektleitung und Weiterentwicklung: Johannes Möller\nKI-Unterstützung: ChatGPT (OpenAI) und Grok (xAI), 2026
Original-Idee: Rainer Bettsteller, 2000/2001
"""

import sys
import os
import struct
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path


def resource_path(relative_path):
    """Return a bundled resource path (PyInstaller) or development path."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

try:
    from PIL import Image, ImageTk, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

import base64
import io
import csv
import hashlib
from collections import Counter, defaultdict

# GeoWorks 1.x 4-bit palette recovered from WORLD/DUMP.GEO (mapPixels):
# RGB components are 4-bit values 0, 5, 10, 15; scale by 17 for 8-bit RGB.
_GEOWORKS_R = (0, 0, 0, 0, 10, 10, 10, 10, 5, 5, 5, 5, 15, 15, 15, 15)
_GEOWORKS_G = (0, 0, 10, 10, 0, 0, 5, 10, 5, 5, 15, 15, 5, 5, 15, 15)
_GEOWORKS_B = (0, 10, 0, 10, 0, 10, 0, 10, 5, 15, 5, 15, 5, 15, 5, 15)
GEOWORKS_1X_PALETTE = tuple(
    (r * 17, g * 17, b * 17)
    for r, g, b in zip(_GEOWORKS_R, _GEOWORKS_G, _GEOWORKS_B)
)

# Windows application/window icon. In a PyInstaller one-file build the ICO
# is extracted to sys._MEIPASS; when run as a script it sits beside this file.
_APP_RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_ICON_PATH = _APP_RESOURCE_DIR / "geoworks_motif_icon.ico"

# Token icons: WP00 and WDAT are decoded from the supplied GeoWorks 1.2
# TOKEN.DB (monochrome 48x30 monikers); remaining entries are fallbacks.
TOKEN_ICONS = {
    'WP00': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAeCAYAAABqpJ3BAAABAklEQVR42u2X6woEIQiFM3r/V3Z/CRJZq55qd5hgkIa5mJ8njZi5RAcRxV9Wg5kp+m67+XNEEFr2pxkH9OKJiCPBaL8Q+ajzpZRCHg0gc15/S+ZHCCAjL45nCNRyYcgixPZEjonYSgUrZSTKep4l4NbAjm3zqAZWTsxoPJZAZoOoUSfk8sxHjvZU/orAKO22LQBVxEbC7e02EWejrylqm6F7rZBZtWH7NmrlrC5uq2eRBFwaQKUQUgM1Q6Dvaax7KwG/BHYQGBWwl8BpAta9RxHIttTb6sCsx0Geia8RQDh/rZVAOe9OIWRHinDeRYCZSV/9YcRrUSkZPpHN9vFvLYLkB7uBA18JRfQmAAAAAElFTkSuQmCC',
    'WDAT': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAeCAYAAABqpJ3BAAABB0lEQVR42tWYQRLFIAhDS+5/Z/7KGYexVgzxt266qfZFIwXM3S/VMDN3d7uEA0r4/vkpARFaKQJqeLUInIBXisApeJUIq4hCPdQs6qy+d1RAg8oA7cyRWKgHyVijgVfYCVXw/xIB1vM9/K4lGBFgPxZ3fucUGBGogmdPYVcEmMXvLjFjiexcsIvOTmFXSGYesl59gh+l0lkhGRuiYtFKIdk7BGZnYvzPChkFBXkYzdppJoSF3/6Rxfi9Aj+LVFToZZK5EURWCJvQUcnc3Z04BS+rB+KFHSV6r6kH2BzoNSXlKlR1n6i0qH+CUzS5ytsqs//EZxpbEVbZXpS1Fhu0ujdqyubuifED5dRJQKOEFXgAAAAASUVORK5CYII=',
    'DP00': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABiElEQVR4nO2ZMUvDQBiGn6T+AUEQLKJO0kFEUNyKdHFw8C900Vk6iIuTUxHESRc3B8VN0LWUbkIRiqLoolVbEAJuVixNXEy19oIod7kr3DMm4cv78OUSch9Y9OJEnQiCIIgzyG84jiPM6ooOmhYeojN1WYUXDq2kVWf6E/XtEtDdiY4OmBoevjL97ERbwOTwISIJ4RroJayAbqyAbqyAbqyAbqyAbqyAbqyAbvpUFH3cKpJwXVq+z+t7g6pX56RSZLdwSLPVlHovpR2YXF8kk89y8XTL2sIS+8t5Iv7N/43yR6j28szq0Sb3Xo30+DSZ1KzU+rGsgZbvc169AmBmbEJq7dgWsfO5ARIgd8cmFoGE6zI1kgKgfHcptbaSt9B3kv2D5OazjA4kKd2UKVyfSa2vVKCycUyj+caDVyd/usdO4QDZm35KBIZzcyrKCun5L7EV0I0V0I0V0I0V0I0V0E1bIJz+hdNAExFNKjs6YLJE1JhV+Idt4qAbxNN64RqIGuvrxMRMFoAPFWt12rBSdzsAAAAASUVORK5CYII=',
    'GEOS': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABuUlEQVR4nO2ZzStEURiHnyvX14KSmjDFho1EoWkW/AUTC1nJxlL5A5ShZGtlTxbsaEqWmoXVjJKvkhkZMrMYC9I1GYuZa6E7DHeSOse56jzLe2/n/T29nfv1gkYtRqUTtm3bfxnkJwzDcM1a5XbQa+GhcqZvVs6Fs0PLsjP9itXDeeB7J8o64NXw8JHpaydKAl4O7+Am4boH/hNaQDVaQDVaQDVaQDVaQDVaQDVaQDXVMhY1qgyGxwcIjvXj62wBwHrIcX1yx0Y4IrSWFIHJcIhAqI/zgyRrcztYDzk6etoYmRgUXku4gL/bRyDUx4uVZyMcIZ97BeAynuIynhJdTvwe6Oz1A5BJZkvhZSK8A84/g8+f3s4fBYCV6XVuzjLC6gnvQOo0DUB7l4+aehN4/xi/OroVXQqQIJBOZInvndLQWMfU4ijNrU2YtdWYtaboUoCku9Dm0i7pRJbgaD8L2zMUCkWeH3Mc71/wdG8JrSVFoFi0iW7FiG7FZCxfxr9/EmsB1WgB1WgB1WgB1WgB1ZQEnOnf53d3r+E2qSzrgJclKo1ZXaffXhx0g/u03nUPVBrrq8SLmTQAb5XqiIFFUevlAAAAAElFTkSuQmCC',
    'DDAT': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABv0lEQVR4nO2ZO0vDUBiGn7QuDmI3UamIs4iCioLS1cXB36CL4GXpIg76B1wUHBTRSXBwE1o6CKKgCFrrBYcWUSva4uQFK4Q0TunFniBi4knhPGMS+r0PX3M55wOFXDS7E6Zpmv8Z5Cc0TRNm9YkOei082GeqsLIuXGpvczvTr5i8vAEqO1HWAa+Gh2Km750oCHg5vIVIQngPVBNKQDZKQDZKQDZKQDZKQDZKQDZKQDY1Tv3QxHkSzefHzBvoHzle0nekYhHiG6sYuu5UmQoc78BaqJfNkSGer6/onw4zvLwG4vW4IzjWgVLenh7ZnZ+luaePYP8ArYMhshcJxvZPyq7bnZvhanvrT7VcEQAw8waZRJz6YAuNXd1kLxKFc9HwFKlYBDNv/LmOawIA1gZC6Tr8PZshGd1xrIZrTyHN56ehoxOAzFnxr6PnPhyt40oH6hqb6B2foj7YQvrwgNv9PWoDATdKOS8wuneMnvvk9eGeo8UFTtdXwMWNvsLzrRr2haByh67q38RKQDZKQDZKQDZKQDZKQDYFAevbwvrW8CKiSWVZB7wsYTdmFa62vTjoBvG0XngP2I31ZeLFTAqAL/SGlDKhcli3AAAAAElFTkSuQmCC',
    'scbk': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAACK0lEQVR4nO2Zz0sUYRjHP6Ozq677o9lCWYSwYA0M+kW5KnQoKDMIxEv3jtFfEFGH/oFO4TEKDx76AR0qSIgOoSR4UCyCUGshXRR2dR13dmZ3Ou3GtrNG+NY7C+/nOPMy7/fDw8PMvA8o5KI1uuG6rvs/g/wJTdM8s7Z4XfRbeGicqc6qsvD1w/C/zvRXXLmZB+orUVMBv4aHX5l+r0RVwM/hK3hJePZAM6EEZKMEZKMEZKMEZKMEZKMEZKMEZKOLelC85zzHhu4TjvejaS0UdzdYXZhgef6BqC08ESLQqndwZnQKy8zwfvIkbtmmq/cq7Z09Ih6/J0IEOiKH0YNRrJ01SsVtHDtP+tPjmjVGYphk6i7RQyfQg1Gy6x+ZeXph33sLETC3VrHMNTqNPi7eWCGXmWfj+zTfFiawrSyh2FHOXnuBbWWZfX6Z7c1FEdsCgpq4XCow++wS6aVHFHc3MRJDJAfuMDD2BoCu3lFa9RA/vkwJDQ8Cm9jcWmbx3S0ADnSfIzX+lsjB4wTaYuxxfrZvhFQgFD3C6ZFJjMQweiCMY+9QLhUp5NPYVo7MyitKjkmi7zrheL+ILasIqYBj59HbYpwaeUKg3aDsFMitz/H5w20AzNxX5l6OkUzdY3B8Gj0YEdbE1do2w7kQ1J/QNf2bWAnIRgnIRgnIRgnIRgnIpipQ+baofGv4Ea9JZU0F/CzRaMzq+afhx0E3eE/rPXug0VhfJn7MpAD4CbtovDCSjlpRAAAAAElFTkSuQmCC',
    'Scrp': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAACK0lEQVR4nO2Zz0sUYRjHP6Ozq677o9lCWYSwYA0M+kW5KnQoKDMIxEv3jtFfEFGH/oFO4TEKDx76AR0qSIgOoSR4UCyCUGshXRR2dR13dmZ3Ou3GtrNG+NY7C+/nOPMy7/fDw8PMvA8o5KI1uuG6rvs/g/wJTdM8s7Z4XfRbeGicqc6qsvD1w/C/zvRXXLmZB+orUVMBv4aHX5l+r0RVwM/hK3hJePZAM6EEZKMEZKMEZKMEZKMEZKMEZKMEZKOLelC85zzHhu4TjvejaS0UdzdYXZhgef6BqC08ESLQqndwZnQKy8zwfvIkbtmmq/cq7Z09Ih6/J0IEOiKH0YNRrJ01SsVtHDtP+tPjmjVGYphk6i7RQyfQg1Gy6x+ZeXph33sLETC3VrHMNTqNPi7eWCGXmWfj+zTfFiawrSyh2FHOXnuBbWWZfX6Z7c1FEdsCgpq4XCow++wS6aVHFHc3MRJDJAfuMDD2BoCu3lFa9RA/vkwJDQ8Cm9jcWmbx3S0ADnSfIzX+lsjB4wTaYuxxfrZvhFQgFD3C6ZFJjMQweiCMY+9QLhUp5NPYVo7MyitKjkmi7zrheL+ILasIqYBj59HbYpwaeUKg3aDsFMitz/H5w20AzNxX5l6OkUzdY3B8Gj0YEdbE1do2w7kQ1J/QNf2bWAnIRgnIRgnIRgnIRgnIpipQ+baofGv4Ea9JZU0F/CzRaMzq+afhx0E3eE/rPXug0VhfJn7MpAD4CbtovDCSjlpRAAAAAElFTkSuQmCC',
    'DEFAULT': 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAADnElEQVR4nO2ZbUxTVxiAnxatQGEoA9TRVanI14ZZTSQbEWdSiYpTMnXbD81MZAtxkbElOlmMP2QsMS6amKAxGZtbMLpkiI4I0ch00+wjY46hAistdJLNbI6P21IuCFzcD9IrH7etc9Fbk/v8uj3n5M373HPv6T3nBQ110fnr6BLcdx9lIsGImxmjmKteqTHUkgf/OU2x8g1cvm7Lw87pP/FNzefA1JmYMAOhmjzcy2nyTMgCoZy8DyUJxXfgcUITUBtNQG00AbXRBNRGE1AbTUBtNAG1mRZsgF6nIz/PRl7uMsymuQAIgofrrQ7KDhwF4OKZY+j1E+9FzblLHDzyGQDTp0/j9Vfzsb34PAnxTyKKAzRea+Xjyi/549bfADyXmUbhltdImmdCr9MhePqoPnuBL6rr/p/Ae28XsMqWww8Nv7J3/2F6BQ9pCy28vMY2ZWz+5u24PX1T2vfu2k52lpWT1bWcqKolLcXCByVFWBel80bxHtweLx/ufoeeXjebC3cyIklkL7ESHxcbLL3AAskWM6tsOXj7RcoOHKVfHADgalMzV5uagwYHSE+xkJ1lpVdwU1F5CkmSaPjlOnX1l1n/Ui4b162k9sK3GCMj6O4REAcGEQcGqau/fF/xAwpkpCYD0O7qlJMPxFfHy+XrfYcqOPf1FVKTkwBwdf6JJElyv6PjJgCpC5OoOF5Fd6+A2TSXM5Xl2J0uGhpvcLq2nj5v/4ML+Lb/d8dto32nAwBv7Sylxd4u//b3CI0FmRz73uHC0NAwRbvK2LRxLVmLM8nMSCEzI4XlS7PYWrQ7oEDAVajZ7gRgQdLThIfPAMY21k03fgsYdDx2pwuA+eZEwsLC5PZki3ms3zHWf+uvf/io/FNe2fou23aUMjo6imWeiShj5IMLODs6OX/xO6KjjLxf/CazE+KYYTBgMBjuW6C1rYPvf2okdlYMBZvWE2WMZIn1WVavyMHT56Wq5jxPzYmntKSIRc+kEhkRzuCdOwyPjHC7qwdvvxgwvjyP/o5V9Ho9G9bmkrdiGabEOUjSKILbg93h4vAnJ7jd1aO4jP74cxMlpQeB8cvoCyTExyKKgzRea5GX0VkxT7BnxzbmmxOJjjYyNDSMo/0mR46dpM35+4S4kw+4ggqEGpMFHvt/Yk1AbTQBtdEE1EYTUBtNQG1kAd+3xfjv/VBDqVI5YQZCWcJfmVWx+h2KhW5QrtYrvgP+yvpqEoo5aQD8C7vEU6zd3SbaAAAAAElFTkSuQmCC',
}


def get_token_icon_image(token: str, scale=1):
    """Return a PIL Image for the given token, or DEFAULT if unknown."""
    if not HAS_PIL:
        return None
    key = (token or '').strip()
    b64 = TOKEN_ICONS.get(key) or TOKEN_ICONS.get('DEFAULT')
    if not b64:
        return None
    try:
        data = base64.b64decode(b64)
        img = Image.open(io.BytesIO(data)).convert('RGBA')
        if scale != 1:
            img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
        return img
    except Exception:
        return None


def _decode_packbits(src: bytes, expected_length: int):
    """Decode a PackBits stream; return bytes only when fully and exactly consumed."""
    out = bytearray()
    i = 0
    while i < len(src) and len(out) < expected_length:
        control = src[i]
        i += 1
        if control <= 127:
            count = control + 1
            if i + count > len(src):
                return None
            out.extend(src[i:i + count])
            i += count
        elif control >= 129:
            count = 257 - control
            if i >= len(src):
                return None
            out.extend(src[i:i + 1] * count)
            i += 1
        # 128 is the PackBits no-op.
        if len(out) > expected_length:
            return None
    if len(out) != expected_length or i != len(src):
        return None
    return bytes(out)


def scan_token_db_monikers(data: bytes):
    """Find structurally validated GeoWorks 1.x TOKEN.DB moniker candidates.

    This is a raw-file signature scan, not yet a VM-resource/token-name resolver.
    """
    records = []
    for off in range(0, len(data) - 14):
        moniker_type = data[off]
        if moniker_type not in (0x41, 0x46):
            continue
        width = int.from_bytes(data[off + 1:off + 3], 'little')
        height = int.from_bytes(data[off + 3:off + 5], 'little')
        if data[off + 5] != 0x1A:
            continue
        bitmap_length = int.from_bytes(data[off + 6:off + 8], 'little')
        end = off + 8 + bitmap_length
        if bitmap_length < 6 or end > len(data):
            continue
        bitmap_width = int.from_bytes(data[off + 8:off + 10], 'little')
        bitmap_height = int.from_bytes(data[off + 10:off + 12], 'little')
        compression = data[off + 12]
        bitmap_type = data[off + 13]
        if (width, height) != (bitmap_width, bitmap_height):
            continue
        if compression != 1 or bitmap_type not in (0x00, 0x11):
            continue
        row_bytes = (width + 7) // 8
        if bitmap_type == 0x11:
            row_bytes += (width + 1) // 2
        expected = row_bytes * height
        decoded = _decode_packbits(data[off + 14:end], expected)
        if decoded is None:
            continue
        prefix_value = int.from_bytes(data[off - 2:off], 'little') if off >= 2 else None
        records.append({
            'offset': off, 'type': moniker_type, 'width': width, 'height': height,
            'bitmap_length': bitmap_length, 'bitmap_type': bitmap_type,
            'prefix_value': prefix_value,
            'prefix_delta': (prefix_value - bitmap_length) if prefix_value is not None else None,
            'decoded_sha256': hashlib.sha256(decoded).hexdigest(),
            'serialized_sha256': hashlib.sha256(data[off:end]).hexdigest(),
            'decoded_length': len(decoded),
            'decoded_data': decoded,
        })
    return records


def summarize_token_db_monikers(records):
    """Human-readable summary; does not claim token/resource ownership."""
    lines = [f'Moniker-Kandidaten: {len(records)}',
             'Validierung: Monikerkopf, GString-Opcode 1A, Bitmap-Header, PackBits und Ausgabelänge.',
             'Hinweis: Fundstellen sind noch nicht mit Token-Namen oder VM-Ressourcen verknüpft.', '']
    dims = Counter((r['width'], r['height'], r['type'], r['bitmap_type']) for r in records)
    lines.append('Verteilung:')
    for (w, h, typ, btype), count in sorted(dims.items()):
        mode = 'S/W' if typ == 0x41 else 'Farbe'
        lines.append(f'  {w}x{h} {mode}: {count}')
    deltas = Counter(r['prefix_delta'] for r in records)
    lines.append('')
    lines.append('Vorfeld-Differenz (Wert bei Offset -2 minus Bitmap-Länge):')
    for delta, count in sorted(deltas.items(), key=lambda x: (x[0] is None, x[0] or 0)):
        lines.append(f'  {delta}: {count}')
    # Focus the on-screen duplicate detail on the 37 exceptional +13 records
    # documented in the current investigation; the CSV still contains all hits.
    special = [r for r in records if r['prefix_delta'] == 13]
    groups = defaultdict(list)
    for r in special:
        groups[r['decoded_sha256']].append(r)
    duplicates = [g for g in groups.values() if len(g) > 1]
    lines.append('')
    lines.append(f'Sondergruppe mit Differenz +13: {len(special)} Fundstellen, {len(groups)} unterschiedliche Bildinhalte, {len(duplicates)} Duplikatgruppen.')
    for idx, group in enumerate(sorted(duplicates, key=lambda g: g[0]['offset']), 1):
        offsets = ', '.join(f"0x{x['offset']:06X}" for x in group)
        lines.append(f'  Gruppe {idx} ({len(group)}x): {offsets}')
    return '\n'.join(lines)

# ---------------------------------------------------------------------------
# GEOS Header Parsing
# ---------------------------------------------------------------------------

SIG_V1 = b'\xC7\x45\xCF\x53'   # GeoWorks 1.x
SIG_V2 = b'\xC7\x45\xC1\x53'   # GEOS 2.x+

FILE_TYPES = {
    0: "Unknown / Non-GEOS",
    1: "Executable / Application",
    2: "VM File",
    3: "Binary / Data",
    4: "Directory Label",
}

def read_cstr(data: bytes, offset: int, maxlen: int = 64) -> str:
    """Null-terminated string lesen, bis maxlen oder Null."""
    end = data.find(b'\x00', offset, offset + maxlen)
    if end < 0:
        end = offset + maxlen
    try:
        return data[offset:end].decode('cp850', errors='replace').strip()
    except Exception:
        return data[offset:end].decode('latin-1', errors='replace').strip()


def is_readable_text(s: str) -> bool:
    """True, wenn der String wie echte Notizen aussieht (kein Binärmüll)."""
    if not s:
        return False
    s = s.strip()
    if len(s) < 4:
        return False
    # Mindestens ein paar echte Buchstaben
    letters = sum(1 for c in s if c.isalpha())
    if letters < 4:
        return False
    printable = sum(1 for c in s if c.isprintable() or c in '\t\n\r')
    if printable / len(s) < 0.85:
        return False
    # Ablehnen, wenn überwiegend Nicht-ASCII-Kontroll-/Symbolmüll
    weird = sum(1 for c in s if ord(c) < 32 or (0x7f <= ord(c) <= 0x9f))
    if weird > 0 and weird >= letters // 2:
        return False
    return True


# Empirisch aus deutschen GeoWorks-1.x-Dateiköpfen ermittelte Zeichen.
# Die Zuordnungen gelten für den untersuchten deutschen Dateibestand; sie sind
# keine allgemeine CP850- oder PC/GEOS-Zeichensatzdefinition.
GEOWORKS_1X_NAME_CHARS = {
    0x86: "Ü",
    0x8A: "ä",
    0x9A: "ö",
    0x9F: "ü",
    0xA7: "ß",
    0xA8: "®",  # durch "reflecta®" im Archiv stark gestützt
    0xE3: "„",  # in Dateinamen als öffnendes Anführungszeichen verwendet
    0xD3: "“",  # Gegenzeichen; Darstellung in GeoManager noch zu prüfen
}


def decode_geos_name(data: bytes, offset: int = 4, maxlen: int = 36) -> str:
    """GEOS-Langnamen lesen; deutsche 1.x-Zeichen empirisch übersetzen.

    Unbekannte Bytes bleiben über CP850 sichtbar. Die Funktion behauptet damit
    ausdrücklich keine vollständige Zeichensatzdefinition.
    """
    chunk = data[offset:offset + maxlen]
    parts = []
    cur = bytearray()
    for b in chunk:
        if b == 0:
            if cur:
                parts.append(bytes(cur))
                cur = bytearray()
                if len(parts) >= 2:
                    break
        else:
            cur.append(b)
    if cur:
        parts.append(bytes(cur))
    if not parts:
        return ""
    # @DIRNAME: zwei Textfragmente zusammenfügen, sonst nur ersten Teil
    if (len(parts) >= 2 and len(parts[0]) <= 8
            and sum(1 for b in parts[1] if 65 <= b <= 122) >= 4):
        raw = parts[0] + parts[1]
    else:
        raw = parts[0]
    decoded = raw.decode("cp850", errors="replace")
    return "".join(GEOWORKS_1X_NAME_CHARS.get(b, ch)
                   for b, ch in zip(raw, decoded)).strip()



def geos_to_unicode(raw: bytes) -> str:
    """GEOS/DOS-Text nach Unicode (deutsche Umlaute etc.)."""
    # Häufige GEOS-/CP850-Abweichungen in deutschen Dateien
    # 0x86 = Ü, 0x9A = ö (in manchen GEOS-Installationen)
    table = str.maketrans({
        0x81: "ü", 0x84: "ä", 0x8e: "Ä", 0x94: "ö", 0x99: "Ö",
        0x9a: "ö", 0x9b: "ü", 0x9c: "£", 0x9f: "ü",
        0x86: "Ü", 0x8a: "ä", 0x8b: "ï", 0x8c: "î",
        0xa0: "á", 0xa1: "í", 0xa2: "ó", 0xa3: "ú",
        0xe1: "ß",
    })
    try:
        s = raw.decode("latin-1")
    except Exception:
        s = raw.decode("cp850", errors="replace")
    return s.translate(table).strip()

def parse_geos_header(data: bytes) -> dict:
    """Parst den GEOS-Header (beide Versionen) anhand realer Dateibeispiele."""
    info = {
        'valid': False,
        'version': None,
        'signature': None,
        'geos_name': '',
        'dos_name': '',
        'file_type': '',
        'file_type_id': -1,
        'version_str': '',
        'release_str': '',
        'protocol_str': '',
        'copyright': '',
        'user_notes': '',
        'created': '',
        'modified': '',
        'icon_token': '',
        'creator_token': '',
        'raw_icon': None,          # (width, height, bitmap_bytes) oder None
        'error': '',
    }

    if len(data) < 200:
        info['error'] = 'Datei zu klein'
        return info

    sig = data[0:4]
    if sig == SIG_V2:
        # ============================================================
        # GEOS 2.x / Ensemble 2+ / NewDeal / Breadbox
        # Layout (from real WRITE.GEO / natur.000):
        #   0x00  signature C7 45 C1 53
        #   0x04  long name (null-terminated, up to ~32 bytes)
        #   0x28  file type (word)  1=Application, 2=VM/Data ...
        #   0x2C  version / release / protocol words
        #   0x38  icon token (4 chars, e.g. "WP00")
        #   0x3E  creator token (4 chars, e.g. "GEOS")
        #   0xA8  copyright string
        # ============================================================
        info['version'] = 2
        info['signature'] = 'C7 45 C1 53  (GEOS 2.x / Ensemble 2+ / NewDeal / Breadbox)'
        info['geos_name'] = decode_geos_name(data, 0x04, 36)

        if len(data) >= 0x2A:
            ftype = struct.unpack_from('<H', data, 0x28)[0]
            info['file_type_id'] = ftype
            info['file_type'] = FILE_TYPES.get(ftype, f'Unknown ({ftype})')

        if len(data) >= 0x38:
            # Observed layout varies slightly; take the six words starting at 0x2C
            vals = struct.unpack_from('<HHHHHH', data, 0x2C)
            info['version_str']  = f'{vals[0]}.{vals[1]}'
            info['release_str']  = f'{vals[2]}.{vals[3]}'
            info['protocol_str'] = f'{vals[4]}.{vals[5]}'

        if len(data) >= 0x42:
            info['icon_token']    = read_cstr(data, 0x38, 4)
            info['creator_token'] = read_cstr(data, 0x3E, 4)

        # Copyright is consistently at 0xA8 in the samples
        if len(data) >= 0xC0:
            end = data.find(b"\x00", 0xA8, 0xA8 + 44)
        if end < 0: end = 0xA8 + 44
        info['copyright'] = geos_to_unicode(data[0xA8:end])

        # User notes: bei GEOS 2.x typischerweise ab Offset 0x44 (nach den Tokens)
        # Fallback auf weitere Offsets
        for off, maxlen in ((0x44, 96), (0xC8, 80), (0x100, 80), (0x140, 80)):
            end = data.find(b"\x00", off, off + maxlen)
            if end < 0:
                end = off + maxlen
            raw = data[off:end]
            if not raw or raw[0] == 0:
                continue
            notes = geos_to_unicode(raw)
            if is_readable_text(notes):
                info["user_notes"] = notes
                break

    elif sig == SIG_V1:
        # ============================================================
        # GeoWorks Ensemble 1.x
        # Layout (from real DRAW.GEO / DRAGON.000):
        #   0x00  signature C7 45 CF 53
        #   0x04  several words (class / flags / version info)
        #   0x14  tokens (e.g. "DP00\0\0GEOS" or "DDAT\0\0DP00")
        #   0x20  long name (null-terminated)
        #   0xA8  copyright string
        # ============================================================
        info['version'] = 1
        info['signature'] = 'C7 45 CF 53  (GeoWorks Ensemble 1.x)'

        if len(data) >= 0x14:
            words = struct.unpack_from('<HHHHHHHH', data, 0x04)
            # First non-zero word often indicates type/class
            ftype = words[0] if words[0] else words[2]
            info['file_type_id'] = ftype
            if (ftype & 0xFF) == 0:
                # A valid GeoWorks 1.x signature is decisive evidence that this
                # is a GEOS-format file. Type 0 only means that the header's
                # standard file-type field does not identify a known class.
                # Third-party programs (e.g. UHR.GEO by Thomas Wachsmann,
                # documented by the user from "Das große Buch von GeoWorks")
                # must not be mislabeled as "Non-GEOS".
                info['file_type'] = 'GeoWorks 1.x GEO-Datei (Drittanbieter / Typkennung 0)'
            else:
                info['file_type'] = FILE_TYPES.get(ftype & 0xFF, f'Class / Type {ftype}')
            # Version-ish fields
            info['version_str']  = f'{words[2]}.{words[3]}'
            info['release_str']  = f'{words[4]}.{words[5]}'
            info['protocol_str'] = f'{words[6]}.{words[7]}'

        if len(data) >= 0x1C:
            # Tokens at 0x14
            info['icon_token']    = read_cstr(data, 0x14, 4)
            info['creator_token'] = read_cstr(data, 0x1A, 4)

        if len(data) >= 0x40:
            info['geos_name'] = decode_geos_name(data, 0x20, 36)

        if len(data) >= 0xC0:
            info['copyright'] = read_cstr(data, 0xA8, 32)

        # User notes (1.x – falls vorhanden)
        for off, maxlen in ((0x60, 64), (0xC0, 60), (0xE0, 60), (0x100, 60)):
            end = data.find(b"\x00", off, off + maxlen)
            if end < 0:
                end = off + maxlen
            raw = data[off:end]
            if not raw or raw[0] == 0:
                continue
            notes = geos_to_unicode(raw)
            if is_readable_text(notes):
                info["user_notes"] = notes
                break

    else:
        info['error'] = f'Keine bekannte GEOS-Signatur (gefunden: {sig.hex(" ").upper()})'
        return info

    info['valid'] = True

    # Spezielle Verzeichnis-Hilfsdateien von PC/GEOS
    gname = info.get('geos_name', '')
    if 'Directory Information' in gname or gname.startswith('@Directory'):
        info['file_type'] = 'Directory Information (@DIRECTO)'
    elif info['version'] == 2 and len(data) <= 600:
        # @DIRNAME.000 ist typischerweise sehr klein und enthält den Langnamen
        # Erkennung: Name sieht aus wie Verzeichnisname, Datei klein
        if gname and not gname.startswith('@') and info.get('file_type_id', -1) not in (1,):
            # Bleibt generisch; der Langname wurde bereits per decode_geos_name gelesen
            pass

    info['raw_icon'] = try_extract_icon(data, info['version'])
    return info


def try_extract_icon(data: bytes, version: int):
    """
    Heuristik: Suche nach einem plausiblen monochromen Icon-Bitmap.
    Gibt (width, height, bitmap) zurück oder None.
    """
    # Classic C64-style icon is 3 bytes wide × 21 high = 63 bytes,
    # but PC/GEOS uses larger icons. We look for common sizes.
    candidates = [
        (48, 30),   # common desktop icon size
        (32, 32),
        (48, 48),
        (16, 16),
        (24, 24),
        (64, 40),
    ]

    # Search in the first 2 KB of the file
    search_limit = min(len(data), 2048)

    for w, h in candidates:
        bytes_needed = (w * h + 7) // 8
        # Look for a stretch of data that is not all zero/FF
        for off in range(100, search_limit - bytes_needed, 2):
            chunk = data[off:off + bytes_needed]
            if len(chunk) < bytes_needed:
                continue
            # Skip pure zero or pure FF
            if chunk == b'\x00' * bytes_needed or chunk == b'\xff' * bytes_needed:
                continue
            # Require some variation
            if len(set(chunk)) < 4:
                continue
            # Accept first plausible candidate
            return (w, h, chunk)

    return None


def make_icon_image(width: int, height: int, bitmap: bytes, scale: int = 4):
    """Monochromes Bitmap → PIL Image (schwarz auf transparent/weiß)."""
    if not HAS_PIL:
        return None
    img = Image.new('1', (width, height), 1)  # 1 = white
    pixels = img.load()
    bit_idx = 0
    for y in range(height):
        for x in range(width):
            byte_idx = bit_idx // 8
            bit = 7 - (bit_idx % 8)
            if byte_idx < len(bitmap):
                if (bitmap[byte_idx] >> bit) & 1:
                    pixels[x, y] = 0  # black
            bit_idx += 1
    # Scale up for better visibility
    img = img.resize((width * scale, height * scale), Image.NEAREST)
    # Convert to RGBA with transparency
    img = img.convert('RGBA')
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 200:  # near white → transparent
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append((0, 0, 0, 255))
    img.putdata(new_data)
    return img


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class GeoViewPlusApp(tk.Tk):
    def __init__(self, initial_file=None):
        super().__init__()
        self.title('GeoViewPlus – GEOS File Information Viewer')
        # Set the supplied ICO directly on the root window; ignore unsupported platforms.
        try:
            if APP_ICON_PATH.is_file():
                self.iconbitmap(str(APP_ICON_PATH))
        except tk.TclError:
            pass
        self.geometry('620x620')
        self.minsize(520, 480)
        self.configure(bg='#f0f0f0')

        self.current_info = None
        self.current_path = None
        self.icon_image = None
        self.tk_icon = None

        self._build_ui()

        if initial_file:
            self.load_file(initial_file)

        # Drag & Drop (basic, works on most platforms via bind)
        self.drop_target_register = getattr(self, 'drop_target_register', None)

    def _build_ui(self):
        # Menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Datei öffnen…', command=self.open_file, accelerator='Ctrl+O')
        filemenu.add_command(label='Icon speichern…', command=self.save_icon, state='disabled')
        filemenu.add_separator()
        filemenu.add_command(label='Beenden', command=self.destroy)
        menubar.add_cascade(label='Datei', menu=filemenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='Über…', command=self.show_about)
        menubar.add_cascade(label='Hilfe', menu=helpmenu)
        self.config(menu=menubar)
        self.bind('<Control-o>', lambda e: self.open_file())

        # Toolbar
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text='Datei öffnen…', command=self.open_file).pack(side=tk.LEFT, padx=2)
        self.btn_save_icon = ttk.Button(toolbar, text='Icon speichern…', command=self.save_icon, state='disabled')
        self.btn_save_icon.pack(side=tk.LEFT, padx=2)
        self.btn_export_index = ttk.Button(toolbar, text='Moniker-Index CSV…', command=self.export_moniker_index, state='disabled')
        self.btn_export_index.pack(side=tk.LEFT, padx=2)
        self.btn_gallery = ttk.Button(toolbar, text='Moniker-Galerie…', command=self.open_moniker_gallery, state='disabled')
        self.btn_gallery.pack(side=tk.LEFT, padx=2)

        # Main content
        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        # Left: Icon
        icon_frame = ttk.LabelFrame(main, text='Icon', padding=8)
        icon_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self.icon_label = ttk.Label(icon_frame, text='(kein Icon)', width=18, anchor='center')
        self.icon_label.pack(pady=10)
        self.icon_info = ttk.Label(icon_frame, text='', font=('', 8))
        self.icon_info.pack()

        # Right: Info fields
        info_frame = ttk.Frame(main)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fields = {}
        labels = [
            ('Datei', 'path'),
            ('Signatur / Version', 'signature'),
            ('GEOS-Name', 'geos_name'),
            ('DOS-Name', 'dos_name'),
            ('Datei-Typ', 'file_type'),
            ('Version', 'version_str'),
            ('Release', 'release_str'),
            ('Protokoll', 'protocol_str'),
            ('Icon-Token', 'icon_token'),
            ('Creator-Token', 'creator_token'),
            ('Copyright', 'copyright'),
        ]
        for i, (label, key) in enumerate(labels):
            ttk.Label(info_frame, text=label + ':', anchor='e').grid(row=i, column=0, sticky='e', padx=4, pady=2)
            var = tk.StringVar()
            ent = ttk.Entry(info_frame, textvariable=var, state='readonly', width=48)
            ent.grid(row=i, column=1, sticky='ew', padx=4, pady=2)
            self.fields[key] = var
        info_frame.columnconfigure(1, weight=1)

        # User notes
        notes_frame = ttk.LabelFrame(self, text='Datei-Notizen / User Notes', padding=4)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=6, wrap=tk.WORD, state='disabled')
        self.notes_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status = ttk.Label(self, text='Bereit – Datei öffnen oder per Drag&Drop ablegen', relief=tk.SUNKEN, anchor='w')
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def open_file(self):
        path = filedialog.askopenfilename(
            title='GEOS / GeoWorks-Datei öffnen',
            filetypes=[
                ('GEOS-Dateien inkl. TOKEN.DB', '*.geo *.000 *.001 *.002 *.003 *.004 *.005 *.006 *.007 *.008 *.009 *.gea *.geb *.gec *.db'),
                ('Alle Dateien', '*.*'),
            ]
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str):
        path = os.path.abspath(path)
        try:
            with open(path, 'rb') as f:
                file_data = f.read()
            data = file_data[:4096]  # header + icon parsing
        except Exception as e:
            messagebox.showerror('Fehler', f'Datei konnte nicht gelesen werden:\n{e}')
            return

        info = parse_geos_header(data)
        info['dos_name'] = Path(path).name
        # TOKEN.DB ist keine normale ausführbare GEO-Anwendung.
        # GeoWorks-1.x-Kennung plus VM-Marker EB AD bei Offset 0xC8
        # werden gemeinsam verlangt, damit gleichnamige Fremddateien
        # nicht allein aufgrund ihres Dateinamens fehlklassifiziert werden.
        dn = info['dos_name'].upper()
        is_token_db = (
            dn == 'TOKEN.DB'
            and data[:4] == SIG_V1
            and data[0xC8:0xCA] == b'\xEB\xAD'
        )
        info['is_token_db'] = is_token_db
        self.moniker_records = []
        self.btn_export_index.config(state='disabled')
        self.btn_gallery.config(state='disabled')
        if is_token_db:
            self.moniker_records = scan_token_db_monikers(file_data)
            info['database_kind'] = 'GeoWorks 1.x VM-Token-Datenbank'
            info['geos_name'] = 'GeoWorks Token-Datenbank'
            info['file_type'] = 'VM-Datei / Token-Datenbank'
            info['file_type_id'] = 2
            # Die folgenden Felder sind im TOKEN.DB-Header keine normalen
            # GEO-Anwendungsmetadaten. Nicht als 0.0 oder Fantasietext anzeigen.
            info['version_str'] = ''
            info['release_str'] = ''
            info['protocol_str'] = ''
            info['icon_token'] = ''
            info['creator_token'] = ''
            info['copyright'] = ''
            info['user_notes'] = (
                'GeoWorks-1.x-VM-Datei erkannt.\n'
                'VM-Kennung EB AD bei Offset 0x00C8.\n\n'
                + summarize_token_db_monikers(self.moniker_records)
            )
        # @DIRNAME / @DIRECTO: Dateityp aus DOS-Namen verfeinern
        if dn.startswith('@DIRNAME'):
            info['file_type'] = 'Directory Name (@DIRNAME)'
        elif dn.startswith('@DIRECTO'):
            info['file_type'] = 'Directory Information (@DIRECTO)'

        self.current_info = info
        self.current_path = path

        # Fill fields
        self.fields['path'].set(path)
        self.fields['signature'].set(info.get('signature') or info.get('error', ''))
        self.fields['geos_name'].set(info.get('geos_name', ''))
        self.fields['dos_name'].set(info.get('dos_name', ''))
        self.fields['file_type'].set(info.get('file_type', ''))
        self.fields['version_str'].set(info.get('version_str', ''))
        self.fields['release_str'].set(info.get('release_str', ''))
        self.fields['protocol_str'].set(info.get('protocol_str', ''))
        self.fields['icon_token'].set(info.get('icon_token', ''))
        self.fields['creator_token'].set(info.get('creator_token', ''))
        self.fields['copyright'].set(info.get('copyright', ''))

        self.notes_text.config(state='normal')
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert(tk.END, info.get('user_notes', ''))
        self.notes_text.config(state='disabled')

        # Icon – aus Token-Tabelle (FreeGEOS-Stil) oder Default
        self.icon_image = None
        self.tk_icon = None
        token = info.get('icon_token') or ''
        if info.get('is_token_db'):
            self.icon_label.config(image='', text='TOKEN.DB\nVM-Datenbank', width=18)
            self.icon_info.config(text=f'{len(self.moniker_records)} Moniker gefunden')
            self.btn_save_icon.config(state='disabled')
            self.btn_export_index.config(state='normal' if self.moniker_records else 'disabled')
            self.btn_gallery.config(state='normal' if self.moniker_records else 'disabled')
        elif HAS_PIL:
            self.icon_image = get_token_icon_image(token)
            if self.icon_image:
                self.tk_icon = ImageTk.PhotoImage(self.icon_image)
                self.icon_label.config(image=self.tk_icon, text='')
                src_label = token if token and token in TOKEN_ICONS else 'DEFAULT'
                self.icon_info.config(text=f'Token: {token or "(keiner)"}\n({src_label})')
                self.btn_save_icon.config(state='normal')
            else:
                self.icon_label.config(image='', text='(kein Icon)')
                self.icon_info.config(text='')
                self.btn_save_icon.config(state='disabled')
        else:
            self.btn_export_index.config(state='disabled')
            self.icon_label.config(image='', text='(kein PIL)')
            self.icon_info.config(text=f'Token: {token}')
            self.btn_save_icon.config(state='disabled')

        if info['valid']:
            if info.get('is_token_db'):
                self.status.config(text='OK – TOKEN.DB (GeoWorks 1.x VM-Token-Datenbank)')
            else:
                self.status.config(text=f'OK – {Path(path).name}  (GEOS v{info["version"]})')
            self.title(f'GeoViewPlus – {Path(path).name}')
        else:
            self.status.config(text=f'Keine GEOS-Datei: {info.get("error", "")}')
            messagebox.showwarning('Hinweis', info.get('error', 'Unbekanntes Format'))

    def _moniker_preview_image(self, record, scale=4):
        """Render GeoWorks 1.x 1-bit and 4-bit monikers using the DUMP.GEO palette."""
        if not HAS_PIL:
            return None
        raw = record.get('decoded_data')
        if raw is None:
            return None
        w, h = record['width'], record['height']
        row_mask = (w + 7) // 8
        pixels = []
        alpha = []
        if record['bitmap_type'] == 0x00:
            stride = row_mask
            for y in range(h):
                row = raw[y * stride:(y + 1) * stride]
                for x in range(w):
                    bit = (row[x // 8] >> (7 - (x % 8))) & 1
                    v = 0 if bit else 255
                    pixels.append((v, v, v))
                    alpha.append(255)
        else:
            row_color = (w + 1) // 2
            stride = row_mask + row_color
            for y in range(h):
                row = raw[y * stride:(y + 1) * stride]
                mask = row[:row_mask]
                color = row[row_mask:row_mask + row_color]
                for x in range(w):
                    nibble_byte = color[x // 2]
                    # GeoWorks 1.x DUMP.GEO mapPixels handles the high nibble first.
                    value = (nibble_byte >> 4) & 0x0F if x % 2 == 0 else nibble_byte & 0x0F
                    rgb = GEOWORKS_1X_PALETTE[value]
                    pixels.append(rgb)
                    opaque = (mask[x // 8] >> (7 - (x % 8))) & 1
                    alpha.append(255 if opaque else 0)
        img = Image.new('RGBA', (w, h))
        img.putdata([(r, g, b, a) for (r, g, b), a in zip(pixels, alpha)])
        return img.resize((w * scale, h * scale), Image.Resampling.NEAREST)

    def open_moniker_gallery(self):
        records = getattr(self, 'moniker_records', [])
        if not records:
            messagebox.showinfo('Moniker-Galerie', 'Keine Moniker-Datensätze vorhanden.')
            return
        win = tk.Toplevel(self)
        win.title('GeoViewPlus – TOKEN.DB Moniker-Galerie')
        # Toplevel windows need their own explicit Windows icon assignment.
        try:
            if APP_ICON_PATH.is_file():
                win.iconbitmap(str(APP_ICON_PATH))
        except tk.TclError:
            pass
        win.geometry('900x620')
        win.minsize(700, 480)
        top = ttk.Frame(win, padding=8)
        top.pack(fill=tk.X)
        ttk.Label(top, text=f'{len(records)} validierte Fundstellen').pack(side=tk.LEFT)
        filter_var = tk.StringVar(value='Alle')
        ttk.Label(top, text='Ansicht:').pack(side=tk.LEFT, padx=(18, 4))
        filter_box = ttk.Combobox(top, textvariable=filter_var, state='readonly', width=18,
                                  values=('Alle', 'S/W', 'Farbe', '32×32', '48×30', '64×40', 'Duplikate'))
        filter_box.pack(side=tk.LEFT)
        body = ttk.Panedwindow(win, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        left = ttk.Frame(body)
        right = ttk.Frame(body, padding=10)
        body.add(left, weight=3)
        body.add(right, weight=2)
        cols = ('offset', 'mode', 'size', 'length', 'duplicate')
        tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='browse')
        for col, label, width in [('offset','Dateioffset',105),('mode','Typ',65),('size','Größe',75),('length','Länge',70),('duplicate','Bildinhalt',100)]:
            tree.heading(col, text=label)
            tree.column(col, width=width, anchor='center')
        scroll = ttk.Scrollbar(left, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        preview_label = ttk.Label(right, text='Moniker auswählen', anchor='center')
        preview_label.pack(fill=tk.BOTH, expand=True)
        details = tk.Text(right, height=9, wrap=tk.WORD)
        details.pack(fill=tk.X, pady=(8, 0))
        details.insert('1.0', 'Vorschaubilder sind technische Interpretationen.\nBei Farbmonikern sind Palette und Nibble-Reihenfolge noch nicht abschließend verifiziert.')
        details.config(state='disabled')
        preview_ref = {'image': None}
        digest_counts = Counter(r['decoded_sha256'] for r in records)
        current_rows = {}

        def filtered_records():
            f = filter_var.get()
            out = []
            for r in records:
                is_color = r['type'] == 0x46
                if f == 'S/W' and is_color: continue
                if f == 'Farbe' and not is_color: continue
                if f == '32×32' and (r['width'], r['height']) != (32,32): continue
                if f == '48×30' and (r['width'], r['height']) != (48,30): continue
                if f == '64×40' and (r['width'], r['height']) != (64,40): continue
                if f == 'Duplikate' and digest_counts[r['decoded_sha256']] < 2: continue
                out.append(r)
            return out

        def refresh(*_):
            tree.delete(*tree.get_children())
            current_rows.clear()
            for r in filtered_records():
                iid = f"{r['offset']:06X}"
                mode = 'Farbe' if r['type'] == 0x46 else 'S/W'
                dup = f"{digest_counts[r['decoded_sha256']]}×" if digest_counts[r['decoded_sha256']] > 1 else 'einmalig'
                tree.insert('', tk.END, iid=iid, values=(f"0x{r['offset']:06X}", mode,
                            f"{r['width']}×{r['height']}", f"0x{r['bitmap_length']:04X}", dup))
                current_rows[iid] = r
            preview_label.config(image='', text='Moniker auswählen')
            preview_ref['image'] = None
            details.config(state='normal'); details.delete('1.0', tk.END)
            details.insert('1.0', f'{len(current_rows)} Fundstellen in dieser Ansicht.\nVorschaubilder sind technische Interpretationen; Token-Zuordnung und Farbpalette sind noch nicht verifiziert.')
            details.config(state='disabled')

        def selected(_event=None):
            sel = tree.selection()
            if not sel: return
            r = current_rows.get(sel[0])
            if not r: return
            img = self._moniker_preview_image(r, 4)
            if img is not None:
                photo = ImageTk.PhotoImage(img)
                preview_ref['image'] = photo
                preview_label.config(image=photo, text='')
            else:
                preview_label.config(image='', text='Pillow fehlt – keine Vorschau')
            mode = 'Farbe' if r['type'] == 0x46 else 'S/W'
            info = (f"Offset: 0x{r['offset']:06X}\nTyp: {mode} (0x{r['type']:02X})\n"
                    f"Größe: {r['width']}×{r['height']}\nBitmap-Länge: 0x{r['bitmap_length']:04X}\n"
                    f"Bitmap-Typ: 0x{r['bitmap_type']:02X}\nVorfeld-Differenz: {r['prefix_delta']}\n"
                    f"Identische Bildinhalte: {digest_counts[r['decoded_sha256']]}\n"
                    f"SHA-256 Bilddaten: {r['decoded_sha256']}\n"
                    'Hinweis: Keine Token-/VM-Ressourcenzuordnung nachgewiesen.')
            details.config(state='normal'); details.delete('1.0', tk.END); details.insert('1.0', info); details.config(state='disabled')

        def export_selected():
            sel = tree.selection()
            if not sel: return
            r = current_rows.get(sel[0])
            if not r: return
            img = self._moniker_preview_image(r, 1)
            if img is None:
                messagebox.showerror('PNG-Export', 'Pillow ist nicht verfügbar.', parent=win); return
            path = filedialog.asksaveasfilename(parent=win, title='Moniker-Vorschau als PNG speichern',
                defaultextension='.png', filetypes=[('PNG','*.png')],
                initialfile=f"MONIKER_{r['offset']:06X}.png")
            if path:
                img.save(path)
                self.status.config(text=f'Moniker-Vorschau exportiert: {path}')

        filter_box.bind('<<ComboboxSelected>>', refresh)
        tree.bind('<<TreeviewSelect>>', selected)
        ttk.Button(right, text='Ausgewählten Moniker als PNG speichern…', command=export_selected).pack(fill=tk.X, pady=(8, 0))
        refresh()

    def export_moniker_index(self):
        if not getattr(self, 'moniker_records', None):
            messagebox.showinfo('Moniker-Index', 'Keine Moniker-Kandidaten vorhanden.')
            return
        path = filedialog.asksaveasfilename(
            title='Moniker-Index als CSV speichern',
            defaultextension='.csv',
            filetypes=[('CSV', '*.csv'), ('Alle Dateien', '*.*')],
            initialfile='TOKEN_DB_Moniker_Index.csv'
        )
        if not path:
            return
        columns = ['offset', 'type', 'width', 'height', 'bitmap_length', 'bitmap_type',
                   'prefix_value', 'prefix_delta', 'decoded_length', 'decoded_sha256', 'serialized_sha256']
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=columns, delimiter=';')
                writer.writeheader()
                for record in self.moniker_records:
                    row = dict(record)
                    row['offset'] = f"0x{row['offset']:06X}"
                    row['type'] = f"0x{row['type']:02X}"
                    row['bitmap_type'] = f"0x{row['bitmap_type']:02X}"
                    for key in ('bitmap_length', 'prefix_value'):
                        row[key] = f"0x{row[key]:04X}" if row[key] is not None else ''
                    writer.writerow(row)
            self.status.config(text=f'Moniker-Index exportiert: {path}')
            messagebox.showinfo('Moniker-Index', f'{len(self.moniker_records)} Einträge exportiert.')
        except Exception as e:
            messagebox.showerror('Fehler beim CSV-Export', str(e))

    def save_icon(self):
        if not self.icon_image:
            return
        path = filedialog.asksaveasfilename(
            title='Icon speichern',
            defaultextension='.png',
            filetypes=[('PNG', '*.png'), ('BMP', '*.bmp'), ('Alle', '*.*')]
        )
        if path:
            try:
                self.icon_image.save(path)
                self.status.config(text=f'Icon gespeichert: {path}')
            except Exception as e:
                messagebox.showerror('Fehler', str(e))

    def show_about(self):
        dialog = tk.Toplevel(self)
        dialog.title('Über GeoViewPlus')
        dialog.transient(self)
        dialog.resizable(False, False)

        outer = ttk.Frame(dialog, padding=14)
        outer.pack(fill='both', expand=True)

        content = ttk.Frame(outer)
        content.pack(fill='both', expand=True)

        logo_label = ttk.Label(content)
        logo_label.pack(side='left', padx=(0, 14), anchor='n')

        logo_path = resource_path('JME-Spirallogo.png')
        try:
            if HAS_PIL:
                with Image.open(logo_path) as original:
                    logo = original.convert('RGBA')
                    logo.thumbnail((104, 104), Image.Resampling.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(logo)
            else:
                logo_photo = tk.PhotoImage(file=logo_path)
                # Tkinter's built-in PNG support varies; keep the fallback modest.
                if logo_photo.width() > 104 or logo_photo.height() > 104:
                    factor = max(
                        1,
                        (logo_photo.width() + 103) // 104,
                        (logo_photo.height() + 103) // 104
                    )
                    logo_photo = logo_photo.subsample(factor, factor)
            logo_label.configure(image=logo_photo)
            logo_label.image = logo_photo
            dialog._logo_photo = logo_photo
        except Exception:
            logo_label.configure(text='JME')

        info = ttk.Frame(content)
        info.pack(side='left', fill='both', expand=True)

        ttk.Label(
            info,
            text='GeoViewPlus',
            font=('TkDefaultFont', 15, 'bold')
        ).pack(anchor='w', pady=(0, 7))

        about_text = (
            'GEOS / GeoWorks File Information Viewer\n\n'
            'Erweiterte Neuimplementierung des klassischen\n'
            'GeoView von Rainer Bettsteller (RABE-Soft, 2000/2001).\n\n'
            'Unterstützt GeoWorks 1.x und GEOS 2.x+.\n'
            'Zusätzlich: Icon-Extraktion und -Anzeige.\n\n'
            'Entwickelt zum 25. Geithainer PC/GEOS-Treffen\n'
            '2026 in Syhra.\n\n'
            'Projektleitung und Weiterentwicklung: Johannes Möller\n'
            'KI-Unterstützung: ChatGPT (OpenAI) und Grok (xAI)\n\n'
            'Möllerjaner © 2026 Johannes Möller'
        )
        ttk.Label(
            info,
            text=about_text,
            justify='left',
            anchor='w',
            wraplength=510
        ).pack(anchor='w', fill='x')

        ttk.Button(outer, text='Schließen', command=dialog.destroy).pack(
            anchor='e', pady=(12, 0)
        )
        dialog.update_idletasks()
        dialog.geometry(
            f'+{self.winfo_rootx() + 40}+{self.winfo_rooty() + 40}'
        )



def main():
    initial = sys.argv[1] if len(sys.argv) > 1 else None
    app = GeoViewPlusApp(initial)
    app.mainloop()


if __name__ == '__main__':
    main()
