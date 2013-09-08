# -*- coding: utf-8 -*-

# Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa (http://ninja-ide.org).
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


"""Utilities to find and use cocotb"""

"""
Changes:
    09/08/2013: Initial Commit
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os

#DEFAULT_POSIX_COCOTB = "/usr/local"
DEFAULT_POSIX_COCOTB = "/home/cospan/Projects"
DEFAULT_WINDOWS_COCOTB = "C:\\Program Files\\"

class CocotbWarning(Exception):
    pass

class CocotbError(Exception):
    pass

def find_cocotb_base (path = "", debug = False):
    """
    Find Cocotb base directory in the normal installation path. If the user
    specifies a location it attempts to find cocotb in that directory. This
    function failes quietly because most people will probably not use cocotb
    on the full design so it's not a big deal if it fails

    Args:
        path (string): Path to cocotb base if cocotb is not installed in the
            default location(can be left blank)
    Returns:
        (String): Path to cocotb on the local machine, returns an empty string
            if none is found

    Raises: Nothing
    """
    #Normally cocotb is installed (on Linux) at
    if os.name == "posix":
        if len(path) == 0:
            path = DEFAULT_POSIX_COCOTB

    else:
        raise CocotbError("Error, Windows and Mac are not supported for " +
                          "cocotb utils")


    dirs = os.listdir(path)
    if debug: print "Look for directory"
    if debug: print "path: %s" % path
    for s in dirs:
        if "cocotb" in s:
            path = os.path.join(path, s)
            if debug: print "Found: %s" % path
            return path

    raise CocotbWarning("Did not find Cocotb in %s" % path)

