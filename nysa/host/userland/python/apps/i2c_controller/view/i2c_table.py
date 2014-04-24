#! /usr/bin/python

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from i2c_token import I2CToken


class I2CTable(QTableWidget):

    def __init__(self, status, actions, loop):
        super(I2CTable, self).__init__()

        self.loop = loop
        self.status = status
        self.actions = actions
        self.setRowCount(0)
        self.setColumnCount(0)
        self.column_pos = 0
        self.row_pos = 0
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        #self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        #self.actions.i2c_row_add.connect(self.add_row)
        #self.actions.i2c_row_delete.connect(self.delete_row)

    def add_row(self):
        self.row_pos = self.rowCount()
        self.status.Verbose(self, "Row Pos: %d" % self.row_pos)
        self.column_pos = 0
        self.add_i2c_token()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def add_i2c_token(self):
        if self.column_pos == 0:
            self.setRowCount(self.rowCount() + 1)
            self.setColumnCount(2)
            start_token = I2CToken(parent = self,
                                   status = self.status,
                                   actions = self.actions,
                                   row = self.row_pos,
                                   column = column,
                                   loop = self.loop)

            self.setCellWidget(self.row_pos, self.column_pos, start_token)
            i = self.item(self.row_pos, self.column_pos)
            i.setFlags(Qt.ItemIsEnabled)

            self.column_pos += 1
            token = I2CToken(parent = self,
                             status = self.status,
                             actions = self.actions,
                             row = self.row_pos,
                             column = self.column_pos,
                             loop = self.loop)
            self.setCellWidget(self.row_pos, self.column_pos, token)
            i = self.item(self.row_pos, self.column_pos)
            i.setFlags(Qt.ItemIsEnabled)

    def update_i2c_transactions(self, d):
        max_column = 0
        #Update the row count
        #print "Length D: %d" % len(d)

        while self.rowCount() > len(d):
            self.removeRow(len(d))

        if self.rowCount() < len(d):
            self.setRowCount(len(d))

        #Update the column count
        for t in d:
            if len(t) > max_column:
                max_column = len(t)
        self.setColumnCount(max_column)

        #update the actual tokens
        for row in range(len(d)):
            #Updating Transaction
            transaction = d[row]
            for column in range(len(transaction)):
                data_token = transaction[column]
                view_token = self.cellWidget(row, column)
                #print "Token type: %s" % str(type(view_token))
                #If the token is not setup correctly, add it
                if type(view_token) is not I2CToken:
                    view_token = I2CToken(parent = self,
                                          status = self.status,
                                          actions = self.actions,
                                          row = row,
                                          column = column,
                                          loop = self.loop)
                    view_token.set_token_type(data_token["type"])
                    self.setCellWidget(row, column, view_token)

                view_token.set_column(column)
                #print "Token type: %s" % data_token["type"]
                view_token.set_token_type(data_token["type"])
                token_type = data_token["type"]
                if token_type == "Start":
                    view_token.set_default_i2c_slave_address(data_token["address"])
                    view_token.set_rw(data_token["reading"])
                
                elif token_type == "Stop":
                    pass
                
                elif token_type == "Repeat Start":
                    pass
                
                elif token_type == "Write":
                    view_token.set_write_data(data_token["data"])
                
                elif token_type == "Read":
                    view_token.set_read_data(data_token["data"])

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def update_i2c_tokens(self):
        #print "update i2c token: in thread: %s" % str(QThread.currentThread().objectName())
        for r in range(self.rowCount()):
            for t in range(self.columnCount()):
                #There can be a None
                token = self.cellWidget(r, t)
                if token is None:
                    continue
                if type(token) != I2CToken:
                    continue
                token.update_token()


    def update_read_data(self, read_data):
        #print "update read data: in thread: %s" % str(QThread.currentThread().objectName())
        for row in read_data:
            #row = item.keys()[0]
            transaction_data = read_data[row]
            for index in range(len(transaction_data)):
                data = transaction_data[index]
                view_token = self.cellWidget(row, index + 1)
                view_token.set_read_data(data)

