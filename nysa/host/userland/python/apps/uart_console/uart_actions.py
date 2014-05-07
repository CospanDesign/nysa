import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_uart_action_instance = None

#Singleton Magic
def UARTActions(*args, **kw):
    global _uart_action_instance
    if _uart_action_instance is None:
        _uart_action_instance = _UARTActions(*args, **kw)
    return _uart_action_instance

class _UARTActions(QtCore.QObject):

    #Update Write Data Model
    uart_baudrate_change = QtCore.pyqtSignal(int, name = "uart_baudrate_change")
    uart_local_echo_en = QtCore.pyqtSignal(bool, name = "uart_local_echo_en")
    uart_flowcontrol_change = QtCore.pyqtSignal(str, name = "uart_flowcontrol_change")

    def __init__(self, parent = None):
        super (_UARTActions, self).__init__(parent)

