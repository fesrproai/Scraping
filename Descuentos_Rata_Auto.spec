# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['descuentos_rata_auto.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=['requests', 'beautifulsoup4', 'lxml', 'sqlite3', 'json', 'datetime', 'hashlib', 're', 'threading', 'time', 'os', 'sys', 'typing'],
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
    name='Descuentos_Rata_Auto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
