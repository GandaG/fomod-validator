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
from .exceptions import MissingFileError, MissingFolderError, WarningError, ParserError


def check_warnings(package_path, elem_tree=None, ignore_errors=False):
    """
    Check for common errors that are usually ignored by mod managers. Raises WarningError if any are found.
    :param package_path: The root folder of your package. Should contain a "fomod" folder with the installer inside.
    :param elem_tree: The root element of your config xml tree.
    :param ignore_errors: If true, the function returns False instead of throwing an error.
    """
    try:
        if elem_tree is not None:
            fomod_folder = check_fomod(package_path)
            config_file = check_file(join(package_path, fomod_folder))
            config_root = etree.parse(join(package_path, fomod_folder, config_file)).getroot()
        else:
            config_root = elem_tree

        element_list = [
            _WarningElement(
                config_root,
                (
                    "moduleName",
                    "moduleImage",
                    "moduleDependencies",
                    "requiredInstallFiles",
                    "installSteps",
                    "conditionalFileInstalls"
                ),
                "Repeated Elements",
                "The tag {} has several occurrences, this may produce unexpected results.",
                lambda **kwargs: sum(1 for value in kwargs["tag_list"] if value.tag == kwargs["elem"].tag) >= 2
            ),
            _WarningElement(
                config_root,
                ("folder",),
                "Missing Source Folders",
                "The source folder(s) under the tag {} weren't found inside the package. "
                "The installers ignore this so be sure to fix it.",
                lambda **kwargs: not isdir(join(package_path, kwargs["elem"].get("source")))
            ),
            _WarningElement(
                config_root,
                ("file",),
                "Missing Source Files",
                "The source file(s) under the tag {} weren't found inside the package. "
                "The installers ignore this so be sure to fix it.",
                lambda **kwargs: not isfile(join(package_path, kwargs["elem"].get("source")))
            ),
            _WarningElement(
                config_root,
                ("moduleImage", "image"),
                "Missing Images",
                "The image(s) under the tag {} weren't found inside the package. "
                "The installers ignore this so be sure to fix it.",
                lambda **kwargs: not isfile(join(package_path, kwargs["elem"].get("path")))
            ),
            _WarningElement(
                config_root,
                ("config",),
                "Empty Installer",
                "The installer is empty - it does nothing, literally!",
                lambda **kwargs: not [
                    elem for elem in kwargs["elem"]
                    if elem.tag == "moduleDependencies" or
                    elem.tag == "requiredInstallFiles" or
                    elem.tag == "installSteps" or
                    elem.tag == "conditionalFileInstalls"
                    ]
            ),
            _WarningElement(
                config_root,
                ("flagDependency",),
                "Mismatched Flag Labels",
                "The flag label that {} is dependent on is never created during installation.",
                lambda **kwargs: not (
                    not kwargs["elem"].get("value") or
                    [
                        elem for elem in kwargs["root"].iter()
                        if elem.tag == "flag" and elem.get("name") == kwargs["elem"].get("flag")
                    ]
                )
            ),
            _WarningElement(
                config_root,
                ("flagDependency",),
                "Mismatched Flag Values",
                "The flag value that {} is dependent on is never set during installation.",
                lambda **kwargs: not (
                    not kwargs["elem"].get("value") or
                    [
                        elem for elem in kwargs["root"].iter()
                        if elem.tag == "flag" and
                        elem.get("name") == kwargs["elem"].get("flag") and
                        elem.text == kwargs["elem"].get("value")
                    ]
                )
            ),
            _WarningElement(
                config_root,
                ("folder", "file"),
                "Empty Source Fields",
                "The source folder(s) under the tag {} were empty. "
                "This will install all files in the package and that is not usually intended, so be sure to fix it.",
                lambda **kwargs: not kwargs["elem"].get("source")
            ),
        ]

        log_list = []
        for warn in element_list:
            log_list.append(warn.tag_log)

        result = _log_warnings(log_list)

        if result:
            if ignore_errors:
                return False
            raise WarningError(result)
        else:
            return True
    except (MissingFolderError, MissingFileError):
        raise
    except etree.ParseError as e:
        raise ParserError(str(e))


class _WarningElement(object):
    def __init__(self, elem_root, tags, title, error_msg, condition):
        tag_list = []
        for element in elem_root.iter():
            if element.tag in tags:
                tag_list.append(element)

        tag_result = []
        for elem in tag_list:
            if condition(**{"tag_list": tag_list, "elem": elem, "root": elem_root}):
                tag_result.append(elem)

        self.tag_log = _ElementLog(tag_result, title, error_msg) if tag_result else None


class _ElementLog(object):
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
