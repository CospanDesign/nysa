from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Node(object):
    def __init__(self, name = "", parent = None):
        self._name = name
        self._children_dict = {}
        self._children_list = []
        self._parent = parent

    def name(self):
        return self._name

    def parent(self):
        if self._parent is not None:
            return self._parent
        return None

    def add_child(self, child):
        print "Adding Child with name: %s" % child.name()
        self._children_dict[child.name()] = child
        self._children_list.append(child)

    def insert_child(self, row, child):
        print "Adding Child with name: %s" % child.name()
        self._children_dict[child.name()] = child
        self._children_list.insert(row, child)

    def child(self, row = None, name = None):
        if isinstance(row, int):
            return self._children_list[row]
        if name in self._children_dict.keys():
            return self._children_dict[name]
        return None

    def child_count(self):
        return len(self._children_list)

    def remove_child(self, child):
        name = child.name()
        if name in self._children_dict.keys():
            del(self._children_dict[name])
        if child in self._children_list:
            self._children_list.remove(child)

    def row(self):
        if self._parent is not None:
            return self._parent._children_list.index(self)
        return None
            

class RootNode(Node):
    def __init__(self):
        super(RootNode, self).__init__(name = "root")

class TreeModel(QAbstractItemModel):
    def __init__(self, parent = None, headers = [], nesting = 1):
        super(TreeModel, self).__init__(parent)
        self.root = RootNode()
        self.headers = headers
        self.nesting = nesting
        self.insertRow(0, QModelIndex())

    def rowCount(self, parent_index):
        parent = node_from_index(parent_index)
        if isinstance(parent, RootNode):
            return parent.child_count()
        pass

    def columnCount(self, parent):
        return len(self.headers)

    #def flags(self, index):
    #    pass
    def data(self, index, role):
        pass

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                assert 0 <= section <= len(self.headers)
                return self.headers[section]

    def index(self, row, column, parent):
        pass

    def parent(self, child):
        node = index.internalPointer()
        #Now I have a pointer to the child
        return node.parent()

    def clear(self):
        self.root = RootNode()
        self.reset()

    def node_from_index(self, index):
        if index.isValid():
            #Index is valid
            return index.internalPointer()
        #else:
        #    print "index: %d, %d, type: %s" % (index.row(), index.column(), type(index))
        return self.root


