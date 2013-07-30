#!/usr/bin/env python
# Copyright (c) 2007-8 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.


"""
This code was mostly taken from the Rapid Gui Development with Python and Qt

as such this file uses the GNU copyright

by: Mark Summerfield

"""
import bisect
import codecs
from PyQt4.QtCore import *
from PyQt4.QtGui import *

KEY, NODE = range(2)


class BranchNode(object):

    def __init__(self, name, parent=None):
        super(BranchNode, self).__init__()
        self.name = name
        self.parent = parent
        self.children = []

    def orderKey(self):
        return self.name.lower()

    def toString(self):
        return self.name

    def __len__(self):
        return len(self.children)

    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row][NODE]

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1

    def childWithKey(self, key):
        if not self.children:
            return None
        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        return None

    def insertChild(self, child):
        child.parent = self
        bisect.insort(self.children, (child.orderKey(), child))

    def removeChild(self, child):
        #assert child in self.children[NODE]:
        self.children.remove(child)

    def hasLeaves(self):
        if not self.children:
            return False
        return isinstance(self.children[0], LeafNode)

class RootNode(BranchNode):

    def __init__(self, name, parent=None):
        super(RootNode, self).__init__(name, parent)

class LeafNode(QObject):

    def __init__(self, fields, parent=None):
        super(LeafNode, self).__init__()
        self.parent = parent
        self.fields = fields

    def orderKey(self):
        return u"\t".join(self.fields).lower()

    def toString(self, separator="\t"):
        return separator.join(self.fields)

    def __len__(self):
        return len(self.fields)

    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            record.insert(0, branch.toString())
            branch = branch.parent
        assert record and not record[0]
        record = record[1:]
        return record + self.fields

    def field(self, column):
        assert 0 <= column <= len(self.fields)
        return self.fields[column]

class TreeTableModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super(TreeTableModel, self).__init__(parent)
        self.root = RootNode("")
        self.headers = []
        self.columns = 0

    def initialize(self, nesting, headers):
        assert nesting > 0
        self.nesting = nesting
        self.root = RootNode("")
        assert headers > 0
        self.headers = headers
        self.columns = len(self.headers)

    def addRecord(self, fields, callReset=True):
        print "TT: add record"
        assert len(fields) > self.nesting
        root = self.root
        branch = None
        for i in range(self.nesting):
            #Go through each of the nesting layers
            key = fields[i].lower()
            #get the branch from the child
            branch = root.childWithKey(key)
            if branch is not None:
                #Branch either has no children (empty)
                #key is not in the children
                #referench to the root
                root = branch
            else:
                #Create a new branch
                branch = BranchNode(fields[i])
                root.insertChild(branch)
                root = branch
        assert branch is not None
        items = fields[self.nesting:]
        self.columns = max(self.columns, len(items))
        #add a leaf of the branch
        branch.insertChild(LeafNode(items, branch))
        if callReset:
            self.reset()

    def asRecord(self, index):
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.asRecord()
        return []

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)

    def columnCount(self, parent):
        return self.columns

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            #print "TT: TextAlignmentRole"
            return int(Qt.AlignTop|Qt.AlignLeft)
        if role != Qt.DisplayRole:
            #print "TT: not Display Role"
            #return QVariant()
            return
        node = self.nodeFromIndex(index)
        assert node is not None
        if isinstance(node, RoothNode):
            #Root is none
            return ""
        return node.field(index.column())

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and \
           role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            #return QVariant(self.headers[section])
            return self.headers[section]

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))

    def parent(self, child): 
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        if isinstance(node, tuple):
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()

        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.root

    def clear(self):
        self.root = RootNode("")
        self.reset()

