"""Regression test for geoscore with a real GeoWorks 1.x and/or FreeGEOS installation.

Usage:
    python test_geoscore.py <GeoWorks-1.x folder> [<FreeGEOS folder>]

Example (Windows):
    python test_geoscore.py "%APPDATA%\\freeGEOS\\GEOWORKS" "%APPDATA%\\freeGEOS\\FreeGEOS.281"
"""
import os
import sys

from geoscore import TokenDB, find_token_db, parse_header, classify_geode_icons, moniker_rgba

failures = []


def check(cond, text):
    print(('  OK    ' if cond else '  FEHLER ') + text)
    if not cond:
        failures.append(text)


def find(root, name):
    for dp, _, files in os.walk(root):
        for f in files:
            if f.lower() == name.lower():
                return os.path.join(dp, f)
    return None


def same(a, b):
    return bool(a and b and a.best_icon() and b.best_icon() and a.best_icon().raw == b.best_icon().raw)


def test_install(root, version, app_doc):
    print(f'\n== {root}')
    dbp = find_token_db(root)
    check(dbp is not None, 'Token-Datenbank gefunden')
    if not dbp:
        return
    db = TokenDB(dbp)
    check(db.version == version, f'Token-Datenbank Version {version}')
    check(len(db.entries) > 100, f'{len(db.entries)} Tokens gelesen')
    for app_name, app_tok, doc_tok in app_doc:
        p = find(os.path.join(root, 'WORLD'), app_name) or find(root, app_name)
        if not p:
            print(f'  (übersprungen: {app_name} nicht gefunden)')
            continue
        with open(p, 'rb') as f:
            d = f.read()
        h = parse_header(d)
        check(h is not None and h.version == version, f'{app_name}: Kopf Version {version}')
        check(h.token == app_tok, f'{app_name}: Token {app_tok}')
        gi = classify_geode_icons(d)
        check(gi.app is not None and gi.app.best_icon() is not None, f'{app_name}: App-Icon in der App gefunden')
        check(same(gi.app, db.lookup(app_tok)), f'{app_name}: App-Icon gleich wie in der Token-Datenbank')
        if doc_tok:
            l = gi.for_token(doc_tok)
            check(l is not None, f'{app_name}: Dokument-Icon {doc_tok} in der App gefunden')
            check(same(l, db.lookup(doc_tok)), f'{app_name}: Dokument-Icon gleich wie in der Token-Datenbank')
        w, hh, rgba = moniker_rgba(gi.app.best_icon())
        check(len(rgba) == w * hh * 4, f'{app_name}: Icon {w}×{hh} zeichenbar')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    test_install(sys.argv[1], 1, [('WRITE.GEO', 'WP00', 'WDAT'), ('DRAW.GEO', 'DP00', 'DDAT'),
                                  ('GEOPLAN.GEO', 'PLNR', 'plnr'), ('CALC.GEO', 'CALc', None)])
    if len(sys.argv) > 2:
        test_install(sys.argv[2], 2, [('write.geo', 'WP00', 'WDAT'), ('draw.geo', 'DP00', 'DDAT')])
    print(f'\n{"ALLE TESTS BESTANDEN" if not failures else f"{len(failures)} FEHLER"}')
    sys.exit(1 if failures else 0)
