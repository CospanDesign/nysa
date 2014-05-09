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


"""
UART Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import time
import json

from array import array as Array

from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))
from driver.uart import UARTError



class UARTEngineError(Exception):
    pass

class UARTEngineThread(QtCore.QThread):
    def __init__(self, engine, uart, mutex, delay, actions, init_commands, loop_commands, server):
        super(UARTEngineThread, self).__init__()

        self.uart = uart
        self.engine = engine
        self.mutex = mutex
        self.delay = int(delay * 1000)
        self.actions = actions
        self.term_flag = False
        self.loop_commands = loop_commands
        self.init_pos = 0
        self.loop_pos = 0
        self.pause = False
        self.step = False
        self.step_loop = False
        self.server = server

