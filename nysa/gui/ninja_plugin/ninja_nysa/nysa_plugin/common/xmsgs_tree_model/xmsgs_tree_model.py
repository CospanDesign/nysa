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
import xml.etree.ElementTree as ET

from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "tree_table"))

from xilinx_xmsgs_parser import XilinxXmsgsParser
from xilinx_xmsgs_parser import XilinxXmsgsParserError

from tree_model import Node
from tree_model import TreeModel
from tree_model import RootNode

builder_names = ["xst", "ngdbuild", "map", "par", "bitgen", "trce"]

class BuilderNode(Node):
    def __init__(self, name, xp, tree_model, parent):
        super(BuilderNode, self).__init__(name, parent)
        self.xp = xp
        self.tree_model = tree_model
        self.messages = None
        self.filter_type = "all"
        self.delta = "false"


    def update(self, type_filter = [], new_items = False):
        #Update the count of messages
        self._children = self.xp.get_messages(self.name(),
                                              type_filter,
                                              new_items)
        if len(type_filter) == 0:
            self.filter_type = "all"
        else:
            self.filter_type = str(type_filter)

        #print "\tnumber of messages: %d" % len(self.messages)
        self.delta = str(new_items)
        parent_index = self.tree_model.createIndex(self.row(), 0, self )
        #self.tree_model.beginInsertRows(parent_index, 0, len(self._children) - 1) 
        for index in range(len(self._children)):
            #self.tree_model.insertRow(1, parent_index)
            message = self._children[index]
            #for message in self._children:
            message.set("builder", self.name())
            self.tree_model.createIndex(index, 0, message)
        #self.tree_model.endInsertRows()

    #Override Node Default Functions
    def child(self, row):
        return self._children[row]

    def child_count(self):
        return len(self._children)

    def field(self, column):
        if column == 0:
            return self.name()
        if column == 1:
            #return self.filter_type
            return ""
        if column == 2:
            #return self.delta
            return ""
        return

    def message_field(self, row, column):
        message = self._children[row]
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

class XmsgsTreeModel(TreeModel):
    def __init__(self, parent = None):
        super (XmsgsTreeModel, self).__init__(parent)
        self.headers = ["Tool", "Level", "Message"]
        self.xp = XilinxXmsgsParser(self.changed_cb)
        self.path = ""
        self.ready = False

    def data(self, index, role):
        #Text Alignment Data
        if role == Qt.TextAlignmentRole:
            return int (Qt.AlignTop | Qt.AlignLeft)

        #Icons/Color
        if role == Qt.DecorationRole:

            node = self.node_from_index(index)
            if node is None:
                return None

        #If not data to fill a box bail
        if role != Qt.DisplayRole:
            return

        node = self.node_from_index(index)
        assert node is not None

        if isinstance(node, RootNode):
            return None
        if isinstance(node, BuilderNode):
            return node.field(index.column())
        if isinstance(node, ET.Element):
            name = node.get("builder")
            builder = self.root.child(name = name)
            return builder.message_field(index.row(), index.column())

        print "Get Data for other type"

    def hasChildren(self, index):
        node = self.node_from_index(index)
        if isinstance(node, RootNode):
            return True
        if isinstance(node, BuilderNode):
            return True
        return False

    def rowCount(self, parent_index):
        if parent_index.row() != -1:
            print "Parent index: %d, %d" % (parent_index.row(), parent_index.column())
        node = self.node_from_index(parent_index)
        print "\trowCount Type: %s" % node.name()
        if node is None:
            return 0
        print "Child Count: %d" % node.child_count()
        return node.child_count()

    def index(self, row, column, parent_index):
        assert self.root

        parent_node = self.node_from_index(parent_index)
        if isinstance(parent_node, RootNode):
            child = parent_node.child(row)
            #print "Parent: %s, child: %s" % (parent_node.name(), child.name())
            
            return self.createIndex(row, column, child)
        if isinstance(parent_node, BuilderNode):
            #child = parent_node.child(row)
            child = parent_node.child(row)
            print "Parent: %s, child is message" % (parent_node.name())
            return self.createIndex(row, column, child)
        print "Unrecognized type"
        #print "index: %d, %d: parent_index = %d, %d" % (row, column, parent_index.row(), parent_index.column())
        #return self.createIndex(row, column, node)

    def parent(self, child_index):
        child = self.node_from_index(child_index)
        if child is None:
            print "parent: child is none"
            return None
        if isinstance(child, BuilderNode):
            #print "Child name: %s" % child.name()
            return self.createIndex(0, 0, self.root)
        if isinstance(child, ET.Element):
            name = child.get("builder")
            builder = self.root.child(name = name)
            return self.createIndex(builder.row(), 0, builder)
        print "Unknown child: %s" % type(child)

    def reset(self):
        print "______RESET______"
        QAbstractItemModel.reset(self)

    #Functions for use by non table interface
    def changed_cb(self, name):
        #Check if the specific builder exists in the root
        #If not add the specific builder to as a new builder node
        builder = self.root.child(name)
        if builder is None:
            builder = BuilderNode(name, self.xp, self, self.root)
            print "Insert %s into root" % name
            bs = self.root._children_list
            keys = []
            for b in bs:
                keys.append(b.name())
            if len(keys) == 0:
                print "List is empty"
                self.root.add_child(builder)
            else:
                #List is shorter than where we need to be put in
                name_index = builder_names.index(name)
                print "insert %s into list: %s" % (name, keys)
                print "\tname index: %d" % name_index
                for key in keys:
                    key_index = builder_names.index(key)

                    if name_index < key_index:
                        print "%s is before %s" % (name, key)
                        self.root.insert_child(row = keys.index(key), child=builder)
                        break

            #self.root.add_child(builder)

        builder.update()
        self.reset()
        #self.emit(SIGNAL("dataChanged()"))

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

    def ready(self):
        return self.ready

    def set_path(self, path):
        self.path = path
        self.clear()
        try:
            self.xp.watch_path(path)
        except TypeError, err:
            self.ready = False
        except XilinxXmsgsParserError, err:
            self.ready = False
        self.reset()

