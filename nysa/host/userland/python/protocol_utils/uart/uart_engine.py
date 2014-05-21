# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


"""
UART Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import time
import json

from array import array as Array

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))
from driver.uart import UARTError



class UARTEngineError(Exception):
    pass

class UARTEngineWorker(QObject):

    finished = QtCore.pyqtSignal()
    dataReady = QtCore.pyqtSignal(list, dict)

    def __init__(self):
        super (UARTEngineWorker, self).__init__()

    @QtCore.pyqtSlot(object, object, object, object)
    def thread_init(self, uart, mutex, actions, status):
        self.uart = uart
        self.mutex = mutex
        self.actions = actions
        self.status = status

        self.term_flag = False
        self.actions = actions

    @QtCore.pyqtSlot()
    def process(self):
        #Get all the data from the UART
        data = self.uart.read_all_data()
        self.uart.get_status()
        if len(data) > 0:
            self.actions.uart_data_in.emit(data.tostring())

class UARTThread(QtCore.QThread):
    def __init__(self):
        super (UARTThread, self).__init__()

    def start(self):
        super (UARTThread, self).start()

    def run(self):
        super (UARTThread, self).run()

class UARTEngine(QObject):

    def __init__(self, uart, actions, status):
        super (UARTEngine, self).__init__()
        self.actions = actions
        self.status = status
        self.status.Verbose(self, "Started")
        self.mutex = QtCore.QMutex()
        self.uart = uart

        #Create the thread and worker
        self.engine_thread = UARTThread()
        self.engine_worker = UARTEngineWorker()

        self.engine_worker.moveToThread(self.engine_thread)
        self.engine_thread.start()


        QtCore.QMetaObject.invokeMethod(self.engine_worker, 
                                        'thread_init',
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, self.uart),
                                        QtCore.Q_ARG(object, self.mutex),
                                        QtCore.Q_ARG(object, self.actions),
                                        QtCore.Q_ARG(object, self.status))

        self.uart.unregister_interrupt_callback(None)
        self.uart.register_interrupt_callback(self.interrupt_callback)

    def interrupt_callback(self):
        print "Interrupt callback"
        QtCore.QMetaObject.invokeMethod(self.engine_worker,
                                        "process",
                                        QtCore.Qt.QueuedConnection)


