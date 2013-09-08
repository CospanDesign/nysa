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



import inspect

#from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

StatusLevel = enum ('FATAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'VERBOSE')


class NysaStatus(QWidget):
  status_list = None
  mdl = None

  def __init__(self):
    QWidget.__init__(self)
    self.level = StatusLevel.VERBOSE
    self.init_ui()

    self.Verbose(self, "Hello World!")

  def init_ui(self):
    self.setWindowTitle('Status')

    self.status_list = QTableView()
    header = ["Index", "Level", "Class", "Message"]
    self.mdl = NysaStatusModel([[]], header, self)
    self.status_list.setModel(self.mdl)
    self.setMinimumSize(400, 300)

    #Hide the grids
    self.status_list.setShowGrid(False)
    self.status_list.setSelectionBehavior(QAbstractItemView.SelectRows)

    #Hide vertical header
    vh = self.status_list.verticalHeader()
    vh.setVisible(False)
    #Set horizontal header properties
    hh = self.status_list.horizontalHeader()
    hh.setStretchLastSection(True)

    #set column width to fit contents
    self.status_list.resizeColumnsToContents()

    layout = QVBoxLayout()
    layout.addWidget(self.status_list)
    self.setLayout(layout)
    self.show()

  def Verbose (self, c, text):
    if self.CheckLevel(StatusLevel.VERBOSE):
      self.status_output("Verbose", c, text, fg = "White", bg="Blue")

  def Debug (self, c, text):
    if self.CheckLevel(StatusLevel.DEBUG):
      self.status_output("Debug", c, text, fg = "White", bg="Black")

  def Info (self, c, text):
    if self.CheckLevel(StatusLevel.INFO):
      self.status_output("Info", c, text, fg="Green", bg="Black")

  def Warning (self, c, text):
    if self.CheckLevel(StatusLevel.WARNING):
      self.status_output("Warning", c, text, fg="Yellow", bg="Black")

  def Error (self, c, text):
    if self.CheckLevel(StatusLevel.ERROR):
      self.status_output("Error", c, text, fg="Red")

  def Fatal (self, c, text):
    if self.CheckLevel(StatusLevel.FATAL):
      self.status_output("Fatal", c, text, fg="Red", bg="Black")

  def Print (self, text):
    self.status_output("Extra", self, text)

  def PrintLine(self, text):
    self.status_output("Extra", self, text)

  def status_output(self, level, c, text, fg = None, bg = None):
    pos = self.mdl.rowCount()
    #print "Position: %d" % pos
    self.mdl.insertRows(pos, 1)
    f = str(inspect.stack()[2][3])
    d = "%s:%s" % (c.__class__.__name__, f)
    self.mdl.set_line_data([str(pos), level, d, text, fg, bg])
    self.status_list.resizeColumnsToContents()
    self.status_list.scrollToBottom()

  def SetLevel(self, level):
    self.level = level

  def GetLevel(self):
    return self.level

  def CheckLevel(self, requestLevel):
    if requestLevel is StatusLevel.FATAL:
      return True
    elif requestLevel is StatusLevel.VERBOSE:
      if  self.level is StatusLevel.VERBOSE:
        return True
    elif requestLevel is StatusLevel.DEBUG:
      if  self.level is StatusLevel.VERBOSE or \
          self.level is StatusLevel.DEBUG:
        return True
    elif requestLevel is StatusLevel.INFO:
      if self.level is StatusLevel.VERBOSE or  \
          self.level is StatusLevel.DEBUG or   \
          self.level is StatusLevel.INFO:
        return True
    elif requestLevel is StatusLevel.WARNING:
      if self.level == StatusLevel.VERBOSE or  \
          self.level == StatusLevel.DEBUG or   \
          self.level == StatusLevel.INFO  or   \
          self.level == StatusLevel.WARNING:
        return True
    elif requestLevel is StatusLevel.ERROR:
      if self.level == StatusLevel.VERBOSE or  \
          self.level == StatusLevel.DEBUG or   \
          self.level == StatusLevel.INFO  or   \
          self.level == StatusLevel.WARNING or \
          self.level == StatusLevel.ERROR:
        return True

    return False


  def paint(self, event):
    self.QWidget.pain(self, event)


class NysaStatusModel(QAbstractTableModel):
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
    self.array_data.append([data[0], data[1], data[2], data[3]])
    #print "New Data: %s" % str(self.array_data)

  def insertRows(self, pos, rows, parent = QModelIndex()):
    self.beginInsertRows(parent, pos, pos + rows - 1) 
    #for i in range(rows):
      #print "Inserting a row"
      #self.array_data.insert(pos, ["", "", "", ""])
      #print "Row Count after insert is: %d" % len(self.array_data)
    self.endInsertRows()
    return True
