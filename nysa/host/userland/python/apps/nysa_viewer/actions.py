import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_action_instance = None

#Singleton Magic
def Actions(*args, **kw):
    global _action_instance
    if _action_instance is None:
        _action_instance = _Actions(*args, **kw)
    return _action_instance

class _Actions(QtCore.QObject):

    #Control Signals
    refresh_signal = QtCore.pyqtSignal(name = "refresh_phy")

    clear_phy_tree_signal = QtCore.pyqtSignal(name = "clear_phy_tree")
    add_device_signal = QtCore.pyqtSignal(str, str, object, name = "add_device")
    remove_device_signal = QtCore.pyqtSignal(str, str, name = "remove_device")

    #View Signals
    phy_tree_changed_signal = QtCore.pyqtSignal(object, object, object, name = "phy_tree_changed")
    phy_tree_get_first_dev = QtCore.pyqtSignal(name = "phy_tree_first_dev")

    def __init__(self, parent = None):
        super (_Actions, self).__init__(parent)

