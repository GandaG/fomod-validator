# -*- mode: python -*-

block_cipher = None
import sys
from path import Path

root_path = Path(__name__).abspath().dirname()
sys.path.append(root_path)
from fomod_validator import __exename__

a = Analysis(['fomod_validator.py'],
             pathex=[root_path],
             binaries=None,
             datas=[(root_path.joinpath('dat'), 'dat')],
             hiddenimports=[],
             hookspath=[root_path],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=__exename__,
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon=root_path.joinpath('dat', 'file_icon.ico'))
