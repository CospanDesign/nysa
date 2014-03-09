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


""" nysa interface
"""

__author__ = 'email@example.com (name)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit

class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()

    def setup_simple_text_output_view(self):
        self.setWindowTitle("Standalone View")
        layout = QVBoxLayout()

        #DEMO WIDGET START
        #You can use this as a standard output
        self.te = QTextEdit()
        self.te.setText("Text!")
        layout.addWidget(self.te)
        #DEMO WIDGET END

        self.setLayout(layout)
        self.show()

    #DEMO WIDGET START
    def append_text(self, text):
        self.te.append(text)

    def clear_text(self):
        self.te.setText("")
    #DEMO WIDGET END



        
