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


""" DRT Viewer... view
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import Qt

from .drt_table import DRTTree

class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()

    def setup_simple_text_output_view(self):
        self.setWindowTitle("Standalone View")
        self.drt_tree_table = DRTTree(self)
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        #Create the buttons
        self.expand_all_button = QPushButton("Expand All")
        self.collapse_all_button = QPushButton("Collapse All")
        button_layout.addWidget(self.expand_all_button)
        button_layout.addWidget(self.collapse_all_button)

        #Connect the signals
        self.expand_all_button.clicked.connect(self.expand_all)
        self.collapse_all_button.clicked.connect(self.collapse_all)

        layout = QHBoxLayout()
        main_layout.addLayout(layout)

        layout.addWidget(self.drt_tree_table)
        self.text = ""
        self.te = QLabel(self.text)
        self.te.setMaximumWidth(500)
        self.te.setWordWrap(True)
        self.te.setAlignment(Qt.AlignTop)
        layout.addWidget(self.te)

        #self.setLayout(layout)
        self.setLayout(main_layout)
        self.show()

    def append_text(self, text):
        self.text += text
        self.te.setText(self.text)

    def clear_text(self):
        self.text = ""
        self.te.setText("")

    def add_drt_entry(self, index, raw, description, dev_type, value_list):
        self.drt_tree_table.add_entry(index, raw, description, dev_type, value_list)

    def clear_table(self):
        self.drt_tree_table.clear()

    def resize_columns(self):
        self.drt_tree_table.resize_columns()

    def expand_all(self):
        self.drt_tree_table.expandAll()


    def collapse_all(self):
        self.drt_tree_table.collapseAll()

        
