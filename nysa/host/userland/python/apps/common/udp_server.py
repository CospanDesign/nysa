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


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import json

from PyQt4 import QtCore
from PyQt4 import QtNetwork

#os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "common")

class UDPServerWorker(QtCore.QObject):
    udp_send_data = QtCore.pyqtSignal(str, name="udp_send_data")

    def __init__(self, socket, port, actions):
        super (UDPServerWorker, self).__init__()
        self.socket = socket
        self.port = port
        self.actions = actions
        self.udp_send_data.connect(self.send_data)

    def send_data(self, data):
        print "Sending Data: %s" % data

        self.socket.writeDatagram(data, QtNetwork.QHostAddress.LocalHost, self.port)
        #self.socket.writeDatagram("hi", QtNetwork.QHostAddress.LocalHost, self.port)
        print "Finished!"

'''
class UdpWorker(QtCore.QRunnable):
    def __init__(self, data, udp_socket, port):
        self.port = port
        self.socket = udp_socket
        self.data = data

    def run(self):
        self.socket.writeDatagram(data, QtNetwork.QHostAddress.Broadcast, self.port)
'''

class UDPServer(QtCore.QObject):

    def __init__(self, status, actions, port):
        super (UDPServer, self).__init__()
        self.port = port
        self.udp_socket = QtNetwork.QUdpSocket(self)
        self.worker_thread = QtCore.QThread()
        self.status = status
        self.actions = actions

        self.status.Verbose(self, "Starting UDP Server on Port 0x%0X" % self.port)
        self.worker = UDPServerWorker(self.udp_socket,
                                      self.port,
                                      self.actions)

        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.finished.connect(self.work_finished)
        #self.connect(self.worker_thread, SIGNAL("finished"), self.work_finished)

        #self.thread_pool = QtCore.QThreadPool(self)
        #self.thread_pool.setMaxThreadCount(1)
        #self.thread = QtCore.QThread()
        #connect(self.thread, SIGNAL(finished()), worker, SLOT(deleteLater())


    def write_data(self, data):
        self.status.Verbose(self, "Sending Data")
        #Need to create a QByteArray
        self.worker.udp_send_data.emit(data)
        #self.upd_socket.writeDatagram(data, QtNetwork.QHostAddress.Broadcast, self.port)

    def work_finished(self):
        self.status.Verbose(self, "Data Sent")

