# -*- coding: utf-8 -*-

import inspect
import os
import sys
import json
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QWizardPage
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QRadioButton
#from PyQt4.QtGui import QMessageBox


class PageBoardSelection(QWizardPage):

    def __init__(self, locator, project, output):
        self.project = project
        self.output = output
        self.output.Debug(self, "creating page")

        board_path = os.path.abspath(
                        os.path.join(os.path.dirname(__file__),
                        os.pardir,
                        os.pardir,
                        os.pardir,
                        os.pardir,
                        os.pardir,
                        os.pardir,
                        "ibuilder",
                        "boards"))

        self.boards = {}
        self.output.Debug(self, "Board Path: %s" % board_path)
        self.output.Debug(self, "Get board names")

        for root, dirs, names in os.walk(board_path):
          for d in dirs:
            f = open(os.path.join(root, d, "config.json"))
            self.output.Debug(self, "Adding: %s" % f)
            c = json.loads(f.read())
            self.boards[c["board_name"]] = c

        QWizardPage.__init__(self)
        self.locator = locator
        self.output = output
        # Table
        layout = QVBoxLayout()
        self.output.Debug(self, "Create table view")

        self.tv = BoardTableView(self.output)
        self.btm = BoardTableModel([[]], ["Name", "Vendor", "FPGA"], self)
        self.tv.setModel(self.btm)

        for a in self.boards:
          name = a
          fpga = self.boards[a]["fpga_part_number"]
          vendor = self.boards[a]["vendor"]
          pos = self.btm.rowCount()
          self.btm.insertRows(pos, 1)
          self.btm.set_line_data([name, vendor, fpga])
          self.tv.resizeColumnsToContents()

        self.board = None
        layout.addWidget(QLabel('Select a target board from the following list'))
        layout.addWidget(self.tv)
        self.setLayout(layout)
        self.tv.selectRow(0)


    def table_select_changed(self, index):
        key = self.boards.keys()[index]
        #self.project.board_dict = self.boards[key]
        self.output.Debug(self, "Table selection changed to: %s" % key)
        self.project.update_board_selection(self.boards[key])

    def validatePage(self):
        self.output.Debug(self, "Validate board selection page")
        return True


class ImageCustomizeSelection(QWizardPage):

    def __init__(self, locator, output, board_dict):
        QWizardPage.__init__(self)
        self.output = output
        self.output.Debug(self, "creating page")
        self.board_dict = board_dict

        grid = QGridLayout(self)
        grid.addWidget(QLabel('Core Name:'), 0, 0)
        self.cname = QLabel("")
        self.output.Debug(self, "adding core name")
        grid.addWidget(self.cname, 1, 0)
        self.output.Debug(self, "Finished adding core name")

        self.bus_panel = QWidget(self)
        self.wishbone = QRadioButton("Wishbone")
        self.wishbone.setChecked(True)
        self.axi = QRadioButton("Axi")
        self.bgl = QGridLayout(self.bus_panel)
        self.bgl.addWidget(QLabel("Select Bus"), 0, 0)
        self.bgl.addWidget(self.wishbone, 1, 0)
        self.bgl.addWidget(self.axi, 1, 1)
        grid.addWidget(self.bus_panel, 2, 0)

    def update_user_selection(self, board_dict):
        self.board_dict = board_dict
        self.output.Debug(self, "selection changed to %s" % self.board_dict["board_name"])
        self.cname.setText(self.board_dict["board_name"])

    def validatePage(self):
        self.output.Debug(self, "Validate bus selection page")
        return True

    def get_bus(self):
        if self.axi.isChecked():
          return "axi"
        return "wishbone"

class BoardTableView(QTableView):

    def __init__(self, output):
        super(BoardTableView, self).__init__()
        self.output = output
        output.Debug(self, "Created table")
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)

    def selectionChanged(self, to_index, from_index):
        #self.output.Debug(self, "Selection Changed to %d" % (to_index.first().top()))
        self.parentWidget().table_select_changed(to_index.first().top())
        return QTableView.selectionChanged(self, from_index, to_index)



class BoardTableModel(QAbstractTableModel):

    def __init__(self, data_in = [[]], header_data=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.array_data = []
        self.header_data = header_data
 
    def rowCount(self, parent=None):
        #print "Row Count = %d" % len(self.array_data)
        return len(self.array_data)
 
    def columnCount(self, parent):
        #print "Column Count = %d" % len(self.array_data[0])
        return len(self.header_data)
 
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
 
    def data(self, index, role):
 
        #if role == QtDisplayRole:
        #  row = index.row()
        #  column = index.column()
        #  return self.array_data[row][col]
       
        '''
        if not index.isValid():
          return QVariant()
       
        elif role != Qt.DisplayRole:
          return QVariant()
        '''
       
        if index.isValid() and role == Qt.DisplayRole:
            return self.array_data[index.row()][index.column()]
 
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header_data[col]
        #return QVariant()
 
    def set_line_data(self, data):
        self.array_data.append(list(data))
        #print "New Data: %s" % str(self.array_data)
 
    def insertRows(self, pos, rows, parent = QModelIndex()):
        self.beginInsertRows(parent, pos, pos + rows - 1) 
        #for i in range(rows):
            #print "Inserting a row"
            #self.array_data.insert(pos, ["", "", "", ""])
            #print "Row Count after insert is: %d" % len(self.array_data)
        self.endInsertRows()
        return True

