# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['menu_automatico.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('scrapers', 'scrapers'), ('core', 'core'), ('database', 'database'), ('scheduler', 'scheduler'), ('api', 'api'), ('utils', 'utils'), ('frontend', 'frontend'), ('env.example', '.'), ('requirements.txt', '.'), ('README.md', '.'), ('INSTALACION.md', '.')],
    hiddenimports=['selenium', 'selenium.webdriver', 'selenium.webdriver.chrome.options', 'firebase_admin', 'firebase_admin.credentials', 'firebase_admin.firestore', 'flask', 'flask_cors', 'schedule', 'fake_useragent', 'retrying', 'beautifulsoup4', 'lxml', 'requests', 'python-dotenv', 'urllib3', 'certifi', 'charset_normalizer', 'idna'],
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
    name='DescuentosCL_Auto',
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
