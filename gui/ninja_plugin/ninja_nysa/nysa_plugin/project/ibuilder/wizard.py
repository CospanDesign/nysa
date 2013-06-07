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

    def __init__(self, locator, output):
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

        boards = {}
        self.output.Debug(self, "Board Path: %s" % board_path)
        self.output.Debug(self, "Get board names")

        for root, dirs, names in os.walk(board_path):
          for d in dirs:
            f = open(os.path.join(root, d, "config.json"))
            self.output.Debug(self, "Adding: %s" % f)
            c = json.loads(f.read())
            boards[c["board_name"]] = c

        QWizardPage.__init__(self)
        self.locator = locator
        self.output = output
        # Table
        layout = QVBoxLayout()
        self.output.Debug(self, "Create table view")

        self.tv = BoardTableView(self.output)
        self.btm = BoardTableModel([[]], ["Name", "Vendor", "FPGA"], self)
        self.tv.setModel(self.btm)

        for a in boards:
          name = a
          fpga = boards[a]["fpga_part_number"]
          vendor = boards[a]["vendor"]
          pos = self.btm.rowCount()
          self.btm.insertRows(pos, 1)
          self.btm.set_line_data([name, vendor, fpga])
          self.tv.resizeColumnsToContents()

        self.board = None
        layout.addWidget(QLabel('Select a target board from the following list'))
        layout.addWidget(self.tv)
        self.setLayout(layout)
        self.tv.selectRow(0)


    def validatePage(self):
        self.output.Debug(self, "Validate board selection page")
        return True


class BoardTableView(QTableView):

    def __init__(self, output):
      super(BoardTableView, self).__init__()
      self.output = output
      output.Debug(self, "Created table")
      self.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.verticalHeader().hide()
      self.horizontalHeader().setStretchLastSection(True)



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

