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

from sys import exit
from configparser import ConfigParser
from os.path import join, expanduser, isdir
from os import makedirs
from webbrowser import open as web_open
from requests import get, codes, ConnectionError, Timeout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.uic import loadUiType
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from . import cur_folder, __version__

base_ui = loadUiType(join(cur_folder, "resources", "mainframe.ui"))
default_settings = {"Path": {"lastused": ""}}


class Mainframe(base_ui[0], base_ui[1]):
    """Custom class for the main window."""
    def __init__(self):
        super(Mainframe, self).__init__()
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        window_icon = QIcon()
        window_icon.addPixmap(QPixmap(join(cur_folder, "resources/window_icon.png")), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(window_icon)

        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)
        self.path_button.clicked.connect(self.path_button_clicked)

        self.package_path = ""
        self.checked_validate = False
        self.checked_warnings = False

        if isdir(join(expanduser("~"), ".fomod")):
            config = ConfigParser()
            config.read_dict(default_settings)
            config.read(join(expanduser("~"), ".fomod", ".validator"))
            self.path_text.setText(config["Path"]["lastused"])

        try:
            response = get("https://api.github.com/repos/GandaG/fomod-validator/releases", timeout=1)
            if response.status_code == codes.ok and response.json()[0]["tag_name"][1:] > __version__:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("There is a new version available.")
                msg_box.setText("Do you want to open the latest release in your browser?")
                msg_box.setStandardButtons(QMessageBox.Ok |
                                           QMessageBox.Ignore)
                msg_box.setDefaultButton(QMessageBox.Ok)
                answer = msg_box.exec_()
                if answer == QMessageBox.Ok:
                    self.close()
                    web_open("https://github.com/GandaG/fomod-validator/releases/latest")
                    exit()
                else:
                    self.show()
            else:
                self.show()
        except (Timeout, ConnectionError):
            self.show()

    def accepted(self):
        """
        Method called when the user clicks the OK button.

        It pulls all the needed info from the gui first, saves the path to a settings file in the $HOME directory,
        closes the main window then does the main checks - refer to the validator sub-package - and if there are issues
        found then it raises a message box about it. Otherwise the all good is given.

        The only handled exceptions should be the ones explicity created in the validator sub-package, all others should
        be freely raised and given to the sys.excepthook to handle.
        """
        from .validator import validate_package, check_warnings, ValidatorError

        self.package_path = self.path_text.text()
        self.checked_validate = self.check_validate.isChecked()
        self.checked_warnings = self.check_warnings.isChecked()

        makedirs(join(expanduser("~"), ".fomod"), exist_ok=True)
        config = ConfigParser()
        config.read_dict(default_settings)
        config["Path"]["lastused"] = self.package_path
        with open(join(expanduser("~"), ".fomod", ".validator"), "w") as configfile:
            config.write(configfile)

        self.close()

        errorbox = QMessageBox()
        try:
            if self.checked_validate:
                validate_package(self.package_path, join(cur_folder, "resources", "mod_schema.xsd"))

            if self.checked_warnings:
                check_warnings(self.package_path)

            errorbox.setText("All good!")
            errorbox.setWindowTitle("Yay!")
            errorbox.exec_()
            return
        except ValidatorError as e:
            errorbox.setText(str(e))
            errorbox.setWindowTitle(e.title)
            errorbox.setIconPixmap(QPixmap(join(cur_folder, "resources/logo_admin.png")))
            errorbox.exec_()
            return

    def rejected(self):
        """Called when the user clicks the Cancel button. Nothing special, just exits."""
        self.close()

    def path_button_clicked(self):
        """
        Called when the user clicks the button next to the line edit - the path choosing button.

        First checks if there is text in the line edit and uses that for the initial search directory. If not, then it
        defaults to the user $HOME directory.

        Once a directory is chosen and the user has not clicked cancel (cancel returns an empty path) it directly sets
        the line edit text.
        """
        open_dialog = QFileDialog()
        if not self.path_text.text():
            button_path = expanduser("~")
        else:
            button_path = self.path_text.text()

        temp_path = open_dialog.getExistingDirectory(self, "Package directory:", button_path)

        if temp_path:
            self.path_text.setText(temp_path)
