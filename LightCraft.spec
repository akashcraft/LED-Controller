# -*- mode: python ; coding: utf-8 -*-
import os
import CTkColorPicker

ctk_color_path = os.path.dirname(CTkColorPicker.__file__)

a = Analysis(
    ['lightcraft.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Resources', 'Resources'),
        (ctk_color_path, 'CTkColorPicker'),
        ('Settings.txt', '.'),
        ('ctk_color_picker_widget.py', '.')
    ],
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
    [],
    exclude_binaries=True,
    name='LightCraft',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Resources/logo.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LightCraft',
)
app = BUNDLE(
    coll,
    name='LightCraft.app',
    icon='Resources/logo.icns',
    bundle_identifier='com.akashcraft.lightcraft',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSBluetoothAlwaysUsageDescription': 'LightCraft needs Bluetooth for hardware control.',
    },
)