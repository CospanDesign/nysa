
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


""" stepper configuration view
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import math

from PyQt4.QtGui import *
from PyQt4.QtCore import *

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "gui",
                             "pvg")

p = os.path.abspath(p)
#print ("Dir: %s" % p)
sys.path.append(p)

RECT_SIZE = 200.0
CIRCLE_SIZE = 200.0
CENTER_POINT_SIZE = 50.0

USER_RECT = (25, 100)
USER_RECT_COLOR = QColor(Qt.green)

from visual_graph.graphics_widget import GraphicsWidget
from visual_graph.graphics_view import GraphicsView

class StepperMotorWidget(QWidget):
    def __init__(self, status, actions):

        self.status = status
        self.actions = actions

        super(StepperMotorWidget, self).__init__()
        self.setMinimumWidth(300)
        self.view = GraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.stepper_motor = StepperGraphicsItem(self)

        self.actual_arm = StepperMotorArm(self.status,
                                          self.actions,
                                          USER_RECT_COLOR,
                                          solid = False,
                                          movable = True)
        self.user_arm = StepperMotorArm(  self.status,
                                          self.actions,
                                          USER_RECT_COLOR,
                                          solid = True,
                                          movable = False)

        self.scene.addItem(self.stepper_motor)
        self.scene.addItem(self.actual_arm)
        self.scene.addItem(self.user_arm)
        l = QHBoxLayout()
        l.addWidget(self.view)
        self.setLayout(l)

        self.show()


class StepperGraphicsItem (QGraphicsItem):
    """Generic box used for flow charts"""

    def __init__(self,
                 parent):

        super(StepperGraphicsItem, self).__init__()
        #StepperGraphicsItem Properties
        self.parent = parent

        self.rect = QRectF(                 -RECT_SIZE,
                                            -RECT_SIZE,
                                             RECT_SIZE,
                                             RECT_SIZE)


        self.style = Qt.SolidLine
        self.setPos(QPoint(0.0, 0.0))
        self.setMatrix(QMatrix())
        self.sm_brush = QBrush(Qt.blue)
        self.cp_brush = QBrush(Qt.black)

        self.controller_angle = 0.0
        self.stepper_angle = 0.0

        #Tooltip
        self.setToolTip(
          "Stepper Motor"
        )

        #Font
        self.text_font = QFont('White Rabbit')
        self.text_font.setPointSize(16)

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsFocusable)
        self.dbg = False
        self.movable(False)
        self.selectable(False)

        self.sm_path = QPainterPath()
        #self.sm_path.addEllipse(self.stepper_motor_rect)
        self.sm_path.addEllipse(-((RECT_SIZE + CIRCLE_SIZE) / 2), -((RECT_SIZE + CIRCLE_SIZE) / 2), CIRCLE_SIZE, CIRCLE_SIZE)
        self.sm_path.setFillRule(Qt.WindingFill)

        self.cp_path = QPainterPath()
        self.cp_path.addEllipse(-((RECT_SIZE + CENTER_POINT_SIZE) / 2), -((RECT_SIZE + CENTER_POINT_SIZE) / 2), CENTER_POINT_SIZE, CENTER_POINT_SIZE)
        self.cp_path.setFillRule(Qt.WindingFill)


    def movable(self, enable):
        self.setFlag(QGraphicsItem.ItemIsMovable, enable)

    def selectable(self, enable):
        self.setFlag(QGraphicsItem.ItemIsSelectable, enable)

    def set_size(self, width, height):
        self.rect.setWidth(width)
        self.rect.setHeight(height)

    def contextMenuEvent(self, event):
        menu = QMenu(self.parentWidget())
        for text, func in (("&Reset Position to 0", self.reset_position),):
            menu.addAction(text, func)
        menu.exec_(event.screenPos())

    def reset_position(self):
        print ("Reset the position of the stepper to 0!")

    def update(self):
        pass

    #Paint
    def paint(self, painter, option, widget):
        painter.fillPath(self.sm_path, self.sm_brush)
        painter.fillPath(self.cp_path, self.cp_brush)


    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def parentWidget(self):
        return self.controller


class StepperMotorArm(QGraphicsItem):

    def __init__(self, status, actions, color, solid = True, movable = True):
        super(StepperMotorArm, self).__init__()
        self.status = status
        self.actions = actions
        self.color = color
        self.movable = movable
        #self.setFlag(QGraphicsItem.ItemIsMovable, True)
        if self.movable:
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        else:
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.setPos(QPointF(    ((-RECT_SIZE / 2)), 
                                ((-RECT_SIZE / 2))))

        self.rect = QRectF(0, 0, USER_RECT[0], USER_RECT[1])
        self.rect.moveTo(- (USER_RECT[0]/2), - (USER_RECT[0]/2))
        self.pen = QPen(Qt.SolidLine)
        self.pen.setColor(color)
        self.pen.setWidth(1)
        self.solid = solid
        self.brush = QBrush(color)
        self.rotate(180)
        self.angle = 0
        self.start_angle = 0.0
        self.cumulative_angle = 0.0

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget):
        self.pen.setColor(Qt.yellow)
        painter.setPen(self.pen)
        
        if self.solid:
            painter.fillRect(self.rect, self.brush)
        else:
            painter.drawRect(self.rect)

        painter.drawRect(0, 0, 1, 1)
        
    def mousePressEvent(self, mouse_event):
        if self.movable:
            self.start_angle = self.angle
            self.cumulative_angle = 0.0
        super(StepperMotorArm, self).mousePressEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        if self.movable:
            self.actions.stepper_update_angle.emit(self.cumulative_angle)

            #print "Initiate a move event:"
            #print "\tPrevious Angle: %f" % self.start_angle
            #print "\tFinal Angle: %f" % self.angle
            #print "\tMoving: %f" % (self.angle - self.start_angle)
            #print "\tCumulative Angle: %f" % self.cumulative_angle
            direction = 1
            if self.cumulative_angle < 0:
                direction = -1
            num_turns = ((int(abs(self.cumulative_angle)) / 360) * direction)
            extra = direction * (abs(self.cumulative_angle) - abs((num_turns * 360)))
            #print "\t\t# of Rotations:        %d" % num_turns
            #print "\t\t# left over rotations: %f" % extra
        super(StepperMotorArm, self).mouseReleaseEvent(mouse_event)

    def mouseMoveEvent(self, mouse_event):
        if self.movable:
            x = self.pos().x() - mouse_event.scenePos().x()
            y = self.pos().y() - mouse_event.scenePos().y()

            angle = math.degrees(math.atan2(x, y))

            angle_delta = angle - self.angle
            if abs(angle_delta) > 180:
                if angle_delta < 0:
                    angle_delta += 360
                else:
                    angle_delta -= 360
                

            self.cumulative_angle += angle_delta
            #print "angle: %f" % angle
            #print "delta angle: %f" % angle_delta
            self.setRotation(-angle)
            self.angle = angle

        super(StepperMotorArm, self).mouseMoveEvent(mouse_event)

