# -*- mode: python -*-
# vim: ft=python

import sys


sys.setrecursionlimit(5000)  # required on Windows


a = Analysis(
    ['labelx/__main__.py'],
    pathex=['labelx'],
    binaries=[],
    datas=[
        ('labelx/config/default_config.yaml', 'labelx/config'),
        ('labelx/icons/*', 'labelx/icons'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='labelx',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon='labelx/icons/icon.ico',
)
app = BUNDLE(
    exe,
    name='labelx.app',
    icon='labelx/icons/icon.icns',
    bundle_identifier=None,
    info_plist={'NSHighResolutionCapable': 'True'},
)
