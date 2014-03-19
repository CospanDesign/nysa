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
    refresh_signal = QtCore.pyqtSignal(name = "refresh_platform")

    clear_platform_tree_signal = QtCore.pyqtSignal(name = "clear_platform_tree")
    add_device_signal = QtCore.pyqtSignal(str, str, object, name = "add_device")
    remove_device_signal = QtCore.pyqtSignal(str, str, name = "remove_device")

    #View Signals
    platform_tree_changed_signal = QtCore.pyqtSignal(object, object, object, name = "platform_tree_changed")
    platform_tree_get_first_dev = QtCore.pyqtSignal(name = "platform_tree_first_dev")

    module_selected = QtCore.pyqtSignal(str, name = "module_selected")
    module_deselected = QtCore.pyqtSignal(str, name = "module_deselected")

    slave_selected = QtCore.pyqtSignal(str, str, name = "slave_selected")
    slave_deselected = QtCore.pyqtSignal(str, str, name = "slave_deselected")

    script_item_selected = QtCore.pyqtSignal(str, object, name = "script_item_selected")
    remove_tab = QtCore.pyqtSignal(object, name = "remove_tab")


    def __init__(self, parent = None):
        super (_Actions, self).__init__(parent)

