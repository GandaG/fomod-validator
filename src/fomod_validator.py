#!/usr/bin/env python

# Copyright 2017 Daniel Nunes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import sys
import traceback
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from urllib.request import urlopen
from zipfile import ZipFile

import keepitfresh
import pyfomod
from pyfomod.warnings import (
    CommentsPresentWarning,
    DefaultAttributeWarning,
    InvalidEnumWarning,
    InvalidSyntaxWarning,
    MissingInfoWarning,
)
from PyQt5 import QtCore, QtGui, QtWidgets, uic

__version__ = "2.3.0"
__exename__ = "FOMOD Validator"
__arcname__ = "fomod-validator"


if getattr(sys, "frozen", False):
    ROOT_FOLDER = sys._MEIPASS
    FROZEN = True
else:
    ROOT_FOLDER = Path(__file__).resolve().parent.parent
    FROZEN = False


RES_FOLDER = Path(ROOT_FOLDER) / "dat"
BASE_UI = uic.loadUiType(RES_FOLDER / "mainframe.ui")
WINDOW_ICON = RES_FOLDER / "windows_icon.png"
EXC_ICON = RES_FOLDER / "logo_admin.png"
LOADING_GIF = RES_FOLDER / "loading.gif"
YES_ICON = RES_FOLDER / "yes_icon.png"
NO_ICON = RES_FOLDER / "no_icon.png"
FIX_ICON = RES_FOLDER / "fix_icon.png"

FIXABLE_TYPES = (
    InvalidEnumWarning,
    DefaultAttributeWarning,
    InvalidSyntaxWarning,
    MissingInfoWarning,
)


def excepthook(exc_type, exc_value, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param exc_type exception type
    @param exc_value exception value
    @param tracebackobj traceback object
    """
    notice = (
        "An unhandled exception occurred. Please report the problem at "
        "<a href = https://github.com/GandaG/fomod-validator/issues>Github</a>."
    )
    version_info = __version__

    tbinfofile = io.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = "Error information:\n\nVersion: {}\n{}: {}\n".format(
        version_info, str(exc_type), str(exc_value)
    )
    sections = [errmsg, tbinfo]
    msg = "\n".join(sections)

    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(notice)
    errorbox.setDetailedText(msg)
    errorbox.setWindowTitle("An Error Has Occured")
    errorbox.setIconPixmap(QtGui.QPixmap(str(EXC_ICON)))
    errorbox.exec_()


def download_file(parent, url, fpath):
    fname = fpath.name
    response = urlopen(url)
    meta = response.info()
    file_size = int(meta["Content-Length"])
    progress_dialog = QtWidgets.QProgressDialog(parent)
    progress_dialog.setWindowFlags(
        progress_dialog.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
    )
    progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
    progress_dialog.setWindowTitle("Update Available")
    progress_dialog.setLabelText("Downloading {}...".format(fname))
    progress_dialog.setCancelButtonText("Cancel")
    progress_dialog.setMaximum(file_size)
    progress_dialog.setMinimum(0)

    with fpath.open("wb") as fobj:
        file_size_dl = 0
        block_size = 8192
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            file_size_dl += len(buffer)
            progress_dialog.setValue(file_size_dl)
            if progress_dialog.wasCanceled():
                return False  # user cancelled, no file downloaded

            fobj.write(buffer)
    return True


def check_updates(parent):
    base_url = "https://github.com/GandaG/fomod-validator/releases"
    regex = r"{}-(\d+\.\d+\.\d+)\.zip".format(__arcname__)

    if not keepitfresh.is_fresh(base_url, regex, __version__):
        file_dict = keepitfresh.get_file_urls(base_url, regex)
        file_url, latest_version = keepitfresh.get_update_version(
            file_dict, __version__
        )
        msg = (
            "<p>A new version is available:</p>"
            "  - <i>Current Version</i>: <b>{}</b><br>"
            "  - <i>Latest Version</i>: <b>{}</b><br>"
            '  - <a href="https://github.com/GandaG/fomod-validator'
            '/blob/master/CHANGELOG.md">Changelog</a>'
            "<p>Do you wish to update and restart?</p>".format(
                __version__, latest_version
            )
        )
        msgbox = QtWidgets.QMessageBox(parent)
        msgbox.setTextFormat(QtCore.Qt.RichText)
        msgbox.setText(msg)
        msgbox.setWindowTitle("Update Available")
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if msgbox.exec_() == QtWidgets.QMessageBox.Yes:
            file_name = Path(urlsplit(file_url).path).name
            with TemporaryDirectory() as tmpdir:
                fpath = Path(tmpdir, file_name)
                if not download_file(parent, file_url, fpath):
                    return  # user cancelled

                with ZipFile(fpath) as fzip:
                    fzip.extractall(tmpdir)
                fpath.unlink()

                entry_point = __exename__ + ".exe"
                initem = str(Path(tmpdir, entry_point))
                keepitfresh.overwrite_restart(initem, sys.executable, entry_point)


class Mainframe(*BASE_UI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("{} {}".format(__exename__, __version__))
        window_icon = QtGui.QIcon()
        window_icon.addPixmap(
            QtGui.QPixmap(str(WINDOW_ICON)), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.setWindowIcon(window_icon)
        self.button_path.clicked.connect(self.button_path_clicked)
        self.button_validate.clicked.connect(self.button_validate_clicked)
        self.button_fix.clicked.connect(self.button_fix_clicked)

        if FROZEN:
            check_updates(self)

    @staticmethod
    def validate_source(package_path, instance):
        source = Path(package_path) / instance.src
        if not source.exists():
            warn_msg = "The source {} {} is missing from the package.".format(
                instance._tag, instance.src
            )
            return [
                pyfomod.ValidationWarning(
                    "Missing Source {}".format(instance._tag.capitalize()),
                    warn_msg,
                    instance,
                    critical=True,
                )
            ]
        return []

    @staticmethod
    def validate_folder(package_path, instance):
        source = Path(package_path) / instance.src
        if instance._tag == "folder" and source.is_file():
            warn_msg = "The source folder {} is actually a file.".format(instance.src)
            return [
                pyfomod.ValidationWarning(
                    "Source Folder is a File", warn_msg, instance, critical=True
                )
            ]
        return []

    @staticmethod
    def validate_image(package_path, instance):
        source = Path(package_path) / instance.image
        if not source.exists():
            title = "Missing Image"
            warn_msg = "The image {} is missing from the package.".format(
                instance.image
            )
            return [
                pyfomod.ValidationWarning(
                    title, warn_msg, instance._image, critical=True
                )
            ]
        return []

    def add_warning(self, warning):
        if isinstance(warning, CommentsPresentWarning):
            return
        if warning.critical:
            title_bg = "firebrick"
            label_bg = "darksalmon"
        else:
            title_bg = "teal"
            label_bg = "cadetblue"
        title = warning.title
        tag = ""
        lineno = ""
        if warning.elem is not None:
            tag = " @ {}".format(warning.elem._tag)
            if warning.elem.lineno is None:
                return  # if no line number then element is not real
            lineno = " : line {}".format(warning.elem.lineno)
        parent_container = QtWidgets.QTreeWidgetItem()
        item = QtWidgets.QPushButton("{}{}{}".format(title, tag, lineno))
        if isinstance(warning, FIXABLE_TYPES):
            self.button_fix.setEnabled(True)
            item.setToolTip("This warning can be fixed automatically.")
            item.setIcon(QtGui.QIcon(str(FIX_ICON)))
        item.toggled.connect(
            lambda x: self.tree_warnings.expandItem(parent_container)
            if x
            else self.tree_warnings.collapseItem(parent_container)
        )
        item.setCheckable(True)
        item.setStyleSheet("text-align:left; background: {};".format(title_bg))
        self.tree_warnings.addTopLevelItem(parent_container)
        self.tree_warnings.setItemWidget(parent_container, 0, item)
        msg = warning.msg
        child = QtWidgets.QLabel()
        child.setWordWrap(True)
        child.setText(msg)
        child.setStyleSheet("background: {};".format(label_bg))
        child_container = QtWidgets.QTreeWidgetItem()
        parent_container.addChild(child_container)
        self.tree_warnings.setItemWidget(child_container, 0, child)

    def button_validate_clicked(self):
        loading_gif = QtGui.QMovie(self.button_validate)
        loading_gif.setFileName(str(LOADING_GIF))
        loading_gif.frameChanged.connect(
            lambda _: self.button_validate.setIcon(
                QtGui.QIcon(loading_gif.currentPixmap())
            )
        )
        if loading_gif.loopCount() != -1:
            loading_gif.finished.connect(loading_gif.start)
        loading_gif.start()

        self.tree_warnings.clear()
        self.button_fix.setEnabled(False)
        package_path = self.text_path.text()
        if package_path.endswith(("/", "\\")):
            package_path = package_path[:-1]

        warning_list = []
        try:
            root = pyfomod.parse(package_path, warnings=warning_list, lineno=True)
            val_dict = {
                "File": [
                    lambda x: self.validate_source(package_path, x),
                    lambda x: self.validate_folder(package_path, x),
                ],
                "Root": [lambda x: self.validate_image(package_path, x)],
            }
            warning_list.extend(root.validate(**val_dict))
        except FileNotFoundError as exc:
            warning_list.append(
                pyfomod.ValidationWarning(
                    "Fomod Not Found", str(exc), None, critical=True
                )
            )

        crit_warns = []
        reg_warns = []
        for warn in warning_list:
            if warn.critical:
                crit_warns.append(warn)
            else:
                reg_warns.append(warn)
        self.tree_warnings.setRootIsDecorated(False)
        self.tree_warnings.setIndentation(0)
        for warn in crit_warns + reg_warns:
            self.add_warning(warn)
        loading_gif.stop()
        if not any((crit_warns, reg_warns)):
            self.button_validate.setIcon(QtGui.QIcon(str(YES_ICON)))
        else:
            self.button_validate.setIcon(QtGui.QIcon(str(NO_ICON)))

    def button_fix_clicked(self):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(
            "<i><b>WARNING</b>: Experimental Feature.</i><br><br>"
            "Marked warnings can be automatically fixed by this software.<br>"
            "Be aware that any comments present in the xml will be lost."
        )
        msgbox.setWindowTitle("Continue Fixing?")
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if msgbox.exec_() == QtWidgets.QMessageBox.Yes:
            package_path = self.text_path.text()
            root = pyfomod.parse(package_path)
            pyfomod.write(root, package_path)
            self.button_validate_clicked()

    def button_path_clicked(self):
        """
        Called when the user clicks the button next to the
        line edit - the path choosing button.

        First checks if there is text in the line edit and
        uses that for the initial search directory. If not,
        then it defaults to the user $HOME directory.

        Once a directory is chosen and the user has not clicked
        cancel (cancel returns an empty path) it directly sets
        the line edit text.
        """
        open_dialog = QtWidgets.QFileDialog()
        if not self.text_path.text():
            init_path = str(Path.home())
        else:
            init_path = self.text_path.text()
        temp_path = open_dialog.getExistingDirectory(
            self, "Select package folder", init_path
        )
        if temp_path:
            self.text_path.setText(temp_path)


def main():
    sys.excepthook = excepthook
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = Mainframe()
    win.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
