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

"""
The main and only module.
"""

import argparse
import errno
import io
import os
import sys
import traceback

import keepitfresh
import pyfomod
from path import Path
from PyQt5 import QtCore, QtGui, QtWidgets, uic

__version__ = '1.5.3'
__exename__ = 'FOMOD Validator'
__arcname__ = 'fomod-validator'


if getattr(sys, 'frozen', False):
    # pylint: disable=no-member
    ROOT_FOLDER = sys._MEIPASS
    FROZEN = True
else:
    ROOT_FOLDER = Path(__file__).abspath().dirname()
    FROZEN = False


BASE_UI = uic.loadUiType(Path(ROOT_FOLDER).joinpath('dat', 'mainframe.ui'))


def excepthook(exc_type, exc_value, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param exc_type exception type
    @param exc_value exception value
    @param tracebackobj traceback object
    """
    notice = (
        "An unhandled exception occurred. Please report the problem"
        " at <a href = https://github.com/GandaG/fomod-validator/is"
        "sues>Github</a>.")
    version_info = __version__
    icon_path = Path(ROOT_FOLDER).joinpath('dat', 'logo_admin.png')

    tbinfofile = io.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = ('Error information:\n\n'
              'Version: {}\n{}: {}\n').format(version_info,
                                              str(exc_type),
                                              str(exc_value))
    sections = [errmsg, tbinfo]
    msg = '\n'.join(sections)

    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(notice)
    errorbox.setDetailedText(msg)
    errorbox.setWindowTitle("An Error Has Occured")
    errorbox.setIconPixmap(QtGui.QPixmap(icon_path))
    errorbox.exec_()


def format_check_output(error_list, file_path):
    """
    Formats the output from pyfomod's check_for_errors into::

        <file>
            <title>
            Lines <lines>: <msg>

            <title>
            Lines <lines>: <msg>
    """
    result_str = file_path + '\n'
    for error in error_list:
        result_str += '    '
        result_str += error.title
        result_str += '\n    Lines '
        result_str += ', '.join(str(line) for line in error.lines)
        result_str += ': '
        result_str += error.msg.replace('\n', '\n    ')
        result_str += '\n\n'
    return result_str


def process_path(fomod_path, check):
    """
    Fully process the path - check if it's a dir, validate
    and check for errors if **check** is True.
    """
    fomod_path = Path(fomod_path)
    result_str = ''
    try:
        if not fomod_path.exists():
            raise FileNotFoundError(errno.ENOENT,
                                    os.strerror(errno.ENOENT),
                                    str(fomod_path))
        if fomod_path.isdir():
            fomod_paths = pyfomod.io.get_installer_files(fomod_path)
        else:
            fomod_paths = [fomod_path]
        for path in fomod_paths:
            pyfomod.assert_valid(path)

            if check:
                if fomod_path.isdir():
                    relpath = Path(path).relpath(fomod_path)
                else:
                    relpath = fomod_path
                error_list = pyfomod.check_for_errors(path, fomod_path)
                formatted = format_check_output(error_list, relpath)
                result_str += formatted
    except (FileNotFoundError, AssertionError) as exc:
        result_str = str(exc)

    return result_str


class Mainframe(BASE_UI[0], BASE_UI[1]):
    """
    Custom class for the main window.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint |
                            QtCore.Qt.WindowTitleHint)
        window_icon = QtGui.QIcon()
        ico_path = Path(ROOT_FOLDER).joinpath('dat', 'window_icon.png')
        window_icon.addPixmap(QtGui.QPixmap(ico_path),
                              QtGui.QIcon.Normal,
                              QtGui.QIcon.Off)
        self.setWindowIcon(window_icon)

        self.button_validate.clicked.connect(self.validate)
        self.path_button.clicked.connect(self.path_button_clicked)
        self.check_warnings.toggled.connect(self.check_unused.setEnabled)

        if FROZEN:
            base_url = 'https://github.com/GandaG/fomod-validator/releases'
            regex = r'{}-(\d+\.\d+\.\d+)\.zip'.format(__arcname__)
            if not keepitfresh.is_fresh(base_url, regex, __version__):
                msgbox = QtWidgets.QMessageBox()
                msgbox.setText('Do you wish to update and restart?')
                msgbox.setWindowTitle("An Update Is Available")
                msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes |
                                          QtWidgets.QMessageBox.No)
                if msgbox.exec_() == QtWidgets.QMessageBox.Yes:
                    keepitfresh.freshen_up(base_url=base_url,
                                           regex=regex,
                                           current_version=__version__,
                                           overwrite_item=sys.executable,
                                           entry_point=__exename__ + '.exe')

    def validate(self):
        """
        Method called when the user clicks the Validate button.

        Outputs to the text browser.
        """
        package_path = self.path_text.text()
        checked_warnings = self.check_warnings.isChecked()

        if self.check_unused.isChecked():
            # pylint: disable=arguments-differ,unused-argument,unused-variable
            class UnusedFilesError(pyfomod.UnusedFilesError):
                """Monkey-patched class to do nothing."""
                def check(self, *args):
                    return False
        else:
            class UnusedFilesError(pyfomod.UnusedFilesError):
                """Should restore class to normal."""
                pass

        self.text_warnings.setPlainText(process_path(package_path,
                                                     checked_warnings))

    def path_button_clicked(self):
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
        if not self.path_text.text():
            init_path = Path("~").expanduser()
        else:
            init_path = self.path_text.text()

        temp_path = open_dialog.getExistingDirectory(self,
                                                     "Select package folder",
                                                     init_path)
        if temp_path:
            self.path_text.setText(temp_path)


def main():
    """
    Entry point to the module - parses cli args or runs the gui.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("fomod_path",
                        help="path to fomod file or folder",
                        nargs='?',
                        default=None)
    parser.add_argument("-c",
                        "--check",
                        help="check for common errors",
                        action="store_true")
    args = parser.parse_args()

    if args.fomod_path is not None:
        return process_path(args.fomod_path, args.check) or 0

    # if no arguments passed, launch gui
    sys.excepthook = excepthook
    app = QtWidgets.QApplication(sys.argv)
    win = Mainframe()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
