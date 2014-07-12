import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_stepper_action_instance = None

#Singleton Magic
def StepperActions(*args, **kw):
    global _stepper_action_instance
    if _stepper_action_instance is None:
        _stepper_action_instance = _StepperActions(*args, **kw)
    return _stepper_action_instance

class _StepperActions(QtCore.QObject):

    #Stepper Execution Control
    stepper_read_status = QtCore.pyqtSignal(int, name = "stepper_read_status")
    stepper_reset = QtCore.pyqtSignal(name = "stepper_reset_finished")
    stepper_update_angle = QtCore.pyqtSignal(float, name = "stepper_update_angle")
    stepper_initial_angle = QtCore.pyqtSignal(float, name = "stepper_initial_angle")
    stepper_move_event = QtCore.pyqtSignal(float, name = "stepper_move_event")
    stepper_update_step_type = QtCore.pyqtSignal(int, name = "stepper_update_step_type")

    stepper_update_clock_rate = QtCore.pyqtSignal(int, name = "stepper_update_clock_rate")
    stepper_update_configuration = QtCore.pyqtSignal(object, name = "stepper_update_configuration")

    stepper_update_register = QtCore.pyqtSignal(int, int, name = "stepper_update_register")
    stepper_update_actual_angle = QtCore.pyqtSignal(float, name = "stepper_update_actual_arm")

    #stepper_response = QtCore.pyqtSignal(object, name = "stepper_transaction_response")

    def __init__(self, parent = None):
        super (_StepperActions, self).__init__(parent)

