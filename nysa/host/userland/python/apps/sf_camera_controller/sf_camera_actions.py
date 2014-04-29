import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_sf_camera_action_instance = None

#Singleton Magic
def SFCameraActions(*args, **kw):
    global _sf_camera_action_instance
    if _sf_camera_action_instance is None:
        _sf_camera_action_instance = _SFCameraActions(*args, **kw)
    return _sf_camera_action_instance

class _SFCameraActions(QtCore.QObject):

    #Image Signals
    sf_camera_read_ready = QtCore.pyqtSignal(object, name = "sf_camera_read_ready")
 
    #Control
    sf_camera_run = QtCore.pyqtSignal(name = "sf_camera_run")
    sf_camera_stop = QtCore.pyqtSignal(name = "sf_camera_stop")
    sf_camera_reset = QtCore.pyqtSignal(name = "sf_camera_reset")
