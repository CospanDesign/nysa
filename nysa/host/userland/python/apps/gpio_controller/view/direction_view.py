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


""" Direction View
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QButtonGroup

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))


from gpio_actions import GPIOActions


class DirectionView(QWidget):

    def __init__(self, count = 8):
        super (DirectionView, self).__init__()
        self.actions = GPIOActions()
        layout = QGridLayout()

        self.dir_items = []

        for i in range (count):
            pass

