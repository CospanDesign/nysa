# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  7/21/2013: Initial commit
'''

import os
import sys
import json
import inspect

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from defines import BUILD_STATUS_UNKNOWN
from defines import BUILD_STATUS_STOP
from defines import BUILD_STATUS_BUILD
from defines import BUILD_STATUS_PASS
from defines import BUILD_STATUS_PASS_WARNINGS
from defines import BUILD_STATUS_FAIL

from defines import BUILD_STATUS_TIME_STEP

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)


STATUS = enum("unknown",
              "stop",
              "fail",
              "build",
              "pass_build",
              "pass_with_warnings")

class BuildStatus(QObject):
    def __init__(self, scene, position, rect, parent):
        super (BuildStatus, self).__init__()
        #Create pixmaps of all the images
        self.rect = rect
        width = rect.width()
        self.unknown_image = QPixmap(BUILD_STATUS_UNKNOWN).scaledToWidth(width)
        self.stop_image = QPixmap(BUILD_STATUS_STOP).scaledToWidth(width)
        self.pass_image = QPixmap(BUILD_STATUS_PASS).scaledToWidth(width)
        self.pass_warnings_image = QPixmap(BUILD_STATUS_PASS_WARNINGS).scaledToWidth(width)
        self.fail_image = QPixmap(BUILD_STATUS_FAIL).scaledToWidth(width)
        self.build_animation = []
        for image in BUILD_STATUS_BUILD:
            self.build_animation.append(QPixmap(image).scaledToWidth(width))
        self.build_image = self.build_animation[0]

        self.position = position
        self.status = STATUS.unknown
        self.setup_animation()
        self.image = self.unknown_image
        self.set_status(STATUS.unknown)
        self.scene = scene
        self.parent = parent
        self.connect(self, SIGNAL("status_update"), parent.status_update)
        self.up = True


    def setup_animation(self):
        self.total_animation_length = BUILD_STATUS_TIME_STEP * len(self.build_animation)
        self.animation_timer = QTimeLine(self.total_animation_length)
        self.animation_timer.setLoopCount(0) #Loop forever
        self.animation_timer.setFrameRange(0, len(self.build_animation) - 1)
        self.animation_timer.setCurveShape(QTimeLine.LinearCurve)
        self.animation_timer.setUpdateInterval(BUILD_STATUS_TIME_STEP)

        self.connect(self.animation_timer,
                     SIGNAL("valueChanged(qreal)"),
                     self.animation_update)

        #self.connect(self.animation_timer,
        #             SIGNAL("frameChanged(int)"),
        #             self.animation_frame_changed)

        #self.animation_timer.start()


    def set_status(self, status):
        self.status = status
        if self.status == STATUS.unknown:
            self.animation_timer.stop()
            self.image = self.unknown_image
        if self.status == STATUS.stop:
            self.animation_timer.stop()
            self.image = self.stop_image
        elif self.status == STATUS.fail:
            self.animation_timer.stop()
            self.image = self.fail_image
        elif self.status == STATUS.pass_build:
            self.animation_timer.stop()
            self.image = self.pass_image
        elif self.status == STATUS.pass_with_warnings:
            self.animation_timer.stop()
            self.image = self.pass_warnings_image
        elif self.status == STATUS.build:
            self.animation_timer.start()
            self.image = self.build_animation[0]
        self.emit(SIGNAL("status_update"))

    def get_status(self):
        return self.status

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def animation_update(self, real):
        index = int(real * len(self.build_animation))
        if not self.up:
            index = (len(self.build_animation) - 1) - index

        if self.image != self.build_animation[index]:
            #print "Update"
            #print "Update animation: %f, index: %d" % (real, index)
            self.image = self.build_animation[index]
            self.emit(SIGNAL("status_update"))

        if index == 0 and not self.up:
            self.up = True

        if index == (len(self.build_animation) - 1) and self.up:
            self.up = False

    def animation_frame_changed(self, index):

        if self.image != self.build_animation[index]:
            print "frame: %d" % index
            #print "Update"
            #print "Update animation: %f, index: %d" % (real, index)
            self.image = self.build_animation[index]
            self.emit(SIGNAL("status_update"))


        #print "frame changed to: %d" % frame_index
        #if frame_index == 0 and self.animation_timer.Direction == QTimeline.Backward:
        #    self.animation_timer.toggleDirection()

        #if frame_index == self.total_animation_length - 1 and self.animation_timer.Direction == QTimeline.Forward:
        #    self.animation_timer.toggleDirection()
        #self.build_image = self.build_animation[frame_index]



    def paint(self, painter, option, widget):
        painter.drawPixmap(self.position, self.image)

