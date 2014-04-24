import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_i2c_action_instance = None

#Singleton Magic
def I2CActions(*args, **kw):
    global _i2c_action_instance
    if _i2c_action_instance is None:
        _i2c_action_instance = _I2CActions(*args, **kw)
    return _i2c_action_instance

class _I2CActions(QtCore.QObject):

    #Token Add/Remove 
    i2c_token_add = QtCore.pyqtSignal(bool, int, int, name = "i2c_token_add")
    i2c_token_remove = QtCore.pyqtSignal(bool, int, int, name = "i2c_token_remove")

    #Adding Removing I2C Rows
    i2c_row_add = QtCore.pyqtSignal(bool, name = "i2c_row_add")
    i2c_row_delete = QtCore.pyqtSignal(bool, name = "i2c_row_delete")

    #I2C Execution Control
    i2c_run = QtCore.pyqtSignal(name = "i2c_run")
    i2c_pause = QtCore.pyqtSignal(name = "i2c_pause")
    i2c_reset = QtCore.pyqtSignal(name = "i2c_reset")
    i2c_stop = QtCore.pyqtSignal(name = "i2c_stop")
    i2c_step = QtCore.pyqtSignal(name = "i2c_step")
    i2c_loop_step = QtCore.pyqtSignal(name = "i2c_loop_step")

    i2c_execute_delay_change = QtCore.pyqtSignal(int, name = "i2c_execute_delay_change")

    #I2C Execution Status
    i2c_execute_status_update = QtCore.pyqtSignal(str, name = "i2c_execute_status_update")

    #Default Base Address
    i2c_default_i2c_address = QtCore.pyqtSignal(int, name = "i2c_default_i2c_address")

    #Characteristics of i2c tokens
    i2c_reading_row_changed = QtCore.pyqtSignal(int, bool, bool, name = "i2c_reading_row_changed")
    i2c_token_changed = QtCore.pyqtSignal(bool, int, int, object, name = "i2c_select_changed")
    i2c_ack_changed = QtCore.pyqtSignal(bool, int, int, bool, name = "i2c_ack_required_changed")

    #Update View
    i2c_update_view = QtCore.pyqtSignal(bool, object, name = "i2c_update_view")
    i2c_update_read_view = QtCore.pyqtSignal(bool, object, name = "i2c_read_update")

    #Update Write Data Model
    i2c_update_write = QtCore.pyqtSignal(bool, int, int, int, name = "i2c_update_write")



    def __init__(self, parent = None):
        super (_I2CActions, self).__init__(parent)

