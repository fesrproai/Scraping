# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_cli_simple.py'],
    pathex=[],
    binaries=[],
    datas=[('utils', 'utils'), ('scrapers', 'scrapers'), ('data', 'data')],
    hiddenimports=['requests', 'beautifulsoup4', 'lxml', 'matplotlib', 'numpy', 'sqlite3', 'json', 'csv', 'datetime', 'hashlib', 'difflib', 're'],
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
    name='Sistema_Descuentos_Chile',
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
