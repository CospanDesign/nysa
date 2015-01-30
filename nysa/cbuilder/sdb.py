#! /usr/bin/python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa.
# (http://wiki.cospandesign.com/index.php?title=Nysa.org)
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

from array import array as Array
import collections

from nysa.common.status import Status

class SDBError(Exception):
    pass

class SDBWarning(Exception):
    pass

class SDBInfo(Exception):
    pass

class SDB (object):

    def __init__(self, status = None):
        self.d = {}
        self.s = status
        if status is None:
            self.s = Status()

        for e in self.ELEMENTS:
            self.d[e] = ""

