"""GeoViewPlus – GEOS / GeoWorks File Information Viewer for Windows.

Shows long names, header data and icons of GEOS files from GeoWorks 1.x,
GEOS 2.x (Ensemble, NewDeal, Breadbox) and FreeGEOS.

Icon sources, in this order:
  applications: the icon stored in the application itself
  documents:    the document icon stored in the creating application
  then:         the token database (TOKEN.DB / TOKEN_DA.000)
  last:         a standard icon

Idea: GeoView by Rainer Bettsteller (RABE-Soft, 2000).
Möllerjaner © 2026 Johannes Möller
"""
from __future__ import annotations

import os
import sys
import threading
from collections import deque
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk

from geoscore import (TokenDB, parse_header, moniker_rgba, classify_geode_icons,
                      find_token_db, SIG_V1, read_dirname, read_dirinfo, match_positions,
                      find_case, STANDARD_PATHS, geode_info, SearchQuery, search)

ADMIN_FILES = ('@DIRNAME.000', '@DIRECTO.000')

APP_NAME = 'GeoViewPlus'
APP_VERSION = '0.6.0'
LIST_ICON_H = 32           # row height in the file list
FALLBACK = {'Programm (Geode)': 'gAPP', 'Dokument (VM-Datei)': 'gDAT',
            'Daten-Datei': 'FILE', 'Verzeichnis': 'FLDR'}


def resource_path(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def moniker_image(mon, scale=1):
    w, h, rgba = moniker_rgba(mon)
    img = Image.frombytes('RGBA', (w, h), rgba)
    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    return img


def fit_row(img, height=LIST_ICON_H, width=52):
    """Center an icon in a fixed cell so the list stays aligned."""
    cell = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    if img.height > height or img.width > width:
        img = img.copy()
        img.thumbnail((width, height), Image.NEAREST)
    cell.paste(img, ((width - img.width) // 2, (height - img.height) // 2), img)
    return cell


def builtin_icon(kind):
    """Small drawn icons for when no token database is available."""
    from PIL import ImageDraw
    img = Image.new('RGBA', (48, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if kind == 'folder':
        d.rectangle((6, 6, 20, 10), fill=(255, 255, 85), outline=(0, 0, 0))
        d.rectangle((6, 9, 41, 27), fill=(255, 255, 85), outline=(0, 0, 0))
    elif kind == 'install':
        d.rectangle((6, 6, 20, 10), fill=(85, 255, 255), outline=(0, 0, 0))
        d.rectangle((6, 9, 41, 27), fill=(85, 255, 255), outline=(0, 0, 0))
        d.text((15, 12), 'GEOS', fill=(0, 0, 170))
    else:
        d.polygon([(14, 2), (30, 2), (36, 8), (36, 28), (14, 28)], fill=(255, 255, 255), outline=(0, 0, 0))
        d.line([(30, 2), (30, 8), (36, 8)], fill=(0, 0, 0))
    return img


def install_kind(folder):
    """'GeoWorks 1.x' / 'GEOS 2.x / FreeGEOS' if folder is a GEOS installation."""
    db = find_token_db(folder)
    if not db:
        return None
    return 'GeoWorks 1.x' if read_head(db, 4) == SIG_V1 else 'GEOS 2.x / FreeGEOS'


def read_head(path, n=0x100):
    try:
        with open(path, 'rb') as f:
            return f.read(n)
    except OSError:
        return b''


def fmt_size(n):
    return f'{n:,}'.replace(',', '.') + ' Bytes'


def fmt_mtime(t):
    return time.strftime('%d.%m.%Y %H:%M', time.localtime(t))

# ---------------------------------------------------------------------------
# Installation context: token database + application index
# ---------------------------------------------------------------------------


class GeosContext:
    """Everything that belongs to one GEOS installation."""

    def __init__(self):
        self.root = None
        self.tokendb = None
        self.tokendb_path = None
        self.apps = {}              # (token, manuf) -> path of application
        self._icons = {}            # app path -> GeodeIcons
        self._key = None
        self.generation = 0
        self.index_done = False

    @staticmethod
    def find_root(folder):
        """Walk up from folder to the installation root."""
        cur = os.path.abspath(folder)
        while True:
            if find_token_db(cur) or os.path.isfile(os.path.join(cur, 'GEOS.INI')) \
                    or os.path.isfile(os.path.join(cur, 'geos.ini')):
                return cur
            parent = os.path.dirname(cur)
            if parent == cur:
                return None
            cur = parent

    def open_for(self, folder):
        """Switch to the installation of folder. Returns True if it changed.

        Only the token database is loaded here; the application index is
        built afterwards in a background thread (start_index).
        """
        root = self.find_root(folder)
        key = root or ('folder', os.path.abspath(folder))
        if key == self._key:
            return False
        self._key = key
        self.root = root
        self.generation += 1
        self.apps = {}
        self._icons = {}
        self.index_done = False
        self.load_tokendb(find_token_db(root) if root else None)
        return True

    def index_dirs(self, folder):
        """Folders searched for applications.

        In an installation: only its WORLD folder (apps live there).
        Outside an installation: only the opened folder itself, not recursive,
        so a parent folder with many installations is never scanned.
        """
        if self.root:
            for n in os.listdir(self.root):
                if n.upper() == 'WORLD' and os.path.isdir(os.path.join(self.root, n)):
                    return [(os.path.join(self.root, n), True)]
            return [(self.root, False)]
        return [(os.path.abspath(folder), False)]

    def build_index(self, folder, generation, progress=None):
        """Runs in a background thread. Must not touch Tk."""
        apps = {}
        n = 0
        for top, recursive in self.index_dirs(folder):
            walker = os.walk(top) if recursive else [(top, [], os.listdir(top))]
            for dp, dirs, files in walker:
                for name in files:
                    if generation != self.generation:
                        return
                    if name.lower().endswith('.geo'):
                        p = os.path.join(dp, name)
                        if os.path.isfile(p):
                            h = parse_header(read_head(p))
                            if h and h.type_name.startswith('Programm'):
                                apps.setdefault((h.token, h.token_manuf), p)
                        n += 1
                        if progress and n % 50 == 0:
                            progress(n)
        if generation == self.generation:
            self.apps = apps
            self.index_done = True

    def load_tokendb(self, path):
        self.tokendb, self.tokendb_path = None, None
        if path:
            try:
                self.tokendb = TokenDB(path)
                self.tokendb_path = path
            except Exception:
                pass

    def geode_icons(self, path):
        if path not in self._icons:
            try:
                with open(path, 'rb') as f:
                    self._icons[path] = classify_geode_icons(f.read())
            except Exception:
                self._icons[path] = None
        return self._icons[path]

    def resolve(self, path, h):
        """Return (icon list or token entry, moniker list owner text, source)."""
        if h.type_name.startswith('Programm'):
            gi = self.geode_icons(path)
            if gi and gi.app and gi.app.best_icon():
                return gi.app, 'aus der App selbst'
        elif h.creator.strip('\0 '):
            app = self.apps.get((h.creator, h.creator_manuf)) or next(
                (p for (t, m), p in self.apps.items() if t == h.creator), None)
            if app:
                gi = self.geode_icons(app)
                l = gi.for_token(h.token, h.token_manuf) if gi else None
                if l and l.best_icon():
                    return l, f'Dokument-Icon aus {os.path.basename(app)}'
        if self.tokendb and h.token.strip('\0 '):
            e = self.tokendb.lookup(h.token, h.token_manuf)
            if e and e.best_icon():
                return e, 'aus der Token-Datenbank'
        return self.standard(h.type_name), 'Standard-Icon'

    def resolve_link(self, ln):
        """Icon of a link: the target app, else the token database."""
        app = self.apps.get((ln.token, ln.token_manuf))
        if app and not ln.is_dir:
            gi = self.geode_icons(app)
            if gi and gi.app and gi.app.best_icon():
                return gi.app, f'aus {os.path.basename(app)}'
        if self.tokendb and ln.token.strip('\0 '):
            e = self.tokendb.lookup(ln.token, ln.token_manuf)
            if e and e.best_icon():
                return e, 'aus der Token-Datenbank'
        return self.standard('Verzeichnis' if ln.is_dir else 'Daten-Datei'), 'Standard-Icon'

    def link_target(self, ln):
        """Host path of a link target, or None (e.g. drive links inside the emulator)."""
        if ln.std_path is None or not self.root or ln.std_path not in STANDARD_PATHS:
            return None
        cur = self.root
        for part in STANDARD_PATHS[ln.std_path].split('/'):
            if part:
                cur = find_case(cur, part)
                if not cur:
                    return None
        for part in [x for x in ln.path.split('\\') if x and x != '.']:
            nxt = find_case(cur, part)
            if not nxt and os.path.isdir(cur):          # match GEOS long names
                for n in os.listdir(cur):
                    q = os.path.join(cur, n)
                    if os.path.isdir(q):
                        dn = read_dirname(q)
                        name = dn.long_name if dn else ''
                    else:
                        h = parse_header(read_head(q))
                        name = h.long_name if h else ''
                    if name == part:
                        nxt = q
                        break
            if not nxt:
                return None
            cur = nxt
        return cur

    def standard(self, type_name):
        if self.tokendb:
            e = self.tokendb.lookup(FALLBACK.get(type_name, 'FILE'))
            if e and e.best_icon():
                return e
        return None

# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------


class GeoViewPlus(tk.Tk):
    COLUMNS = (('dos', 'DOS-Name', 110), ('type', 'Typ', 150), ('token', 'Token', 80),
               ('creator', 'Ersteller', 80), ('size', 'Größe', 90), ('mtime', 'Geändert', 115))

    def __init__(self, start=None):
        super().__init__()
        self.title(f'{APP_NAME} {APP_VERSION}')
        self.geometry('1180x720')
        self.minsize(900, 520)
        try:
            self.iconbitmap(resource_path('geoworks_motif_icon.ico'))
        except Exception:
            pass
        self.ctx = GeosContext()
        self.folder = None
        self.items = {}             # tree iid -> dict
        self._img_refs = {}         # keep PhotoImages alive
        self._detail_imgs = []
        self._pending = []
        self.only_geos = tk.BooleanVar(value=True)
        self.show_admin = tk.BooleanVar(value=False)
        self._build_menu()
        self._build_ui()
        if start:
            self.after(50, lambda: self.open_path(start))

    # ---------------- UI construction ----------------
    def _build_menu(self):
        m = tk.Menu(self)
        f = tk.Menu(m, tearoff=False)
        f.add_command(label='Ordner öffnen …', accelerator='Strg+O', command=self.ask_folder)
        f.add_command(label='Datei öffnen …', command=self.ask_file)
        f.add_separator()
        f.add_command(label='Token-Datenbank wählen …', command=self.ask_tokendb)
        f.add_separator()
        f.add_command(label='Beenden', command=self.destroy)
        m.add_cascade(label='Datei', menu=f)
        v = tk.Menu(m, tearoff=False)
        v.add_checkbutton(label='Nur GEOS-Dateien anzeigen', variable=self.only_geos,
                          command=self.refresh)
        v.add_checkbutton(label='Verwaltungsdateien (@DIRNAME, @DIRECTO) anzeigen',
                          variable=self.show_admin, command=self.refresh)
        v.add_command(label='Aktualisieren', accelerator='F5', command=self.refresh)
        m.add_cascade(label='Ansicht', menu=v)
        x = tk.Menu(m, tearoff=False)
        x.add_command(label='Suchen …', accelerator='Strg+F', command=self.open_search)
        x.add_command(label='Token-Datenbank durchsehen …', command=self.show_tokendb)
        m.add_cascade(label='Extras', menu=x)
        h = tk.Menu(m, tearoff=False)
        h.add_command(label=f'Über {APP_NAME} …', command=self.show_about)
        m.add_cascade(label='Hilfe', menu=h)
        self.config(menu=m)
        self.bind('<Control-o>', lambda e: self.ask_folder())
        self.bind('<F5>', lambda e: self.refresh())
        self.bind('<Control-f>', lambda e: self.open_search())

    def _build_ui(self):
        style = ttk.Style(self)
        style.configure('Files.Treeview', rowheight=LIST_ICON_H + 4)
        style.configure('Big.TLabel', font=('Segoe UI', 13, 'bold'))
        style.configure('Head.TLabel', foreground='#555')

        top = ttk.Frame(self, padding=(8, 6))
        top.pack(fill='x')
        ttk.Button(top, text='Ordner öffnen …', command=self.ask_folder).pack(side='left')
        ttk.Button(top, text='▲ übergeordnet', command=self.go_up).pack(side='left', padx=(6, 0))
        ttk.Button(top, text='Suchen …', command=self.open_search).pack(side='right', padx=(6, 0))
        self.path_var = tk.StringVar()
        e = ttk.Entry(top, textvariable=self.path_var)
        e.pack(side='left', fill='x', expand=True, padx=8)
        e.bind('<Return>', lambda ev: self.open_path(self.path_var.get()))

        pane = ttk.PanedWindow(self, orient='horizontal')
        pane.pack(fill='both', expand=True, padx=8, pady=(0, 4))

        left = ttk.Frame(pane)
        self.tree = ttk.Treeview(left, style='Files.Treeview',
                                 columns=[c[0] for c in self.COLUMNS], selectmode='browse')
        self.tree.heading('#0', text='GEOS-Name', command=lambda: self.sort_by('#0'))
        self.tree.column('#0', width=300, minwidth=180)
        for key, title, width in self.COLUMNS:
            self.tree.heading(key, text=title, command=lambda k=key: self.sort_by(k))
            self.tree.column(key, width=width, minwidth=50,
                             anchor='e' if key == 'size' else 'w')
        sb = ttk.Scrollbar(left, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='left', fill='y')
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.show_detail())
        self.tree.bind('<Double-1>', self.on_double)
        self.tree.bind('<Return>', self.on_double)
        self.tree.bind('<BackSpace>', lambda e: self.go_up())
        pane.add(left, weight=3)

        right = ttk.Frame(pane, padding=(10, 0, 0, 0))
        pane.add(right, weight=2)
        self._build_detail(right)
        self.after(100, lambda: pane.sashpos(0, int(self.winfo_width() * 0.58)))

        self.status = tk.StringVar(value='Bitte einen Ordner öffnen.')
        ttk.Label(self, textvariable=self.status, relief='sunken', anchor='w',
                  padding=(6, 2)).pack(fill='x', side='bottom')

    def _build_detail(self, parent):
        head = ttk.Frame(parent)
        head.pack(fill='x', pady=(4, 8))
        self.big_icon = tk.Label(head, bg='#c0c0c0', width=140, height=88, bd=1, relief='sunken')
        self.big_icon.pack(side='left')
        hd = ttk.Frame(head, padding=(10, 0, 0, 0))
        hd.pack(side='left', fill='both', expand=True)
        self.d_name = ttk.Label(hd, text='', style='Big.TLabel', wraplength=300)
        self.d_name.pack(anchor='w')
        self.d_src = ttk.Label(hd, text='', foreground='#2c6e2c', wraplength=300)
        self.d_src.pack(anchor='w', pady=(4, 0))
        self.d_buttons = ttk.Frame(hd)
        self.d_buttons.pack(anchor='w', pady=(6, 0))

        grid = ttk.Frame(parent)
        grid.pack(fill='x')
        self.fields = {}
        self.field_labels = {}
        rows = ['Pfad', 'DOS-Name', 'Datei-Typ', 'GEOS-Version', 'Token', 'Ersteller',
                'Release', 'Protokoll', 'Größe', 'Erstellt', 'Letzte Änderung', 'Copyright',
                'Interner Name', 'Eigenschaften', 'Bibliotheken', 'Dokumentarten', 'Erzeugt von']
        for i, r in enumerate(rows):
            lab = ttk.Label(grid, text=r + ':', style='Head.TLabel')
            lab.grid(row=i, column=0, sticky='ne', padx=(0, 8))
            self.field_labels[r] = lab
            v = ttk.Label(grid, text='', wraplength=330, justify='left')
            v.grid(row=i, column=1, sticky='nw')
            self.fields[r] = v
        grid.columnconfigure(1, weight=1)

        self.notes_label = ttk.Label(parent, text='Datei-Notizen:', style='Head.TLabel')
        self.notes_label.pack(anchor='w', pady=(8, 0))
        self.notes = tk.Text(parent, height=4, wrap='word', relief='flat', bg='#ececec',
                             font=('Segoe UI', 9))
        self.notes.pack(fill='x')
        self.notes.configure(state='disabled')

        bar = ttk.Frame(parent)
        bar.pack(fill='x', pady=(8, 2))
        ttk.Label(bar, text='Icon-Varianten:', style='Head.TLabel').pack(side='left')
        ttk.Button(bar, text='Als ICO …', command=lambda: self.save_icon('ico')).pack(side='right')
        ttk.Button(bar, text='Als PNG …', command=lambda: self.save_icon('png')).pack(side='right', padx=4)

        gal = ttk.Frame(parent)
        gal.pack(fill='both', expand=True)
        self.gallery = tk.Canvas(gal, bg='#c0c0c0', highlightthickness=0, height=150)
        gsb = ttk.Scrollbar(gal, orient='vertical', command=self.gallery.yview)
        self.gallery.configure(yscrollcommand=gsb.set)
        self.gallery.pack(side='left', fill='both', expand=True)
        gsb.pack(side='left', fill='y')
        self.gallery.bind('<Configure>', lambda e: self._layout_gallery())
        self._gallery_items = []
        self.selected_moniker = None

    # ---------------- navigation ----------------
    def ask_folder(self):
        d = filedialog.askdirectory(title='GEOS-Ordner öffnen', initialdir=self.folder or None)
        if d:
            self.open_path(d)

    def ask_file(self):
        f = filedialog.askopenfilename(title='GEOS-Datei öffnen', initialdir=self.folder or None,
                                       filetypes=[('GEOS-Dateien', '*.GEO *.000 *.001 *.002 *.DB *.VM'),
                                                  ('Alle Dateien', '*.*')])
        if f:
            self.open_path(f)

    def ask_tokendb(self):
        f = filedialog.askopenfilename(title='Token-Datenbank wählen',
                                       filetypes=[('Token-Datenbank', 'TOKEN.DB TOKEN_DA.000 *.DB *.000'),
                                                  ('Alle Dateien', '*.*')])
        if f:
            self.ctx.load_tokendb(f)
            if not self.ctx.tokendb:
                messagebox.showerror(APP_NAME, 'Diese Datei ist keine lesbare Token-Datenbank.')
            self.refresh()

    def go_up(self):
        if self.folder:
            parent = os.path.dirname(self.folder)
            if parent != self.folder:
                self.open_path(parent, select=self.folder)

    def on_double(self, event=None):
        sel = self.tree.selection()
        if sel:
            it = self.items.get(sel[0])
            if it and it['isdir']:
                self.open_path(it['path'])
            elif it and it.get('link'):
                target = self.ctx.link_target(it['link'])
                if target:
                    self.open_path(target)
                else:
                    messagebox.showinfo(APP_NAME, f'Das Ziel „{it["link"].target_text()}“ liegt außerhalb '
                                        'der Installation (z. B. ein Laufwerk im Emulator) und kann hier '
                                        'nicht geöffnet werden.')

    def open_path(self, path, select=None):
        path = os.path.abspath(path.strip().strip('"'))
        if os.path.isfile(path):
            select = path
            path = os.path.dirname(path)
        if not os.path.isdir(path):
            messagebox.showerror(APP_NAME, f'Ordner nicht gefunden:\n{path}')
            return
        self.folder = path
        self.path_var.set(path)
        if self.ctx.open_for(path):
            self._start_index(path)
        self.refresh(select)

    def _start_index(self, folder):
        """Build the application index without blocking the window."""
        gen = self.ctx.generation
        self._index_count = 0

        def progress(n):
            self._index_count = n

        t = threading.Thread(target=self.ctx.build_index, args=(folder, gen, progress), daemon=True)
        t.start()
        self._watch_index(t, gen)

    def _watch_index(self, thread, gen):
        if gen != self.ctx.generation:
            return
        if thread.is_alive():
            self.status_extra = f'Suche Apps … {self._index_count} gefunden'
            self._update_status()
            self.after(200, lambda: self._watch_index(thread, gen))
            return
        self.status_extra = ''
        # Documents may now get their icon from the creating app
        for iid, it in self.items.items():
            if not it['isdir'] and it.get('header') and it.get('source') != 'aus der App selbst':
                it.pop('source', None)
                if iid not in self._pending:
                    self._pending.append(iid)
        self._update_status()
        self.after(1, self._load_icons)

    # ---------------- listing ----------------
    def refresh(self, select=None):
        if not self.folder:
            return
        self.tree.delete(*self.tree.get_children())
        self.items.clear()
        self._img_refs.clear()
        self._pending.clear()
        try:
            names = os.listdir(self.folder)
        except OSError as ex:
            messagebox.showerror(APP_NAME, str(ex))
            return
        dirs, files = [], []
        for n in names:
            p = os.path.join(self.folder, n)
            (dirs if os.path.isdir(p) else files).append((n, p))
        n_geos = 0
        for n, p in sorted(dirs, key=lambda x: x[0].lower()):
            dn = read_dirname(p)
            long_name = dn.long_name if dn and dn.long_name else n
            ftok = dn.token.strip('\0 ') if dn else ''
            kind = install_kind(p)
            typ = f'GEOS-Installation ({kind})' if kind else 'Ordner'
            iid = self.tree.insert('', 'end', text='  ' + long_name,
                                   values=(n, typ, f'{ftok}/{dn.token_manuf}' if ftok else '', '', '',
                                           fmt_mtime(os.path.getmtime(p))))
            self.items[iid] = dict(path=p, isdir=True, header=None, dirname=dn, name=n,
                                   long=long_name, install=kind)
            self._pending.append(iid)
        # Links (Verknüpfungen) stored in this folder's @DIRNAME.000
        cur = read_dirname(self.folder)
        for k, ln in enumerate(cur.links if cur else []):
            tok = ln.token.strip('\0 ')
            iid = self.tree.insert('', 'end', text='  ' + ln.long_name,
                                   values=('→ ' + ln.target_text(),
                                           'Verknüpfung' + (' (Ordner)' if ln.is_dir else ''),
                                           f'{tok}/{ln.token_manuf}' if tok else '',
                                           f'{ln.creator.strip(chr(0))}/{ln.creator_manuf}' if ln.creator.strip('\0 ') else '',
                                           '', ''))
            self.items[iid] = dict(path=os.path.join(self.folder, f'@link{k}'), isdir=False, header=None,
                                   link=ln, name='@DIRNAME.000', long=ln.long_name)
            self._pending.append(iid)
        # GeoManager window info and icon positions (@DIRECTO.000)
        self.dirinfo = read_dirinfo(self.folder)
        positions = match_positions(self.dirinfo.positions, [n for n, _ in files + dirs]) \
            if self.dirinfo and self.dirinfo.positions else {}
        for iid, it in self.items.items():
            if it['name'] in positions:
                it['pos'] = positions[it['name']]
        for n, p in sorted(files, key=lambda x: x[0].lower()):
            if n.upper() in ADMIN_FILES and not self.show_admin.get():
                continue
            h = parse_header(read_head(p))
            if not h and self.only_geos.get():
                continue
            st = os.stat(p)
            if h:
                n_geos += 1
                tok = h.token.strip('\0 ')
                vals = (n, f'{h.version}.x · {h.type_name}', f'{tok}/{h.token_manuf}' if tok else '',
                        f'{h.creator.strip(chr(0))}/{h.creator_manuf}' if h.creator.strip('\0 ') else '',
                        fmt_size(st.st_size).replace(' Bytes', ''), fmt_mtime(st.st_mtime))
                text = h.long_name or n
            else:
                vals = (n, 'DOS-Datei', '', '', fmt_size(st.st_size).replace(' Bytes', ''),
                        fmt_mtime(st.st_mtime))
                text = n
            iid = self.tree.insert('', 'end', text='  ' + text, values=vals)
            self.items[iid] = dict(path=p, isdir=False, header=h, name=n, long=text,
                                   size=st.st_size, mtime=st.st_mtime, pos=positions.get(n))
            if h:
                self._pending.append(iid)
        self._counts = (n_geos, len(dirs))
        self._update_status()
        target = None
        for iid, it in self.items.items():
            if select and os.path.normcase(it['path']) == os.path.normcase(select):
                target = iid
        kids = self.tree.get_children()
        if target or kids:
            t = target or kids[0]
            self.tree.selection_set(t)
            self.tree.focus(t)
            self.tree.see(t)
        self.after(1, self._load_icons)

    def _update_status(self):
        n_geos, n_dirs = getattr(self, '_counts', (0, 0))
        if self.ctx.root:
            db = os.path.relpath(self.ctx.tokendb_path, self.ctx.root) if self.ctx.tokendb_path else 'keine'
            inst = f'Installation: {self.ctx.root} · Token-Datenbank: {db}'
        else:
            inst = 'keine GEOS-Installation erkannt (Ordner darüber oder daneben)'
        extra = getattr(self, 'status_extra', '')
        apps = extra or f'{len(self.ctx.apps)} Apps bekannt'
        self.status.set(f'{n_geos} GEOS-Dateien · {n_dirs} Ordner · {inst} · {apps}')

    def _load_icons(self):
        """Resolve icons in small batches so the window stays responsive."""
        batch, self._pending = self._pending[:15], self._pending[15:]
        for iid in batch:
            it = self.items.get(iid)
            if not it:
                continue
            if it['isdir']:
                dn = it.get('dirname')
                owner, src = None, 'GEOS-Installation' if it.get('install') else 'Ordner-Symbol'
                if not it.get('install'):
                    if dn and dn.token.strip('\0 ') and self.ctx.tokendb:
                        e = self.ctx.tokendb.lookup(dn.token, dn.token_manuf)
                        if e and e.best_icon():
                            owner, src = e, f'Ordner-Icon „{dn.token}“ aus der Token-Datenbank'
                    if not owner:
                        owner = self.ctx.standard('Verzeichnis')
            elif it.get('link'):
                owner, src = self.ctx.resolve_link(it['link'])
            else:
                owner, src = self.ctx.resolve(it['path'], it['header'])
            it['owner'], it['source'] = owner, src
            mon = owner.best_icon(prefer=(1, 0, 2, 3)) if owner else None
            if mon:
                img = moniker_image(mon)
            else:
                img = builtin_icon('install' if it.get('install') else 'folder' if it['isdir'] else 'file')
                if src == 'Standard-Icon':
                    it['source'] = 'eingebautes Symbol (keine Token-Datenbank)'
            it['img'] = img
            photo = ImageTk.PhotoImage(fit_row(img))
            self._img_refs[iid] = photo
            self.tree.item(iid, image=photo)
            if iid in self.tree.selection():
                self.show_detail()
        if self._pending:
            self.after(1, self._load_icons)

    def sort_by(self, key):
        rev = getattr(self, '_sort', (None, False))
        rev = not rev[1] if rev[0] == key else False
        self._sort = (key, rev)

        def k(iid):
            it = self.items[iid]
            if key == '#0':
                v = it['long'].lower()
            elif key == 'size':
                v = it.get('size', -1)
            elif key == 'mtime':
                v = it.get('mtime', 0)
            else:
                v = str(self.tree.set(iid, key)).lower()
            return (not it['isdir'], v)
        order = sorted(self.tree.get_children(), key=k, reverse=rev)
        if rev:   # keep folders on top
            order = [i for i in order if self.items[i]['isdir']] + [i for i in order if not self.items[i]['isdir']]
        for i, iid in enumerate(order):
            self.tree.move(iid, '', i)

    # ---------------- detail panel ----------------
    def show_detail(self):
        sel = self.tree.selection()
        if not sel:
            return
        it = self.items[sel[0]]
        h = it['header']
        owner = it.get('owner')
        mon = owner.best_icon(prefer=(2, 1, 0, 3)) if owner else None
        self._detail_imgs = []
        if mon:
            img = moniker_image(mon, 2 if mon.bitmap[0] <= 64 else 1)
            ph = ImageTk.PhotoImage(img)
            self._detail_imgs.append(ph)
            self.big_icon.configure(image=ph, width=max(140, img.width + 8), height=max(88, img.height + 8))
        elif it.get('img') is not None:
            img = it['img'].resize((it['img'].width * 2, it['img'].height * 2), Image.NEAREST)
            ph = ImageTk.PhotoImage(img)
            self._detail_imgs.append(ph)
            self.big_icon.configure(image=ph, width=140, height=88)
        else:
            self.big_icon.configure(image='')
        self.d_name.configure(text=it['long'])
        self.d_src.configure(text=('Icon: ' + it['source']) if it.get('source') else '',
                             foreground='#a00' if 'Standard' in it.get('source', '') else
                             '#555' if 'Datenbank' in it.get('source', '') else '#2c6e2c')
        f = self.fields
        for k in ('Interner Name', 'Eigenschaften', 'Bibliotheken', 'Dokumentarten', 'Erzeugt von'):
            f[k].configure(text='')
        for w in self.d_buttons.winfo_children():
            w.destroy()
        f['Pfad'].configure(text=os.path.dirname(it['path']))
        f['DOS-Name'].configure(text=it['name'])
        self.notes_label.configure(text='Datei-Notizen:')
        if it['isdir']:
            dn = it.get('dirname')
            for k in ('Datei-Typ', 'GEOS-Version', 'Token', 'Ersteller', 'Release', 'Protokoll',
                      'Größe', 'Erstellt', 'Copyright'):
                f[k].configure(text='')
            f['Datei-Typ'].configure(text=(f'GEOS-Installation ({it["install"]})' if it.get('install') else 'Ordner')
                                     + (' – Langname aus @DIRNAME.000' if dn else ''))
            if dn:
                f['GEOS-Version'].configure(text='GEOS 2.x / FreeGEOS')
                tok = dn.token.strip('\0 ')
                f['Token'].configure(text=f'„{tok}“, Hersteller-ID {dn.token_manuf} (Ordner-Icon)' if tok else '–')
            f['Letzte Änderung'].configure(text=fmt_mtime(os.path.getmtime(it['path'])))
            self.notes_label.configure(text='Ordner-Info:')
            self._set_notes(self._folder_info(it['path'], dn))
        elif it.get('link'):
            ln = it['link']
            for k in f:
                if k not in ('Pfad', 'DOS-Name'):
                    f[k].configure(text='')
            f['DOS-Name'].configure(text='(gespeichert in @DIRNAME.000)')
            f['Datei-Typ'].configure(text='Verknüpfung' + (' auf einen Ordner' if ln.is_dir else ''))
            f['GEOS-Version'].configure(text='GEOS 2.x / FreeGEOS')
            tok = ln.token.strip('\0 ')
            f['Token'].configure(text=f'„{tok}“, Hersteller-ID {ln.token_manuf}' if tok else '–')
            f['Ersteller'].configure(text=f'„{ln.creator}“, Hersteller-ID {ln.creator_manuf}'
                                     if ln.creator.strip('\0 ') else '–')
            f['Release'].configure(text='.'.join(map(str, ln.release)))
            f['Protokoll'].configure(text='.'.join(map(str, ln.protocol)))
            target = self.ctx.link_target(ln)
            self.notes_label.configure(text='Verknüpfung:')
            self._set_notes(f'Ziel: {ln.target_text()}\n'
                            + (f'Auf diesem Rechner: {target}\n(Doppelklick öffnet das Ziel)' if target else
                               'Das Ziel liegt außerhalb der Installation (z. B. Laufwerk im Emulator).'))
        elif h:
            f['Datei-Typ'].configure(text=h.type_name)
            f['GEOS-Version'].configure(text='GeoWorks 1.x' if h.version == 1 else 'GEOS 2.x / FreeGEOS')
            tok = h.token.strip('\0 ')
            f['Token'].configure(text=f'„{tok}“, Hersteller-ID {h.token_manuf}' if tok else '–')
            f['Ersteller'].configure(text=f'„{h.creator}“, Hersteller-ID {h.creator_manuf}'
                                     if h.creator.strip('\0 ') else '–')
            f['Release'].configure(text=h.release_str)
            f['Protokoll'].configure(text=h.protocol_str)
            f['Größe'].configure(text=fmt_size(it['size']))
            f['Erstellt'].configure(text=h.created or '–')
            f['Letzte Änderung'].configure(text=fmt_mtime(it['mtime']))
            f['Copyright'].configure(text=h.notice or '–')
            self._program_details(it, h)
            notes = h.notes
            if it.get('pos'):
                notes = (notes + '\n\n' if notes else '') + \
                    f'Position im GeoManager-Fenster: x = {it["pos"][0]}, y = {it["pos"][1]}'
            self._set_notes(notes)
        else:
            for k in f:
                if k not in ('Pfad', 'DOS-Name'):
                    f[k].configure(text='')
            f['Datei-Typ'].configure(text='DOS-Datei (kein GEOS-Dateikopf)')
            f['Größe'].configure(text=fmt_size(it['size']))
            f['Letzte Änderung'].configure(text=fmt_mtime(it['mtime']))
            self._set_notes('')
        self._fill_gallery(owner, mon)
        # show only rows that have a value
        for k, v in f.items():
            if v.cget('text'):
                self.field_labels[k].grid()
                v.grid()
            else:
                self.field_labels[k].grid_remove()
                v.grid_remove()

    def _button(self, text, cmd):
        ttk.Button(self.d_buttons, text=text, command=cmd).pack(side='left', padx=(0, 6))

    def _program_details(self, it, h):
        """Extra rows for applications and documents, plus jump/search buttons."""
        f = self.fields
        tok, creator = h.token.strip('\0 '), h.creator.strip('\0 ')
        if h.type_name.startswith('Programm'):
            try:
                with open(it['path'], 'rb') as fh:
                    gi = geode_info(fh.read())
            except OSError:
                gi = None
            if gi:
                f['Interner Name'].configure(text=f'{gi.name}.{gi.ext}' if gi.ext else gi.name)
                f['Eigenschaften'].configure(text=f'{gi.attr_text()} · {gi.resources} Ressourcen, '
                                                  f'{gi.exports} Exporte')
                f['Bibliotheken'].configure(text=gi.libs_text())
                f['Dokumentarten'].configure(text=', '.join(f'„{t}“/{m}' for t, m in gi.document_tokens)
                                             or 'keine')
            if tok:
                self._button('Dokumente dieser App suchen …',
                             lambda: self.open_search(SearchQuery(creator=tok, kind='Dokumente')))
        elif creator:
            app = self.ctx.apps.get((h.creator, h.creator_manuf)) or next(
                (p for (t, m), p in self.ctx.apps.items() if t == h.creator), None)
            if app:
                ah = parse_header(read_head(app))
                f['Erzeugt von'].configure(text=f'{ah.long_name if ah else ""} ({os.path.basename(app)})')
                self._button('→ Zur App', lambda: self.open_path(app))
            else:
                f['Erzeugt von'].configure(text=f'App mit Token „{creator}“ – in dieser Installation nicht gefunden')
            self._button('Ähnliche Dokumente suchen …',
                         lambda: self.open_search(SearchQuery(token=tok, creator=creator)))

    def open_search(self, query=None):
        root = self.ctx.root or self.folder
        if not root:
            messagebox.showinfo(APP_NAME, 'Bitte zuerst einen Ordner öffnen.')
            return
        SearchWindow(self, root, query or SearchQuery())

    def _folder_info(self, path, dn):
        lines = []
        if dn:
            lines.append(f'Langname: {dn.long_name}')
            if dn.links:
                lines.append(f'Verknüpfungen darin: {len(dn.links)} ('
                             + ', '.join(l.long_name for l in dn.links[:6])
                             + (' …' if len(dn.links) > 6 else '') + ')')
        di = read_dirinfo(path)
        if di:
            lines.append('GeoManager-Fenster (@DIRECTO.000):')
            lines += ['  ' + x for x in di.describe().split('\n')]
        if not lines:
            lines.append('Keine GEOS-Ordnerdateien (@DIRNAME.000, @DIRECTO.000) – '
                         'unter GeoWorks 1.x gibt es keine langen Ordnernamen.')
        return '\n'.join(lines)

    def _set_notes(self, text):
        self.notes.configure(state='normal')
        self.notes.delete('1.0', 'end')
        self.notes.insert('1.0', text)
        self.notes.configure(state='disabled')

    def _fill_gallery(self, owner, selected):
        self._gallery_items = []
        self.selected_moniker = selected
        if owner:
            for m in owner.monikers:
                if m.is_graphic:
                    self._gallery_items.append((m, ImageTk.PhotoImage(moniker_image(m))))
        self._layout_gallery()

    def _layout_gallery(self):
        c = self.gallery
        c.delete('all')
        x = y = 8
        row_h = 0
        width = max(c.winfo_width(), 200)
        for i, (m, ph) in enumerate(self._gallery_items):
            w = max(ph.width(), 86)
            hgt = ph.height() + 30
            if x + w > width - 8 and x > 8:
                x, y = 8, y + row_h + 8
                row_h = 0
            tag = f'm{i}'
            if m is self.selected_moniker:
                c.create_rectangle(x - 3, y - 3, x + w + 3, y + hgt, outline='#0057b7', width=2, tags=tag)
            c.create_image(x + w // 2, y + ph.height() // 2, image=ph, tags=tag)
            label = f'{m.bitmap[0]}×{m.bitmap[1]}\n' + {0: 'S/W', 1: '16 Farben', 2: '256 Farben', 3: '24 Bit'}.get(m.bitmap[2], '')
            c.create_text(x + w // 2, y + ph.height() + 3, text=label, anchor='n',
                          font=('Segoe UI', 8), justify='center', tags=tag)
            c.tag_bind(tag, '<Button-1>', lambda e, mm=m: self._pick(mm))
            x += w + 12
            row_h = max(row_h, hgt)
        c.configure(scrollregion=(0, 0, width, y + row_h + 8))

    def _pick(self, m):
        self.selected_moniker = m
        self._layout_gallery()

    def save_icon(self, kind):
        m = self.selected_moniker
        sel = self.tree.selection()
        if not m or not sel:
            messagebox.showinfo(APP_NAME, 'Bitte zuerst eine Datei mit Icon auswählen.')
            return
        it = self.items[sel[0]]
        base = os.path.splitext(it['name'])[0]
        name = f'{base}_{m.bitmap[0]}x{m.bitmap[1]}.{kind}'
        path = filedialog.asksaveasfilename(title='Icon speichern', initialfile=name,
                                            defaultextension='.' + kind,
                                            filetypes=[(kind.upper(), '*.' + kind)])
        if not path:
            return
        img = moniker_image(m)
        if kind == 'png':
            img.save(path)
        else:
            side = max(img.width, img.height)
            sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
            sq.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
            sizes = [(s, s) for s in (16, 32, 48, 64) if s <= max(side, 16)] or [(side, side)]
            sq.save(path, sizes=sizes)
        self.status.set(f'Icon gespeichert: {path}')

    # ---------------- token database browser ----------------
    def show_tokendb(self):
        db = self.ctx.tokendb
        if not db:
            messagebox.showinfo(APP_NAME, 'Keine Token-Datenbank geladen.\n'
                                'Bitte einen Ordner einer GEOS-Installation öffnen oder '
                                'über „Datei → Token-Datenbank wählen“ eine auswählen.')
            return
        win = tk.Toplevel(self)
        win.title(f'Token-Datenbank – {self.ctx.tokendb_path}')
        win.geometry('720x600')
        tv = ttk.Treeview(win, style='Files.Treeview', columns=('tok', 'manuf', 'var'))
        tv.heading('#0', text='Name')
        tv.heading('tok', text='Token')
        tv.heading('manuf', text='Hersteller-ID')
        tv.heading('var', text='Icon-Varianten')
        tv.column('#0', width=280)
        tv.column('tok', width=80)
        tv.column('manuf', width=100)
        tv.column('var', width=200)
        sb = ttk.Scrollbar(win, orient='vertical', command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side='left', fill='both', expand=True)
        sb.pack(side='left', fill='y')
        win._imgs = []
        entries = sorted(db.entries.values(), key=lambda e: (e.token.lower(), e.manuf))
        state = {'i': 0}

        def fill():
            for e in entries[state['i']:state['i'] + 40]:
                mon = e.best_icon(prefer=(1, 0, 2, 3))
                img = ''
                if mon:
                    img = ImageTk.PhotoImage(fit_row(moniker_image(mon)))
                    win._imgs.append(img)
                n = sum(1 for m in e.monikers if m.is_graphic)
                tv.insert('', 'end', text='  ' + (e.name() or '–'), image=img,
                          values=(e.token, e.manuf, f'{n} Grafiken'))
            state['i'] += 40
            if state['i'] < len(entries) and win.winfo_exists():
                win.after(1, fill)
        fill()

    # ---------------- about ----------------
    def show_about(self):
        d = tk.Toplevel(self)
        d.title(f'Über {APP_NAME}')
        d.transient(self)
        d.resizable(False, False)
        outer = ttk.Frame(d, padding=14)
        outer.pack(fill='both', expand=True)
        content = ttk.Frame(outer)
        content.pack(fill='both', expand=True)
        logo = ttk.Label(content)
        logo.pack(side='left', padx=(0, 14), anchor='n')
        try:
            with Image.open(resource_path('JME-Spirallogo.png')) as im:
                im = im.convert('RGBA')
                im.thumbnail((104, 104), Image.LANCZOS)
                d._logo = ImageTk.PhotoImage(im)
            logo.configure(image=d._logo)
        except Exception:
            logo.configure(text='JME')
        info = ttk.Frame(content)
        info.pack(side='left', fill='both', expand=True)
        ttk.Label(info, text=f'{APP_NAME} {APP_VERSION}', font=('Segoe UI', 15, 'bold')).pack(anchor='w', pady=(0, 7))
        text = ('GEOS / GeoWorks File Information Viewer\n\n'
                'Erweiterte Neuimplementierung des klassischen\n'
                'GeoView von Rainer Bettsteller (RABE-Soft, 2000/2001).\n\n'
                'Unterstützt GeoWorks 1.x, GEOS 2.x und FreeGEOS.\n'
                'Icons werden direkt aus den Apps gelesen, Dokument-Icons\n'
                'aus der erzeugenden App, sonst aus der Token-Datenbank.\n\n'
                'Entwickelt zum 25. Geithainer PC/GEOS-Treffen\n'
                '2026 in Syhra.\n\n'
                'Projektleitung und Weiterentwicklung: Johannes Möller\n'
                'KI-Unterstützung: ChatGPT (OpenAI), Grok (xAI) und Claude (Anthropic)\n\n'
                'Möllerjaner © 2026 Johannes Möller')
        ttk.Label(info, text=text, justify='left', wraplength=520).pack(anchor='w', fill='x')
        ttk.Button(outer, text='Schließen', command=d.destroy).pack(anchor='e', pady=(12, 0))
        d.update_idletasks()
        d.geometry(f'+{self.winfo_rootx() + 40}+{self.winfo_rooty() + 40}')


class SearchWindow(tk.Toplevel):
    """Search GEOS files of the whole installation by name, token, creator, ID."""

    KINDS = ('alle', 'Programme', 'Dokumente', 'Daten')

    def __init__(self, app, root, query):
        super().__init__(app)
        self.app = app
        self.root_dir = root
        self.title(f'Suchen – {root}')
        self.geometry('980x600')
        self._imgs = {}
        self._gen = 0
        self.results = {}
        frm = ttk.Frame(self, padding=8)
        frm.pack(fill='x')
        self.v_text = tk.StringVar(value=query.text)
        self.v_token = tk.StringVar(value=query.token)
        self.v_creator = tk.StringVar(value=query.creator)
        self.v_manuf = tk.StringVar(value='' if query.manuf is None else str(query.manuf))
        self.v_kind = tk.StringVar(value=query.kind)
        self.v_scope = tk.StringVar(value='inst')
        row = 0
        for label, var, width in (('Name enthält:', self.v_text, 24), ('Token:', self.v_token, 6),
                                  ('Ersteller:', self.v_creator, 6), ('Hersteller-ID:', self.v_manuf, 7)):
            ttk.Label(frm, text=label).grid(row=0, column=row, sticky='e', padx=(8 if row else 0, 4))
            e = ttk.Entry(frm, textvariable=var, width=width)
            e.grid(row=0, column=row + 1, sticky='w')
            e.bind('<Return>', lambda ev: self.start())
            if row == 0:
                e.focus_set()
            row += 2
        ttk.Label(frm, text='Art:').grid(row=1, column=0, sticky='e', padx=(0, 4), pady=(6, 0))
        ttk.Combobox(frm, textvariable=self.v_kind, values=self.KINDS, state='readonly',
                     width=12).grid(row=1, column=1, sticky='w', pady=(6, 0))
        sc = ttk.Frame(frm)
        sc.grid(row=1, column=2, columnspan=5, sticky='w', pady=(6, 0), padx=(8, 0))
        ttk.Radiobutton(sc, text=f'ganze Installation ({root})', variable=self.v_scope,
                        value='inst').pack(side='left')
        ttk.Radiobutton(sc, text='aktueller Ordner mit Unterordnern', variable=self.v_scope,
                        value='folder').pack(side='left', padx=(10, 0))
        self.btn = ttk.Button(frm, text='Suchen', command=self.start)
        self.btn.grid(row=0, column=8, rowspan=2, padx=(12, 0), sticky='ns')
        tv = ttk.Treeview(self, style='Files.Treeview',
                          columns=('dos', 'folder', 'type', 'token', 'creator'))
        for k, t, w in (('#0', 'GEOS-Name', 260), ('dos', 'DOS-Name', 110), ('folder', 'Ordner', 230),
                        ('type', 'Typ', 150), ('token', 'Token', 80), ('creator', 'Ersteller', 80)):
            tv.heading(k, text=t)
            tv.column(k, width=w)
        sb = ttk.Scrollbar(self, orient='vertical', command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        self.status = tk.StringVar(value='Suchbegriffe eingeben und „Suchen“ drücken. '
                                         'Token und Ersteller: genau 4 Zeichen, Groß-/Kleinschreibung zählt.')
        ttk.Label(self, textvariable=self.status, relief='sunken', anchor='w',
                  padding=(6, 2)).pack(fill='x', side='bottom')
        tv.pack(side='left', fill='both', expand=True, padx=(8, 0), pady=(0, 8))
        sb.pack(side='left', fill='y', pady=(0, 8))
        tv.bind('<Double-1>', self.jump)
        tv.bind('<Return>', self.jump)
        self.tv = tv
        if any((query.text, query.token, query.creator, query.manuf is not None)):
            self.after(50, self.start)

    def _query(self):
        manuf = self.v_manuf.get().strip()
        return SearchQuery(text=self.v_text.get().strip(), token=self.v_token.get().strip(),
                           creator=self.v_creator.get().strip(),
                           manuf=int(manuf) if manuf.isdigit() else None, kind=self.v_kind.get())

    def start(self):
        q = self._query()
        if not any((q.text, q.token, q.creator, q.manuf is not None)) and q.kind == 'alle':
            if not messagebox.askyesno(APP_NAME, 'Ohne Suchbegriff werden alle GEOS-Dateien gelistet. '
                                                 'Trotzdem suchen?', parent=self):
                return
        top = self.root_dir if self.v_scope.get() == 'inst' else (self.app.folder or self.root_dir)
        self._gen += 1
        gen = self._gen
        self.tv.delete(*self.tv.get_children())
        self.results.clear()
        self._imgs.clear()
        self._queue = deque()
        self._count = 0
        self._found = 0
        self._done = False

        def worker():
            for p, h in search(top, q, stop=lambda: gen != self._gen,
                               progress=lambda n: setattr(self, '_count', n)):
                self._queue.append((p, h))
            if gen == self._gen:
                self._done = True

        threading.Thread(target=worker, daemon=True).start()
        self.after(100, lambda: self._poll(gen, top))

    def _poll(self, gen, top):
        if gen != self._gen or not self.winfo_exists():
            return
        batch = [self._queue.popleft() for _ in range(min(40, len(self._queue)))]
        for p, h in batch:
            self._found += 1
            tok, cr = h.token.strip('\0 '), h.creator.strip('\0 ')
            iid = self.tv.insert('', 'end', text='  ' + (h.long_name or os.path.basename(p)), values=(
                os.path.basename(p), os.path.relpath(os.path.dirname(p), top),
                f'{h.version}.x · {h.type_name}', f'{tok}/{h.token_manuf}' if tok else '',
                f'{cr}/{h.creator_manuf}' if cr else ''))
            self.results[iid] = (p, h)
            try:
                owner, _ = self.app.ctx.resolve(p, h)
                mon = owner.best_icon(prefer=(1, 0, 2, 3)) if owner else None
                if mon:
                    ph = ImageTk.PhotoImage(fit_row(moniker_image(mon)))
                    self._imgs[iid] = ph
                    self.tv.item(iid, image=ph)
            except Exception:
                pass
        if self._done and not self._queue:
            self.status.set(f'{self._found} Treffer in {top}. Doppelklick zeigt die Datei im Hauptfenster.')
            return
        self.status.set(f'Suche … {self._count} Dateien geprüft, {self._found} Treffer')
        self.after(60, lambda: self._poll(gen, top))

    def jump(self, event=None):
        sel = self.tv.selection()
        if sel and sel[0] in self.results:
            self.app.open_path(self.results[sel[0]][0])
            self.app.lift()


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else None
    app = GeoViewPlus(start)
    app.mainloop()


if __name__ == '__main__':
    main()
