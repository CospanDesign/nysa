# -*- coding: utf-8 *-*

# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  07/20/2013: Initial commit
'''

import os
import sys
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from downloader_view import DownloaderView

class ToolPropertiesView(QWidget):
    def __init__(self, locator):
        QWidget.__init__(self)
        self.setWindowTitle("Tool Properties")

        self.properties = QTableWidget()
        self.properties.setShowGrid(True)
        self.dl = DownloaderView(locator)

        self.grid = QGridLayout()
        self.grid.addWidget(QLabel("Tool Properties"), 0, 0, 1, 4)
        self.grid.addWidget(QLabel("Downloader"), 0, 4, 1, 4)
        self.grid.addWidget(self.properties, 1, 0, 4, 4)
        self.grid.addWidget(self.dl, 1, 4, 4, 4)
        self.setLayout(self.grid)

    def set_downloader_script(self, workdir, script_path, flags):
        self.dl.set_downloader_script(workdir, script_path, flags)

