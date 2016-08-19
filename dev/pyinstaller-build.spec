# -*- mode: python -*-

block_cipher = None
import os

a = Analysis(['pyinstaller-bootstrap.py'],
             pathex=[os.getcwd()],
             binaries=None,
             datas=[('../setup.cfg', '.'),
                    ('../resources', 'resources/'),
                    ('../fomod/validator/resources', 'resources/'),],
             hiddenimports=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='FOMOD Validator',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='resources/file_icon.ico')
