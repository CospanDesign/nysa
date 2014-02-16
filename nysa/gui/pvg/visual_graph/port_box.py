'''
Log
  1/09/2014: Initial commit
'''

__author__ = "Dave McCoy dave.mccoy@cospandesign.com"

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from defines import direc

from link import Link
from link import side_type as st

from box import Box
from port import Port


class PortBox(Box):

    def __init__(self,
                 name,
                 color,
                 scene = None,
                 graphics_widget = None,
                 position = QPointF(0, 0),
                 user_data = None):
        if scene is None:
            if graphics_widget is None:
                raise Exception("Need a better exception")
            scene = graphics_widget.scene
        super(PortBox, self).__init__(position = position,
                                      scene = scene,
                                      name = name,
                                      color = color,
                                      user_data = user_data)

        self.ports = {}
        self.ports["input"] = {}
        self.ports["output"] = {}
        self.ports["inout"] = {}

        self.ports_group = ["ngroup"]

        self.connections = {}
        self.removed = False
        #Generate a random number so cores of the same name can exist

    def add_port_group(self, name):
        if name not in self.ports_group:
            self.ports_group.append(name)

    def remove_port_group(self, name):
        if name in self.ports_group:
            self.ports.remove(name)

    def add_port(self, direction, name, bus_range = 1, port_group = None):
        if((direction != "input") or
           (direction != "output") or
           (direction != "inout")):
          raise Exception("%s is not direction!" % direction)

        self.ports[direction][name] = {}
        self.ports[direction][name]["range"] = {}

        if self.port_group is None:
            #self.ports_group["ngroup"] = 
            pass
            
    def remove_port(self, direction, name):
        if  ((direction != "input") or
             (direction != "output") or
             (direction != "inout")):
            raise Exception ("%s is not direction!" % direction)

        if name not in self.ports[direction]:
            raise Exception ("%s is not inside ports" % name)

        del (self.ports[direction][name])
 
    def add_connection(self, output_port, port_box, input_port):
        if ((output_port not in self.ports["output"]) or
            (output_port not in self.ports["inout"])):
            if output_port not in self.connections:
                self.connections[output_port] = {}

            if port_box not in self.connections[output_port]:
                self.connections[output_port][port_box] = []

            if input_port not in self.connections[output_port][port_box]:
                self.connections[output_port][port_box].append(input_port)


    def remove_connection(self, port_box, input_port = None):
        if ((port_box not in self.connections["output"]) and
            (port_box not in self.connections["inout"])):
            return
        if input_port is None:
            #The user is deleting all connections to the specified box
            if port_box in self.connections["output"]:
                del(self.connections["output"][port_box])
            if port_box in self.connections["inout"]:
                del(self.connections["inout"][port_box])
            return

        if ((input_port not in self.connections["output"][port_box]) and
            (input_port not in self.connections["inout"][port_box])):
            #Couldn't find the port in the list of connections
            return

        if port_box not in self.connections["output"]:
            #Remove the specified connection
            self.connections[output_port][port_box].remove(input_port)
            if len(self.connections[output_port][port_box]) == 0:
                #No more connections remove the rest
                del(self.connections[output_port][port_box])

        if port_box not in self.connections["inout"]:
            #Remove the specified connection
            self.connections[output_port][port_box].remove(input_port)
            if len(self.connections[output_port][port_box]) == 0:
                #No more connections remove the rest
                del(self.connections[output_port][port_box])

    def remove(self):
        self.removed = True

    def is_removed(self):
        #We need this because during an update the graph may still have a reference to this connection
        #if so we need to remove it from our own graph
        return self.removed()

    def get_global_port_pos(self, direction, port_name):
        p = self.ports[direction][port_name]

    #Paint
    def paint(self, painter, option, widget):

        #Draw Rectangle
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        self.set_pen_border(option, pen)

        painter.setPen(pen)
        painter.drawRect(self.rect)
        painter.fillRect(self.rect, QColor(self.color))
        painter.setFont(self.text_font)

        #draw text
        pen.setColor(Qt.black)
        painter.setPen(pen)

        self.add_label_to_rect(painter, self.rect, self.box_name)

        for group in self.ports_group:
            print "Port Group: %s" % group
            #Create a sub box for everything
            #Get the size of this port box
            #First find the number of input and output ports


        '''
        for i in range(0, len(self.arbitor_masters)):
            #print "Add Arbitor %s" % self.arbitor_masters[i]
            arb_rect = QRectF(ARB_MASTER_RECT)

            am = ArbitorMaster(name = self.arbitor_masters[i], 
                               position = arb_pos,
                               y_pos = position.y(),
                               scene = self.scene(),
                               slave = self)

            #am.movable(False)

            self.arbitor_boxes.append(am)
            al = Link(self, am, self.scene(), lt.arbitor_master)
            al.from_box_side(st.right)
            al.to_box_side(st.left)

            al.en_bezier_connections(True)
            self.links[am] = al

            #Progress the position
            arb_pos = QPointF(arb_pos.x(), arb_pos.y() + arb_rect.height() + ARB_MASTER_VERTICAL_SPACING)
        '''


