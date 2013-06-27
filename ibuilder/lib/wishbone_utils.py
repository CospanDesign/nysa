# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Utilities used in detecting and generating wishbone cores"""

"""
Log:
06/25/2013
    -Initial Commit
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import re


def is_wishbone_bus_signal(signal):
    #Look for a wishbone slave signal
    if re.search("i_wbs_we", signal) is not None:
        return True
    if re.search("i_wbs_stb", signal) is not None:
        return True
    if re.search("i_wbs_cyc", signal) is not None:
        return True
    if re.search("i_wbs_sel", signal) is not None:
        return True
    if re.search("i_wbs_adr", signal) is not None:
        return True
    if re.search("i_wbs_dat", signal) is not None:
        return True
    if re.search("o_wbs_dat", signal) is not None:
        return True
    if re.search("o_wbs_ack", signal) is not None:
        return True
    if re.search("o_wbs_int", signal) is not None:
        return True


    #Look for a wishbone master signal
    if re.search("o_.*_we$", signal) is not None:
        return True
    if re.search("o_.*_stb$", signal) is not None:
        return True
    if re.search("o_.*_cyc$", signal) is not None:
        return True
    if re.search("o_.*_sel$", signal) is not None:
        return True
    if re.search("o_.*_adr$", signal) is not None:
        return True
    if re.search("o_.*_dat$", signal) is not None:
        return True
    if re.search("i_.*_dat$", signal) is not None:
        return True
    if re.search("i_.*_ack$", signal) is not None:
        return True
    if re.search("i_.*_int$", signal) is not None:
        return True
    return False

