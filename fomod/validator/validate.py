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
from .exceptions import MissingFileError, MissingFolderError, ValidationError, InvalidError


def validate(package_path, cur_folder):
    try:
        fomod_folder = check_fomod(package_path)
        config_file = check_file(join(package_path, fomod_folder))
        xmlschema_doc = etree.parse(join(cur_folder, "resources", "mod_schema.xsd"))
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xmlschema.assertValid(etree.parse(join(package_path, fomod_folder, config_file)))
    except (MissingFolderError, MissingFileError, etree.ParseError) as m:
        raise ValidationError(str(m))
    except etree.DocumentInvalid as e:
        raise InvalidError(check_file(join(package_path, check_fomod(package_path))) +
                           " is invalid with error message:\n\n" + str(e))
