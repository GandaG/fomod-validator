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

from os.path import join, isfile, isdir
from lxml import etree
from .utility import check_file, check_fomod
from .exceptions import MissingFileError, MissingFolderError, WarningError


def check_warnings(package_path):
    class ElementLog(object):
        def __init__(self, elements, title, msg):
            self.elements = {}
            for elem_ in elements:
                if elem_.tag not in self.elements.keys():
                    self.elements[elem_.tag] = [elem_]
                else:
                    self.elements[elem_.tag].append(elem_)

            self.title = title

            self.msgs = {}
            for elem_ in elements:
                self.msgs[elem_.tag] = msg.replace("{}", elem_.tag)

    result = "<b>Warnings Log</b><br><br><br><br>"
    result_initial = result

    repeatable_tags = ("moduleName", "moduleImage", "moduleDependencies",
                       "requiredInstallFiles", "installSteps", "conditionalFileInstalls", "")
    repeated_elems = []
    repeated_elems_msg = "The tag {} has several occurrences, this may produce unexpected results."
    folder_tags = ("folder",)
    missing_folders = []
    missing_folders_msg = "These source folder(s) weren't found inside the package. " \
                          "The installers ignore this so be sure to fix it."
    file_tags = ("file",)
    missing_files = []
    missing_files_msg = "These source file(s) weren't found inside the package. " \
                        "The installers ignore this so be sure to fix it."

    try:
        fomod_folder = check_fomod(package_path)
        config_file = check_file(join(package_path, fomod_folder))
        config_tree = etree.parse(join(package_path, fomod_folder, config_file))

        for element in config_tree.getroot().iter():
            if element.tag in repeatable_tags:
                list_ = repeated_elems
            elif element.tag in folder_tags:
                list_ = missing_folders
            elif element.tag in file_tags:
                list_ = missing_files
            else:
                continue

            list_.append(element)

        result_repeat = []
        result_folder = []
        result_file = []

        for elem in repeated_elems:
            if sum(1 for value in repeated_elems if value.tag == elem.tag) >= 2:
                result_repeat.append(elem)

        for elem in missing_folders:
            if not isdir(join(package_path, elem.get("source"))):
                result_folder.append(elem)

        for elem in missing_files:
            if not isfile(join(package_path, elem.get("source"))):
                result_file.append(elem)

        repeat_log = None
        folder_log = None
        file_log = None

        if result_repeat:
            repeat_log = ElementLog(result_repeat, "Repeated Elements", repeated_elems_msg)
        if result_folder:
            folder_log = ElementLog(result_folder, "Missing Source Folders", missing_folders_msg)
        if result_file:
            file_log = ElementLog(result_file, "Missing Source Files", missing_files_msg)

        result += _log_warnings([repeat_log, folder_log, file_log])

        if result != result_initial:
            raise WarningError(result)
    except (MissingFolderError, MissingFileError):
        raise


def _log_warnings(list_):
    result = ""

    for log in list_:
        if log:
            result += "<i>" + log.title + "</i><br><br>"

            for tag in log.elements:
                result += "Lines"
                for elem in log.elements[tag]:
                    result += " " + str(elem.sourceline) + ","
                result = result[:-1]
                result += ": " + log.msgs[tag] + "<br>"

            result += "<br><br>"

    return result
