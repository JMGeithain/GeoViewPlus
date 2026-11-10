# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/Johannes Möller/Downloads/GeoViewPlus_0.4.4.1_JME_Logo_Layoutfix/GeoViewPlus.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Johannes Möller/Downloads/GeoViewPlus_0.4.4.1_JME_Logo_Layoutfix/geoworks_motif_icon.ico', '.'), ('C:/Users/Johannes Möller/Downloads/GeoViewPlus_0.4.4.1_JME_Logo_Layoutfix/JME-Spirallogo.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GeoViewPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:/Users/Johannes Möller/Downloads/GeoViewPlus_0.4.4.1_JME_Logo_Layoutfix/geoworks_motif_icon.ico'],
)
