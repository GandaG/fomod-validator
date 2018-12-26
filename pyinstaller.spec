# -*- mode: python -*-

block_cipher = None
import sys
from pathlib import Path

root_path = Path(__name__).resolve().parent
sys.path.insert(0, str(root_path / "src"))
from fomod_validator import __exename__

a = Analysis([str(root_path / "src" / "fomod_validator.py")],
             pathex=[str(root_path)],
             binaries=None,
             datas=[(str(root_path / "dat"), "dat")],
             hiddenimports=[],
             hookspath=[str(root_path)],
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
          icon=str(root_path / "dat" / "file_icon.ico"))
