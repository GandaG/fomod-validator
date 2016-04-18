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

from PyQt5 import uic, QtWidgets, QtCore
from os.path import join, expanduser
from . import cur_folder


class Mainframe(QtWidgets.QDialog):
    def __init__(self):
        super(Mainframe, self).__init__()

        self.base = uic.loadUi(join(cur_folder, "resources", "mainframe.ui"))

        self.base.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)

        self.base.buttonBox.accepted.connect(self.accepted)
        self.base.buttonBox.rejected.connect(self.rejected)
        self.base.path_button.clicked.connect(self.path_button_clicked)

        self.package_path = ""
        self.checked_validate = False
        self.checked_warnings = False

        self.base.show()

    def accepted(self):
        self.base.close()

    def rejected(self):
        self.base.close()

    def path_button_clicked(self):
        open_dialog = QtWidgets.QFileDialog()
        self.base.path_text.setText(open_dialog.getExistingDirectory(self, "Package directory:", expanduser("~")))
