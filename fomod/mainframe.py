#!/usr/bin/env python

# Copyright 2016 Daniel Nunes
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

from PyQt5 import uic, QtWidgets, QtCore, QtGui
from os.path import join, expanduser
from . import cur_folder

base_ui = uic.loadUiType(join(cur_folder, "resources", "mainframe.ui"))


class Mainframe(base_ui[0], base_ui[1]):
    def __init__(self):
        super(Mainframe, self).__init__()
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        window_icon = QtGui.QIcon()
        window_icon.addPixmap(QtGui.QPixmap(join(cur_folder, "resources/window_icon.jpg")),
                              QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(window_icon)

        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)
        self.path_button.clicked.connect(self.path_button_clicked)

        self.package_path = ""
        self.checked_validate = False
        self.checked_warnings = False

        self.show()

    def accepted(self):
        from .validator import validate, check_warnings, ValidatorError

        self.package_path = self.path_text.text()
        self.checked_validate = self.check_validate.isChecked()
        self.checked_warnings = self.check_warnings.isChecked()

        self.close()

        try:
            errorbox = QtWidgets.QMessageBox()

            if self.checked_validate:
                validate(self.package_path, cur_folder)

            if self.checked_warnings:
                log = check_warnings(self.package_path)

            errorbox.setText("All good!")
            errorbox.setWindowTitle("Yay!")
            errorbox.exec_()
            return
        except ValidatorError as e:
            errorbox.setText(str(e))
            errorbox.setWindowTitle(e.title)
            errorbox.setIconPixmap(QtGui.QPixmap(join(cur_folder, "resources/logo_admin.png")))
            errorbox.exec_()
            return

    def rejected(self):
        self.close()

    def path_button_clicked(self):
        open_dialog = QtWidgets.QFileDialog()
        self.path_text.setText(open_dialog.getExistingDirectory(self, "Package directory:", expanduser("~")))
