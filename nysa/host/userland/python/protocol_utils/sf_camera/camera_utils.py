# Copyright (c) 2014 Cospan Design (nysa@cospandesign.com)

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


# -*- coding: utf-8 -*-

"""
Camera Device

PyQT Device that interface a Camera from Nysa to a PyQt image input

"""

import sys
import time
import os
import threading
from array import array as Array

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CameraDeviceError(Exception):
    pass

class IMAGE_SIZES(object):
    VGA = 0
    QVGA = 1
    QQVGA = 3
    ZQQVGA = 4
    CIF = 5
    QCIF = 6
    ZCIF = 7
    SUB_QCIF = 8
    ZSUB_QCIF = 9

class CameraWorker(QThread):
    sf_interrupt = pyqtSignal(name = "sf_camera_interrupt")

    def __init__(self, camera, width, height, mutex, img_format, actions, debug = False):
        super (CameraWorker, self).__init__()
        self.debug = debug
        self.camera = camera
        self.mutex = mutex
        self.actions = actions
        self.width = width
        self.height = height
        self.img_format = img_format

        self.captured = False
        self.image_in_queue = False
        self.busy = False

    def read_interrupt(self):
        with self.mutex:
            self.sf_interrupt.emit()

    def process_interrupt(self):
        with self.mutex:
            self.busy = True
            image = self.camera.read_raw_image()
            qimage = QImage(image, self.width, self.height, self.img_format)
            #For Debug purpose save the image
            #qimage.save("image.png", "png")
            self.busy = False
            self.actions.sf_camera_read_ready.emit(qimage)

class CameraThreadWorker(QThread):

    def __init__(self, camera, width, height, mutex, img_format, actions, debug = False):
        super (CameraThreadWorker, self).__init__()
        self.debug = debug
        self.camera = camera
        self.mutex = mutex
        self.actions = actions
        self.width = width
        self.height = height
        self.img_format = img_format

        self.captured = False
        self.term_flag = False

    def __del__(self):
        self.term_flag = True

    def set_size(self, width, height):
        self.width = width
        self.height = height

    def end_reading(self):
        self.term_flag = True

    def run(self):
        while not self.term_flag:
            #Try and lock, every 100ms refresh so if the user wants to exit we are not stuck
            if self.mutex.tryLock(0.100):
                image = self.camera.read_raw_image()
                qimage = QImage(image, self.width, self.height, self.img_format)
                #qimage.save("image.png", "png")
                self.actions.sf_camera_read_ready.emit(qimage)
                self.mutex.unlock()

class CameraUtils(QObject):
    def __init__(self, camera, actions, debug):
        super(CameraUtils, self).__init__()
        self.img_format = QImage.Format_RGB16
        self.mutex = QMutex()
        self.camera_thread_worker = None
        self.height = 0
        self.width = 0
        self.camera = camera
        self.actions = actions
        self.debug = debug

    def setup_camera(self):
        self.camera.set_control(0x00)
        self.camera.reset_camera()
        self.camera.set_rgb_mode()
        self.camera.reset_counts()
        time.sleep(.5)
        row_count = self.camera.read_row_count()
        print "row count: %d" % row_count
        pixel_count = self.camera.read_pixel_count()
        print "pixel count: %d" % (pixel_count / 2)
        self.height = row_count
        self.width = pixel_count / 2 #Asuming RGB565: then 2 bytes per pixel
        self.camera.enable_camera(True)
        self.camera.get_status()

    def run(self):
        if self.camera_thread_worker is None:
            self.camera_thread_worker = CameraThreadWorker(self.camera,
                                                           self.width,
                                                           self.height,
                                                           self.mutex,
                                                           self.img_format,
                                                           self.actions,
                                                           self.debug)
        if self.camera_thread_worker.isRunning():
            #Already Running just exit
            return

        else:
            self.camera_thread_worker.start()

    def stop(self):
        if self.camera_thread_worker is None:
            return
        if self.camera_thread_worker.isRunning():
            self.camera_thread_worker.end_reading()
            self.camera_thread_worker.wait()

        self.camera_thread_worker = None

    def reset(self):
        if self.camera_thread_worker is not None:
            if self.camera_thread_worker.isRunning():
                self.camera_thread_worker.end_reading()
                self.camera_thread_worker.wait()
            self.camera_thread_worker = None

        self.setup_camera()

    def set_black_and_white(self):
        pass

    def set_color_mode(self):
        pass
