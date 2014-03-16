# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
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


""" utils
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'


from PyQt4.Qt import QColor

def get_color_from_id(num):
    #Boost the light level, it would be very difficult to see if the
    #Background Color is too dark
    red = ((num >> 16) & 0xFF) | 0x40
    green = ((num >> 8) & 0xFF) | 0x40
    blue = (num & 0xFF) | 0x40
    return QColor(red, green, blue)

