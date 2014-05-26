#! /usr/bin/python

# Copyright (c) 2014 Cospan Design (dave.mccoy@cospandesign.com)

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

import os
import sys
import argparse

from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QColor

direction_ss = os.path.join(os.path.dirname(__file__), "stylesheet.css")

class UARTConsole(QTextEdit):
    def __init__(self, status, actions):
        super (UARTConsole, self).__init__()
        self.status = status
        self.actions = actions
        self.local_echo = False
        self.insert_line_feed = False
        style = open(direction_ss, "r").read()
        self.setStyleSheet(style)
        self.actions.uart_local_echo_en.connect(self.enable_local_edit)
    
    def keyPressEvent(self, event):
        #print "Key event: %s" % str(dir(event))
        if self.local_echo:
            super(UARTConsole, self).keyPressEvent(event)
        else:
            pass
        #print "%s" % event.text()
        #self.actions.uart_data_out.emit(event.key)
        self.actions.uart_data_out.emit(event.text())

    def setText(self, text):
        super(UARTConsole, self).setText(text)
        self.moveCursor(QTextCursor.End)

    def append(self, text):
        super(UARTConsole, self).append(text)
        self.moveCursor(QTextCursor.End)

    def append_text(self, text):
        self.textCursor().insertText(text)
        self.moveCursor(QTextCursor.End)

    def enable_local_edit(self, enable):
        self.status.Verbose(self, "Enable Local Edits: %s" % str(enable))
        self.local_echo = enable
