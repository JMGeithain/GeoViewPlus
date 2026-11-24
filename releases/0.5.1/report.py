"""HTML overview of GEOS files with icons (GeoViewPlus prototype).

Icon order:
  apps:      icon inside the app  ->  token database  ->  standard icon
  documents: document icon inside the creating app  ->  token database  ->  standard icon
"""
import base64, html, io, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from geoscore import (TokenDB, parse_header, moniker_rgba, classify_geode_icons)

FALLBACK = {'Programm (Geode)': 'gAPP', 'Dokument (VM-Datei)': 'gDAT', 'Daten-Datei': 'FILE'}


class AppIndex:
    """Token -> application file, built by scanning folder trees once."""

    def __init__(self, roots):
        self.apps = {}
        self._cache = {}
        for root in roots:
            for dp, _, files in os.walk(root):
                for n in files:
                    if n.lower().endswith('.geo'):
                        p = os.path.join(dp, n)
                        with open(p, 'rb') as f:
                            h = parse_header(f.read(0x100))
                        if h and h.type_name.startswith('Programm'):
                            self.apps.setdefault((h.token, h.token_manuf), p)

    def icons(self, path):
        if path not in self._cache:
            with open(path, 'rb') as f:
                self._cache[path] = classify_geode_icons(f.read())
        return self._cache[path]


def to_png(mon):
    w, h, rgba = moniker_rgba(mon)
    b = io.BytesIO()
    Image.frombytes('RGBA', (w, h), rgba).save(b, 'PNG')
    return base64.b64encode(b.getvalue()).decode()


def resolve_icon(path, h, db, idx):
    """Return (moniker, source text)."""
    if h.type_name.startswith('Programm'):
        gi = idx.icons(path)
        if gi.app and gi.app.best_icon():
            return gi.app.best_icon(), 'aus der App selbst'
    else:
        app = idx.apps.get((h.creator, h.creator_manuf))
        if app:
            gi = idx.icons(app)
            l = gi.for_token(h.token, h.token_manuf)
            if l and l.best_icon():
                return l.best_icon(), f'Dokument-Icon aus {os.path.basename(app)}'
    e = db.lookup(h.token, h.token_manuf) if h.token.strip('\0 ') else None
    if e and e.best_icon():
        return e.best_icon(), 'aus der Token-Datenbank'
    e = db.lookup(FALLBACK.get(h.type_name, 'FILE'))
    return (e.best_icon() if e else None), 'Standard-Icon'


def rows_for(folder, db, idx):
    out = []
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name)
        if not os.path.isfile(p):
            continue
        with open(p, 'rb') as f:
            h = parse_header(f.read(0x100))
        if not h:
            continue
        mon, src = resolve_icon(p, h, db, idx)
        out.append((name, h, to_png(mon) if mon else None, src, mon.describe() if mon else '',
                    os.path.getsize(p)))
    return out


CSS = """body{font:13px Segoe UI,Arial,sans-serif;margin:24px;color:#222;background:#f4f4f2}
h1{font-size:20px;margin:0 0 4px}h2{font-size:15px;margin:28px 0 8px}
p.sub{color:#555;margin:0 0 16px;max-width:900px}table{border-collapse:collapse;background:#fff;width:100%}
th,td{padding:4px 8px;border-bottom:1px solid #e3e3e0;text-align:left;vertical-align:middle}
th{background:#e9e9e5;font-weight:600}
td.ic{width:72px;text-align:center;background:#c0c0c0}td.ic img{image-rendering:pixelated}
.v1{color:#7a3e00}.v2{color:#00507a}.mono{font-family:Consolas,monospace;font-size:12px}
.src{font-size:11px;color:#2c6e2c}.src.db{color:#555}.src.std{color:#a00}.small{color:#666;font-size:11px}"""


def build(sections, out):
    parts = [f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>GeoViewPlus – Prototyp</title><style>{CSS}</style></head><body>',
             '<h1>GeoViewPlus – Prototyp der Kernlogik</h1>',
             '<p class="sub">App-Icons werden aus der App selbst gelesen, Dokument-Icons aus der App, die das Dokument erzeugt hat '
             '(Ersteller-Token im Dokumentkopf). Nur wenn das nicht geht, wird die Token-Datenbank und zuletzt ein Standard-Icon verwendet.</p>']
    for title, rows in sections:
        parts.append(f'<h2>{html.escape(title)}</h2><table><tr><th>Icon</th><th>DOS-Name</th><th>GEOS-Name / Icon-Quelle</th><th>Typ</th>'
                     '<th>Token</th><th>Ersteller</th><th>Release</th><th>Protokoll</th><th>Größe</th><th>Copyright</th></tr>')
        for name, h, png, src, desc, size in rows:
            img = f'<img src="data:image/png;base64,{png}" title="{html.escape(desc)}">' if png else ''
            cls = 'src' + (' db' if 'Datenbank' in src else ' std' if 'Standard' in src else '')
            size_s = f'{size:,}'.replace(',', '.')
            parts.append(
                f'<tr><td class="ic">{img}</td><td class="mono">{html.escape(name)}</td>'
                f'<td><b>{html.escape(h.long_name)}</b><div class="{cls}">{html.escape(src)}</div></td>'
                f'<td><span class="v{h.version}">{h.version}.x</span> · {html.escape(h.type_name)}</td>'
                f'<td class="mono">{html.escape(h.token)}/{h.token_manuf}</td>'
                f'<td class="mono">{html.escape(h.creator.strip(chr(0)))}/{h.creator_manuf}</td>'
                f'<td class="mono">{h.release_str}</td><td class="mono">{h.protocol_str}</td>'
                f'<td class="mono">{size_s}</td><td class="small">{html.escape(h.notice)}</td></tr>')
        parts.append('</table>')
    parts.append('</body></html>')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))


if __name__ == '__main__':
    up = '/mnt/user-data/uploads'
    db1 = TokenDB(f'{up}/GEOWORKS/SYSTEM/TOKEN.DB')
    db2 = TokenDB(f'{up}/FreeGEOS.281/privdata/token_da.000')
    idx1 = AppIndex([f'{up}/GEOWORKS'])
    idx2 = AppIndex([f'{up}/FreeGEOS.281'])
    build([
        ('GeoWorks 1.28 – WORLD', rows_for(f'{up}/GEOWORKS/WORLD', db1, idx1)),
        ('GeoWorks 1.28 – DOCUMENT (Auswahl)', rows_for(f'{up}/GEOWORKS/DOCUMENT', db1, idx1)),
        ('FreeGEOS 2.81 – WORLD', rows_for(f'{up}/FreeGEOS.281/world', db2, idx2)),
        ('FreeGEOS 2.81 – DOCUMENT', rows_for(f'{up}/FreeGEOS.281/document', db2, idx2)),
    ], sys.argv[1] if len(sys.argv) > 1 else 'GeoViewPlus_Prototyp.html')
