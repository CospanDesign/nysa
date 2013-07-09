# -*- coding: utf-8 -*-


#the idea for this module was taken from the Ninja-IDE Actions Module


from __future__ import absolute_import

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from project.ibuilder import ibuilder
__nysaActionsInstance = None


# Singleton!
def NysaActions(*args, **kw):
    global __nysaActionsInstance
    if __nysaActionsInstance is None:
        __nysaActionsInstance = _NysaActions(*args, **kw)
    return __nysaActionsInstance

class _NysaActions(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.ibuilder = None
        self.cbuilder = None
        self.host = None
        self.nysa_plugin = None

    def setup_signals(self):
        print "Setup Signals"

    def set_nysa_plugin(self, nysa_plugin):
        self.nysa_plugin = nysa_plugin

    def set_ibuilder(self, ibuilder):
        self.ibuilder = ibuilder

    def set_cbuilder(self, cbuilder):
        self.cbuilder = cbuilder
        self.connect(self.cbuilder, SIGNAL("module_built(QString)"), self._module_built)

    def set_host(self, host):
        self.host = host

    def _module_built(self, module_name):
        self.emit(SIGNAL("module_built(QString)"), module_name)

    def ibuilder_properties_triggered(self, directory):
        self.emit(SIGNAL("ibuilder_properties_dialog(QString)"), directory)

