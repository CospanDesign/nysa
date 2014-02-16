__author__ = "Dave McCoy dave.mccoy@cospandesign.com"

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from defines import direc

from link import Link
from link import side_type as st

from box import Box
from port import Port

class Port(object):
    def __init__(self, name, direction, group = None, port_range = 1):
        self.name = name
        self.direction = direction
        self.group = group

class Signal(object):
    def __init__(self, name, cnct_module, cnct_module_port_name, signal_range = [1], start_range = 0):
        self.name = name
        self.module_
        self.port_name = name

class ModuleBox (Box):
    def __init__(self,
                 name,
                 color,
                 scene,
                 graphics_widget,
                 position = QPointF(0, 0),
                 user_data = None):
        super(ModuleBox, self).__init__(position = position,
                                        scene = scene,
                                        name = name,
                                        color = color,
                                        user_data = user_data)
        self.ports = {}
        self.signals = {}
        self.connections = {}
        self.removed = False

    def add_port(self, port_name, direction, group = None, port_range = 1):
        self.ports[port_name] = Port(name, direction, group, port_range)

    def remove_port(self, port_name):
        if port_name in self.ports:
            del(self.ports[port_name])
