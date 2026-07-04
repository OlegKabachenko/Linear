# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('uix/uix_config.yaml', 'uix'),
        ('uix/bigtouchswitch/bigtouchswitch.kv', 'uix/bigtouchswitch'),
        ('uix/calculatebox/calculatebox.kv', 'uix/calculatebox'),
        ('uix/controlbox/controlbox.kv', 'uix/controlbox'),
        ('uix/customdialog/customdialog.kv', 'uix/customdialog'),
        ('uix/mainscreen/mainscreen.kv', 'uix/mainscreen'),
        ('uix/parameterbox/parameterbox.kv', 'uix/parameterbox'),
        ('uix/params/params.kv', 'uix/params'),
        ('uix/sizablebtn/sizablebtn.kv', 'uix/sizablebtn'),
        ('uix/standartboxlayout/standartboxlayout.kv', 'uix/standartboxlayout'),
        ('uix/systembox/systembox.kv', 'uix/systembox'),
        ('uix/systemdatabox/systemdatabox.kv', 'uix/systemdatabox'),
        ('config.yaml', '.'),

    ],
    hiddenimports=['kivy', 'kivy_garden', 'kivymd'],
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
    name='Linear',
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
)
