# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for CRM Sistema de Gestion
# Build with: pyinstaller crm.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # UI files (Qt Designer layouts)
        ('app/views/ui', 'app/views/ui'),
        # Assets (SVG icons)
        ('app/assets', 'app/assets'),
        # Database schema SQL (para crear la BD en primer uso)
        ('db/database_query.sql', 'db'),
    ],
    hiddenimports=[
        # PyQt5 plugins needed at runtime
        'PyQt5.QtPrintSupport',
        'PyQt5.sip',
        # matplotlib backend for PyQt5
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_agg',
        # openpyxl internals
        'openpyxl.cell._writer',
        # reportlab internals
        'reportlab.graphics.barcode.code128',
        'reportlab.graphics.barcode.code93',
        'reportlab.graphics.barcode.code39',
        'reportlab.graphics.barcode.usps',
        'reportlab.graphics.barcode.usps4s',
        'reportlab.graphics.barcode.ecc200datamatrix',
        # bcrypt
        'bcrypt',
        # PIL / Pillow
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'xmlrpc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CRM-Sistema',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # Sin ventana de consola (app de escritorio)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='app/assets/crm.ico',  # Descomentar si tienes un .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CRM-Sistema',
)
