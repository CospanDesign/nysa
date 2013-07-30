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

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "tree_table"))

from tree_table import TreeTableModel
from tree_table import RootNode
from tree_table import BranchNode
from tree_table import LeafNode

from xilinx_xmsgs_parser import XilinxXmsgsParser
from xilinx_xmsgs_parser import XilinxXmsgsParserError

class BuilderNode(BranchNode):
    def __init__(self, name, xp, parent):
        super(BuilderNode, self).__init__(name, parent)
        self.xp = xp
        self.messages = None
        self.filter_type = "all"
        self.delta = "false"

    def update(self, type_filter = [], new_items = False):
        print "Update builder"
        #Update the count of messages
        self.messages = self.xp.get_messages(self.name,
                                             type_filter,
                                             new_items)
        if len(type_filter) == 0:
            self.filter_type = "all"
        else:
            self.filter_type = str(type_filter)

        self.delta = str(new_items)

    def __len__(self):
        #print "Get child length"
        return len(self.messages)

    def field(self, column):
        if column == 0:
            return self.name
        if column == 1:
            return self.filter_type
        if column == 2:
            return self.delta
        return

    def message_field(self, row, column):
        message = self.messages[row]
        if column == 0:
            return message.get('type')
        if column == 1:
            return message.get('delta')
        if column == 2:
            data = ""
            for text in message.itertext():
                data += text
            return data
        return

    def childAtRow(self, row):
        return self.messages[row]

    def rowOfChild(self, child):
        if child in self.messages:
            return self.messages.index(child)
        return -1

    def childWithKey(self, key):
        if key not in range(0, len(self.messages)):
            return None
        return self.messages[key]

class XmsgsTreeModel(TreeTableModel):
    def __init__(self, parent = None):
        super (XmsgsTreeModel, self).__init__(parent)
        self.headers = ["Tool", "Level", "Message"]
        self.initialize(1, self.headers)
        self.xp = XilinxXmsgsParser(self.changed_cb)
        self.path = ""
        self.ready = False

    def ready(self):
        return self.ready

    def set_path(self, path):
        self.path = path
        self.clear()
        try:
            self.xp.watch_path(path)
            self.ready = True
        except TypeError, err:
            self.ready = False
        except XilinxXmsgsParserError, err:
            self.ready = False
        self.reset()

    def changed_cb(self, name):
        print "builder %s has changed" % name
        #Check if the specific builder exists in the root
        #If not add the specific builder to as a new builder node
        builder = self.root.childWithKey(name)
        if builder is None:
            builder = BuilderNode(name, self.xp, self.root)
        builder.update()

    def addRecord(self, nesting, callReset=True):
        pass

    def asRecord(self, index):
        #Is this index the absolute index? or is this relative to a parent
        #It has to be the absolute index because it gives no relative reference
        node = self.nodeFromIndex(index)
        if node is None:
            return []
        if isinstance(node, ET.Element):
            filter_type = node.get("type")
            delta = node.get("delta")
            message = ""
            for text in node.itertext():
                message += text
            return [filter_type, delta, message]
        return []

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int (Qt.AlignTop | Qt.AlignLeft)
        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            if node is None:
                return None

        if role  != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        if node is None:
            return None

    def index(self, row, column, parent_index):
        assert self.root
        print "Get index of %d %d, with parent index: %s" % (row, column, str(parent_index))
        parent = self.nodeFromIndex(parent_index)
        return self.createIndex(row, column, parent.childAtRow(row))
        
    def parent(self, child):
        parent = self.root
        print "Get parent of %s" % str(child)
        #Check if this type is the root node, if so, just return root node
        if isinstance(child, RootNode):
            return self.root
        #if this type is a BuilderNode return the name of the builder
        if isinstance(child, BuilderNode):
            return self.root
        #if this type is an Element from an XML tree, need to find the builder
        if isinstance(child, ET.Element):
            builder = child.get("builder")
            parent = root.childWithKey(builder)

    def status_available(self, builder):
        return builder_exists(builder)


    def pass_with_warnings(self, builder):
        try:
            if len (self.xp.get_messages(builder,
                                         type_filters = ["warning"])) > 0:
                return True
        except XilinxXmsgsParserError, err:
            #This means we don't have any messages
            return False

        return False

    def failed(self, builder):
        try:
            if len(self.xp.get_messages(builder,
                                    type_filters = ["error"])) > 0:
                return True

        except XilinxXmsgsParserError, err:
            #This means we don't have any messages
            return False

        return False
