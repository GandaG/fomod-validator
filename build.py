#!/usr/bin/env python

# Script with the build process for PyInstaller/Windows

from platform import system
from subprocess import run
from zipfile import ZipFile

from fomod_validator import __arcname__, __exename__, __version__
from path import Path

if system != 'Windows':
    raise OSError('Freezing only allowed in Windows')

root_path = Path(__file__).abspath().dirname()
dist_dir = root_path.joinpath('dist', 'pyinstaller')
spec_path = root_path.joinpath('pyinstaller.spec')

pyinstaller_args = ['pyinstaller',
                    spec_path,
                    '--clean',
                    '--distpath',
                    dist_dir]
run(pyinstaller_args).check_returncode()

zip_name = "{}-{}.zip".format(__arcname__, __version__)
zip_dir = root_path.joinpath('dist')
zip_path = zip_dir.joinpath(zip_name)
exe_path = dist_dir.joinpath(__exename__ + '.exe')
assert exe_path.exists()

included_files = ["LICENSE", "README.md", "CHANGELOG.md"]
with ZipFile(zip_path, "w") as zipfile:
    zipfile.write(exe_path, arcname=__exename__)
    for fname in included_files:
        new_fname = Path(fname).splitext()[0] + '.txt'
        file_path = root_path.joinpath(fname)
        zipfile.write(file_path, arcname=new_fname)
