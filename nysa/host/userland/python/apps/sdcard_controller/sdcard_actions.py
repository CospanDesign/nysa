import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_sdcard_action_instance = None

#Singleton Magic
def SDCARDActions(*args, **kw):
    global _sdcard_action_instance
    if _sdcard_action_instance is None:
        _sdcard_action_instance = _SDCARDActions(*args, **kw)
    return _sdcard_action_instance

class _SDCARDActions(QtCore.QObject):

    #SDCARD Execution Control
    sdcard_read_status = QtCore.pyqtSignal(int, name = "sdcard_read_status")
    sdcard_reset = QtCore.pyqtSignal(name = "sdcard_reset_finished")

    def __init__(self, parent = None):
        super (_SDCARDActions, self).__init__(parent)

