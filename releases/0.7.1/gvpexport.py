"""Export functions and Windows integration for GeoViewPlus (imported by GeoViewPlus.py)."""
import base64
import csv
import html
import io
import os
import sys

from PIL import Image

CSV_COLUMNS = ['GEOS-Name', 'DOS-Name', 'Ordner', 'Typ', 'GEOS-Version', 'Token', 'Token-Hersteller-ID',
               'Ersteller', 'Ersteller-Hersteller-ID', 'Release', 'Protokoll', 'Größe', 'Erstellt',
               'Geändert', 'Copyright', 'Notizen', 'Icon-Quelle']


def row_for(item, folder_label=''):
    """Flatten one list entry (dict from the main window) to CSV values."""
    h, ln = item.get('header'), item.get('link')
    base = {'GEOS-Name': item['long'], 'DOS-Name': item['name'], 'Ordner': folder_label,
            'Icon-Quelle': item.get('source', '')}
    if item.get('isdir'):
        dn = item.get('dirname')
        base.update({'Typ': 'GEOS-Installation' if item.get('install') else 'Ordner',
                     'Token': dn.token.strip('\0 ') if dn else '',
                     'Token-Hersteller-ID': dn.token_manuf if dn and dn.token.strip('\0 ') else ''})
    elif ln:
        base.update({'Typ': 'Verknüpfung', 'GEOS-Version': '2.x', 'Token': ln.token.strip('\0 '),
                     'Token-Hersteller-ID': ln.token_manuf, 'Ersteller': ln.creator.strip('\0 '),
                     'Ersteller-Hersteller-ID': ln.creator_manuf if ln.creator.strip('\0 ') else '',
                     'Notizen': 'Ziel: ' + ln.target_text()})
    elif h:
        base.update({'Typ': h.kind_name, 'GEOS-Version': f'{h.version}.x', 'Token': h.token.strip('\0 '),
                     'Token-Hersteller-ID': h.token_manuf, 'Ersteller': h.creator.strip('\0 '),
                     'Ersteller-Hersteller-ID': h.creator_manuf if h.creator.strip('\0 ') else '',
                     'Release': h.release_str, 'Protokoll': h.protocol_str, 'Erstellt': h.created,
                     'Copyright': h.notice, 'Notizen': h.notes.replace('\r', ' ').replace('\n', ' ')})
    else:
        base['Typ'] = 'DOS-Datei'
    if 'size' in item:
        base['Größe'] = item['size']
    if 'mtime' in item:
        import time
        base['Geändert'] = time.strftime('%d.%m.%Y %H:%M', time.localtime(item['mtime']))
    return [base.get(c, '') for c in CSV_COLUMNS]


def write_csv(path, rows):
    """Semicolon CSV, UTF-8 with BOM so Excel shows umlauts correctly."""
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(CSV_COLUMNS)
        w.writerows(rows)


def png_b64(img):
    b = io.BytesIO()
    img.save(b, 'PNG')
    return base64.b64encode(b.getvalue()).decode()


HTML_CSS = """body{font:13px Segoe UI,Arial,sans-serif;margin:24px;color:#222;background:#f4f4f2}
h1{font-size:19px;margin:0 0 4px}p.sub{color:#555;margin:0 0 14px}
table{border-collapse:collapse;background:#fff;width:100%}
th,td{padding:4px 8px;border-bottom:1px solid #e3e3e0;text-align:left;vertical-align:middle}
th{background:#e9e9e5;font-weight:600}td.ic{width:60px;text-align:center;background:#c0c0c0}
td.ic img{image-rendering:pixelated}.mono{font-family:Consolas,monospace;font-size:12px}
.small{color:#666;font-size:11px}"""


def write_html(path, title, subtitle, entries):
    """entries: [(PIL image or None, csv row list)]"""
    show = ['GEOS-Name', 'DOS-Name', 'Ordner', 'Typ', 'Token', 'Ersteller', 'Release', 'Protokoll',
            'Größe', 'Geändert', 'Copyright']
    idx = [CSV_COLUMNS.index(c) for c in show]
    with_folder = any(r[2] for _, r in entries)
    if not with_folder:
        show.remove('Ordner')
        idx.remove(2)
    out = [f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
           f'<style>{HTML_CSS}</style></head><body><h1>{html.escape(title)}</h1>'
           f'<p class="sub">{html.escape(subtitle)}</p><table><tr><th>Icon</th>'
           + ''.join(f'<th>{html.escape(c)}</th>' for c in show) + '</tr>']
    for img, r in entries:
        cell = f'<img src="data:image/png;base64,{png_b64(img)}">' if img is not None else ''
        tds = []
        for c, i in zip(show, idx):
            v = r[i]
            if c == 'Token' and v != '':
                v = f'{v}/{r[i + 1]}'
            if c == 'Ersteller' and v != '':
                v = f'{v}/{r[i + 1]}'
            if c == 'Größe' and v != '':
                v = f'{v:,}'.replace(',', '.')
            cls = ' class="mono"' if c in ('DOS-Name', 'Token', 'Ersteller', 'Release', 'Protokoll', 'Größe') \
                else ' class="small"' if c == 'Copyright' else ''
            text = f'<b>{html.escape(str(v))}</b>' if c == 'GEOS-Name' else html.escape(str(v))
            tds.append(f'<td{cls}>{text}</td>')
        out.append(f'<tr><td class="ic">{cell}</td>' + ''.join(tds) + '</tr>')
    out.append('</table><p class="small">Erstellt mit GeoViewPlus</p></body></html>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))


def save_ico(img, path):
    """Save an icon centred on a square canvas as .ico (16–64 px)."""
    side = max(img.width, img.height)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    if side < 16:
        f = -(-16 // side)
        sq = sq.resize((side * f, side * f), Image.NEAREST)
        side *= f
    sq.save(path, sizes=[(s, s) for s in (16, 32, 48, 64) if s <= side] or [(side, side)])


def safe_token_name(token, manuf):
    """File name for a token that stays unique on case-insensitive Windows file systems."""
    raw = token.encode('latin-1', 'replace')
    readable = ''.join(c if c.isalnum() else '_' for c in token)
    return f'{readable}-{raw.hex().upper()}_{manuf}'


def export_tokendb(db, folder, moniker_image, ico=True, all_variants=False, progress=None):
    """Write icons of every token as PNG (and ICO) plus index.csv / index.html. Returns count."""
    os.makedirs(folder, exist_ok=True)
    rows, entries = [], []
    items = sorted(db.entries.values(), key=lambda e: (e.token.lower(), e.manuf))
    n = 0
    for k, e in enumerate(items):
        best = e.best_icon(prefer=(1, 2, 0, 3))
        if not best:
            continue
        base = safe_token_name(e.token, e.manuf)
        img = moniker_image(best)
        img.save(os.path.join(folder, base + '.png'))
        if ico:
            save_ico(img, os.path.join(folder, base + '.ico'))
        if all_variants:
            for m in e.monikers:
                if m.is_graphic and not m.blank:
                    w, h, fmt = m.bitmap[0], m.bitmap[1], m.bitmap[2]
                    moniker_image(m).save(os.path.join(folder, f'{base}_{w}x{h}_{["sw", "16", "256", "24"][fmt]}.png'))
        rows.append([e.token, e.manuf, e.name(), base + '.png', best.describe()])
        entries.append((img, e.token, e.manuf, e.name(), base + '.png', best.describe()))
        n += 1
        if progress and k % 25 == 0:
            progress(k, len(items))
    with open(os.path.join(folder, 'index.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['Token', 'Hersteller-ID', 'Name', 'Datei', 'Icon'])
        w.writerows(rows)
    out = ['<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>Icons der Token-Datenbank</title>'
           f'<style>{HTML_CSS}</style></head><body><h1>Icons der Token-Datenbank</h1>'
           f'<p class="sub">{html.escape(db.path)} · {n} Tokens</p><table><tr><th>Icon</th><th>Token</th>'
           '<th>Hersteller-ID</th><th>Name</th><th>Datei</th><th>Icon-Variante</th></tr>']
    for img, tok, manuf, name, fname, desc in entries:
        out.append(f'<tr><td class="ic"><img src="{html.escape(fname)}"></td><td class="mono">{html.escape(tok)}</td>'
                   f'<td class="mono">{manuf}</td><td><b>{html.escape(name or "–")}</b></td>'
                   f'<td class="mono">{html.escape(fname)}</td><td class="small">{html.escape(desc)}</td></tr>')
    out.append('</table><p class="small">Erstellt mit GeoViewPlus</p></body></html>')
    with open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    return n

# ---------------------------------------------------------------------------
# Windows Explorer context menu (current user only, HKCU)
# ---------------------------------------------------------------------------

CONTEXT_KEYS = [r'Software\Classes\Directory\shell\GeoViewPlus'] + [
    rf'Software\Classes\SystemFileAssociations\{ext}\shell\GeoViewPlus'
    for ext in ('.geo', '.000', '.001', '.002', '.003', '.db', '.vm')]


def launch_command():
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}" "%1"', sys.executable
    exe = sys.executable
    pyw = os.path.join(os.path.dirname(exe), 'pythonw.exe')
    exe = pyw if os.path.isfile(pyw) else exe
    script = os.path.abspath(sys.argv[0])
    return f'"{exe}" "{script}" "%1"', exe


def register_context_menu():
    import winreg
    cmd, icon = launch_command()
    for key in CONTEXT_KEYS:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key) as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, 'Mit GeoViewPlus öffnen')
            winreg.SetValueEx(k, 'Icon', 0, winreg.REG_SZ, icon)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key + r'\command') as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, cmd)


def unregister_context_menu():
    import winreg
    for key in CONTEXT_KEYS:
        for sub in (key + r'\command', key):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
            except OSError:
                pass


def context_menu_registered():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CONTEXT_KEYS[0]):
            return True
    except (ImportError, OSError):
        return False
