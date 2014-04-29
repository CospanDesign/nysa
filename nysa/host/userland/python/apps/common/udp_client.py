#!/usr/bin/python

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

import sys
import os
import json

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtNetwork


class UDPClient(QtCore.QObject):
    def __init__(self):
        super (UDPClient, self).__init__()
        self.socket = QtNetwork.QUdpSocket()
        #self.socket.bind(QtNetwork.QHostAddress.Broadcast, 0xc594, QtNetwork.QUdpSocket.ShareAddress)
        self.socket.bind(QtNetwork.QHostAddress.LocalHost, 0xC594)
        self.socket.readyRead.connect(self.receiver)
        print "UDP Client initialized"

    def receiver(self):
        print "Receiving Data"
        while (self.socket.hasPendingDatagrams()):
            size = self.socket.pendingDatagramSize()
            msg, host, port = self.socket.readDatagram(size)
            #msg = msg.replace("\\", "")
            data = json.loads(msg)
            print ("Data:\n%s" % str(data))
            print ("Type: %s" % data["type"])

class Example(QtGui.QWidget):
  def __init__(self):
    super(Example, self).__init__()
    self.initUI()
    self.udp_client = UDPClient()

  def initUI(self):
    self.resize(250, 150)
    self.center()

    self.setWindowTitle('Center')
    self.show()


  def center(self):
    qr = self.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


def main():
  app = QtGui.QApplication(sys.argv)
  ex = Example()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()


