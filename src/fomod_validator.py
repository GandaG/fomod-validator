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

import keepitfresh
import pyfomod
from PyQt5 import QtCore, QtGui, QtWidgets, uic

__version__ = "1.5.3"
__exename__ = "FOMOD Validator"
__arcname__ = "fomod-validator"


if getattr(sys, "frozen", False):
    ROOT_FOLDER = sys._MEIPASS
    FROZEN = True
else:
    ROOT_FOLDER = Path(__file__).resolve().parent.parent
    FROZEN = False


BASE_UI = uic.loadUiType(Path(ROOT_FOLDER) / "dat" / "mainframe.ui")


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
    icon_path = Path(ROOT_FOLDER) / "dat" / "logo_admin.png"

    tbinfofile = io.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = ("Error information:\n\nVersion: {}\n{}: {}\n").format(
        version_info, str(exc_type), str(exc_value)
    )
    sections = [errmsg, tbinfo]
    msg = "\n".join(sections)

    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(notice)
    errorbox.setDetailedText(msg)
    errorbox.setWindowTitle("An Error Has Occured")
    errorbox.setIconPixmap(QtGui.QPixmap(str(icon_path)))
    errorbox.exec_()


class catch_warnings(object):
    def __enter__(self):
        log = []
        self.orig_warn = pyfomod.base.warnings.warn
        pyfomod.base.warnings.warn = lambda x, *args, **kwargs: log.append(x)
        return log

    def __exit__(self, *args):
        pyfomod.base.warnings.warn = self.orig_warn


class Mainframe(*BASE_UI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("{} {}".format(__exename__, __version__))
        window_icon = QtGui.QIcon()
        ico_path = Path(ROOT_FOLDER) / "dat" / "window_icon.png"
        window_icon.addPixmap(
            QtGui.QPixmap(str(ico_path)), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.setWindowIcon(window_icon)
        self.button_path.clicked.connect(self.button_path_clicked)
        self.button_validate.clicked.connect(self.button_validate_clicked)
        self.button_fix.clicked.connect(self.button_fix_clicked)
        if FROZEN:
            base_url = "https://github.com/GandaG/fomod-validator/releases"
            regex = r"{}-(\d+\.\d+\.\d+)\.zip".format(__arcname__)
            if not keepitfresh.is_fresh(base_url, regex, __version__):
                msgbox = QtWidgets.QMessageBox()
                msgbox.setText("Do you wish to update and restart?")
                msgbox.setWindowTitle("An Update Is Available")
                msgbox.setStandardButtons(
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if msgbox.exec_() == QtWidgets.QMessageBox.Yes:
                    keepitfresh.freshen_up(
                        base_url=base_url,
                        regex=regex,
                        current_version=__version__,
                        overwrite_item=sys.executable,
                        entry_point=__exename__ + ".exe",
                    )

    @staticmethod
    def validate_file(package_path, instance):
        source = Path(package_path) / Path(instance.src)
        if not source.exists():
            warn_msg = "The source {} {} is missing from the package.".format(
                instance._tag, instance.src
            )
            pyfomod.warn(
                "Missing Source {}".format(instance._tag.capitalize()),
                warn_msg,
                instance,
                critical=True,
            )
        elif instance._tag == "folder" and source.isfile():
            warn_msg = "The source folder {} is actually a file.".format(instance.src)
            pyfomod.warn("Source Folder is a File", warn_msg, instance, critical=True)

    def add_warning(self, warning):
        if isinstance(warning, pyfomod.base.CriticalWarning):
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
            if warning.elem.lineno is not None:
                lineno = " : line {}".format(warning.elem.lineno)
        parent_container = QtWidgets.QTreeWidgetItem()
        item = QtWidgets.QPushButton("{}{}{}".format(title, tag, lineno))
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
        self.tree_warnings.clear()
        self.button_fix.setEnabled(False)
        package_path = self.text_path.text()
        if package_path.endswith(("/", "\\")):
            package_path = package_path[:-1]
        with catch_warnings() as warns:
            try:
                root = pyfomod.parse(package_path, quiet=False, lineno=True)
                val_dict = {"File": [lambda x: self.validate_file(package_path, x)]}
                root.validate(**val_dict)
            except FileNotFoundError as exc:
                pyfomod.warn("Fomod Not Found", str(exc), None, critical=True)
            crit_warns = []
            reg_warns = []
            for warn in warns:
                if warn.title in ("Syntax Error", "Missing Info"):
                    self.button_fix.setEnabled(True)
                elif warn.title == "Comment Detected":
                    continue
                if isinstance(warn, pyfomod.base.CriticalWarning):
                    crit_warns.append(warn)
                else:
                    reg_warns.append(warn)
        self.tree_warnings.setRootIsDecorated(False)
        self.tree_warnings.setIndentation(0)
        for warn in crit_warns + reg_warns:
            self.add_warning(warn)

    def button_fix_clicked(self):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(
            "WARNING: Experimental Feature.\n"
            "Syntax Errors and missing info.xml can be fixed "
            "but all comments will be lost. Proceed?"
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
