# -*- coding: utf-8 *-*

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common",
                             "xmsgs_tree_model"))

import xmsgs_tree_model


class XmsgViewer(QWidget):

    def __init__(self, xmodel):
        super (XmsgViewer, self).__init__()
        self.table = QTableView()
        self.set_model(xmodel)


    def set_model(self, model):
        if model is None:
            self.xmodel = xmsgs_tree_model.XmsgsTreeModel()
        else:
            self.xmodel = model
        self.table = QTableView()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Xilinx xmsg viewer")
        self.table.setModel(self.xmodel)
        self.setMinimumSize(400, 300)

        #Hide the grids
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        #Hide Vertical Header
        vh = self.table.verticalHeader()
        vh.setVisible(False)

        #Set Horizontal Header Properties
        hh = self.table.horizontalHeader()
        hh.setStretchLastSection(True)

        #Set Column width to fit contents
        self.table.resizeColumnsToContents()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.show()

