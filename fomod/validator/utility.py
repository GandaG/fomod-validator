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

from os import listdir
from .exceptions import MissingFileError, MissingFolderError


def check_fomod(package_path):
    existing_fomod = False
    fomod_folder = "fomod"

    try:
        for folder in listdir(package_path):
            if folder.upper() == "FOMOD":
                existing_fomod = True
                fomod_folder = folder
    except FileNotFoundError:
        raise MissingFolderError(fomod_folder)

    if not existing_fomod:
        raise MissingFolderError(fomod_folder)

    return fomod_folder


def check_file(fomod_path):
    config_exists = False
    config_file = "moduleconfig.xml"

    for file in listdir(fomod_path):
        if file.upper() == "MODULECONFIG.XML":
            config_exists = True
            config_file = file

    if not config_exists:
        raise MissingFileError(config_file)

    return config_file
