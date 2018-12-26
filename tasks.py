import os
import sys
import time
from pathlib import Path
from platform import system
from shutil import rmtree
from subprocess import run
from zipfile import ZipFile

from invoke import task

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from fomod_validator import __arcname__, __exename__, __version__


@task
def check(c):
    c.run("isort -m 3 -tc -fgw 0 -up -w 88 -rc src")
    c.run("black src")
    c.run("flake8 --max-line-length=80 --select=C,E,F,W,B,B950 --ignore=E501 src")


@task
def build(c):
    if system().lower() != "windows":
        raise OSError("Freezing only supported in Windows.")

    root_path = Path(__file__).resolve().parent
    rmtree(root_path / "dist", ignore_errors=True)
    rmtree(root_path / "build", ignore_errors=True)
    dist_dir = root_path / "dist" / "pyinstaller"
    print("----> Freezing executable to {}".format(dist_dir), flush=True)
    spec_path = root_path / "pyinstaller.spec"
    print("----> spec file found at {}".format(spec_path), flush=True)

    pyinstaller_args = [
        "pyinstaller",
        str(spec_path),
        "--clean",
        "--distpath",
        str(dist_dir),
    ]
    run(pyinstaller_args).check_returncode()
    print("----> Pyinstaller ran successfully!!!", flush=True)

    zip_name = "{}-{}.zip".format(__arcname__, __version__)
    zip_dir = root_path / "dist"
    zip_path = zip_dir / zip_name
    print("----> Archive will be built to {}".format(zip_path), flush=True)
    exe_path = dist_dir / (__exename__ + ".exe")
    assert exe_path.exists()
    print("----> Executable found at {}".format(exe_path), flush=True)

    included_files = ["LICENSE", "README.md", "CHANGELOG.md"]
    with ZipFile(zip_path, "w") as zipfile:
        zipfile.write(exe_path, arcname=__exename__ + ".exe")
        for fname in included_files:
            new_fname = str(Path(fname).stem + ".txt")
            file_path = root_path / fname
            print("----> Adding file {} to archive.".format(file_path), flush=True)
            zipfile.write(file_path, arcname=new_fname)
