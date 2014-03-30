import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_memory_action_instance = None

#Singleton Magic
def MemoryActions(*args, **kw):
    global _memory_action_instance
    if _memory_action_instance is None:
        _memory_action_instance = _MemoryActions(*args, **kw)
    return _memory_action_instance

class _MemoryActions(QtCore.QObject):

    #Memory Test
    memory_test_start = QtCore.pyqtSignal(name = "memory_test_start")
    memory_read_finished = QtCore.pyqtSignal(str, name = "memory_read_finished")


    def __init__(self, parent = None):
        super (_MemoryActions, self).__init__(parent)
        print "Started Memory Actions"

