import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_gpio_action_instance = None

#Singleton Magic
def GPIOActions(*args, **kw):
    global _gpio_action_instance
    if _gpio_action_instance is None:
        _gpio_action_instance = _GPIOActions(*args, **kw)
    return _gpio_action_instance

class _GPIOActions(QtCore.QObject):

    #Raw Register signals
    get_pressed = QtCore.pyqtSignal(int, name = "get_pressed")
    set_pressed = QtCore.pyqtSignal(int, int, name = "set_pressed")

    read_rate_change = QtCore.pyqtSignal(int, name = "read_rate_change")
    read_start_stop = QtCore.pyqtSignal(bool, float, name = "read_start_stop")

    #GPIO Specific signals
    gpio_input_changed = QtCore.pyqtSignal(int, name = "gpio_in_changed")
    gpio_out_changed = QtCore.pyqtSignal(int, bool, name = "gpio_out_changed")
    direction_changed = QtCore.pyqtSignal(int, bool, name = "direction_changed")
    interrupt_en_changed = QtCore.pyqtSignal(int, bool, name = "interrupt_en_changed")
    interrupt_edge_changed = QtCore.pyqtSignal(int, bool, name = "interrupt_edge_changed")



    def __init__(self, parent = None):
        super (_GPIOActions, self).__init__(parent)
        print "Started"

