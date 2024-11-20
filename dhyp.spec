# -*- mode: python -*-

block_cipher = None

import openvr
openvr_dll_path = os.path.join(os.path.dirname(openvr.__file__), 'libopenvr_api_64.dll')
         
a = Analysis(['main.py'],
             binaries=[ (openvr_dll_path, '.' ), ],
             hiddenimports=['ctypes'],
             datas=[('white_pixel.png', '.')],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='dont_hit_your_pole',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='dont_hit_your_pole')
