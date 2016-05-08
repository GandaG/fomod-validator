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

from os.path import join
from lxml import etree
from .utility import check_fomod, check_file
from .exceptions import MissingFileError, MissingFolderError, ValidationError, ParserError


def validate_package(package_path, schema_file):
    """
    Validate your FOMOD installer. Raises ValidationError if installer is not valid.
    :param package_path: The root folder of your package. Should contain a "fomod" folder with the installer inside.
    :param schema_file: The path to the schema file, with filename and extension.
    """
    try:
        fomod_folder = check_fomod(package_path)
        config_file = check_file(join(package_path, fomod_folder))
        validate_tree(etree.parse(join(package_path, fomod_folder, config_file)), schema_file)
    except (MissingFolderError, MissingFileError):
        raise
    except etree.ParseError as e:
        raise ParserError(str(e))
    except ValidationError as e:
        raise ValidationError(check_file(join(package_path, check_fomod(package_path))) +
                              " is invalid with error message:\n\n" + str(e))


def validate_tree(elem_tree, schema_file):
    """
    Validate your FOMOD installer. Raises ValidationError if installer is not valid.
    :param elem_tree: The root element of your config xml tree.
    :param schema_file: The path to the schema file, with filename and extension.
    """
    try:
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xmlschema.assertValid(elem_tree)
    except etree.ParseError as e:
        raise ParserError(str(e))
    except etree.DocumentInvalid as e:
        raise ValidationError("The Config tree is invalid with error message:\n\n" + str(e))
