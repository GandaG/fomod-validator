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


class MissingFolderError(Exception):
    def __init__(self, folder):
        self.msg = folder + " folder is missing."
        Exception.__init__(self, self.msg)


class MissingFileError(Exception):
    def __init__(self, file):
        self.msg = file + " file is missing."
        Exception.__init__(self, self.msg)


class ValidationError(Exception):
    def __init__(self, msg=""):
        self.msg = msg
        Exception.__init__(self, self.msg)


class WarningError(Exception):
    def __init__(self, msg=""):
        self.msg = msg
        Exception.__init__(self, self.msg)
