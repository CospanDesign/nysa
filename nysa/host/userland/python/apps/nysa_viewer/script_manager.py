#! /usr/bin/python

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


""" script manager

Used to manage the different user scripts that can be used within Nysa Viewer
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import inspect

from PyQt4.Qt import QObject

from status import Status


p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir)

sys.path.append(p)

from apps.common.nysa_base_controller import NysaBaseController

NAME_POS          = 0
IMAGE_ID_POS      = 1
DEV_ID_POS        = 2
DEV_SUB_ID_POS    = 3
DEV_UNIQUE_ID_POS = 4
SCRIPT_POS        = 5



#Declare a QObect subclass in order to take advantage of signals
class ScriptManager(QObject):

    def __init__(self):
        super (ScriptManager, self).__init__()
        p = os.path.join(os.path.dirname(__file__),
                         os.pardir)
        self.status = Status()
        self.script_dirs = [p]
        self.scripts = []

    def scan(self):
        from apps.drt_viewer.controller import Controller as drt_controller
        from apps.gpio_controller.controller import Controller as gpio_controller
        from apps.memory_controller.controller import Controller as mem_controller
        from apps.i2c_controller.controller import Controller as i2c_controller
        from apps.sf_camera_controller.controller import Controller as sf_controller
        from apps.uart_console.controller import Controller as uart_controller
        #print "DIR: %s" % (str(dir(self)))

        script_list = NysaBaseController.plugins
        print "\tNBC CLASSES: %s" % str(NysaBaseController.plugins)
        for script in script_list:
            print "Adding: %s" % str(script)
            self.insert_script(script)


    def insert_script(self, script):
        #Go through the script to see what it interfaces with
        name = script.get_name()
        unique_image_id = script.get_unique_image_id()
        device_id = script.get_device_id()
        sub_id = script.get_device_sub_id()
        unique_id = script.get_device_unique_id()
        s = [None, None, None, None, None, None]
        s[NAME_POS] = name
        s[IMAGE_ID_POS] = unique_image_id
        s[DEV_ID_POS] = device_id
        s[DEV_SUB_ID_POS] = sub_id
        s[DEV_UNIQUE_ID_POS] = unique_id
        s[SCRIPT_POS] = script
        self.scripts.append(s)

    def identify_image_scripts(self, image_id):
        script_dict = {}
        for script_entry in self.scripts:
            if image_id != 0 and script_entry[IMAGE_ID_POS] == image_id:
                script_dict[script_entry[NAME_POS]] = None
                script_dict[script_entry[NAME_POS]] = script_entry[SCRIPT_POS]
        return script_dict

    def get_device_script(self, dev_id, sub_id = None, unique_id = None):
        script_dict = {}
        print "Number of scripts: %d" % len(self.scripts)
        for script_entry in self.scripts:
            print "Looking at: %d, %s, %s" % (dev_id, str(type(sub_id)), str(type(unique_id)))
            print "Comparing: %s, %s, %s" % (script_entry[DEV_ID_POS], script_entry[DEV_SUB_ID_POS], script_entry[DEV_UNIQUE_ID_POS])
            if dev_id != script_entry[DEV_ID_POS]:
                continue
            if sub_id is not None and sub_id != 0:
                if script_entry[DEV_SUB_ID_POS] is not None:
                    if sub_id != script_entry[DEV_SUB_ID_POS]:
                        continue
            if unique_id is not None and unique_id != 0:
                if script_entry[DEV_UNIQUE_ID_POS] is not None:
                    if unique_id != script_entry[DEV_UNIQUE_ID]:
                        continue
            script_dict[script_entry[NAME_POS]] = None
            script_dict[script_entry[NAME_POS]] = script_entry[SCRIPT_POS]

        return script_dict





