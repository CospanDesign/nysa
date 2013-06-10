# -*- coding: utf-8 -*-
import sys
import os
import json
import glob

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.core import file_manager

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir,
                                "editor",
                                "fpga_designer"))

from fpga_designer import FPGADesigner

'''
Functions independent of the project used to build/simulate/debug
'''

DESIGNER_EXT = "ibd"

class IBuilder (QObject):
    output = None
    
    def __init__(self, output, locator):
        self.output = output
        self.locator = locator
        self.editor = self.locator.get_service('editor')
        self.explorer = self.locator.get_service('explorer')
        self.builder = self.locator.get_service('misc')._misc

        self.output.Debug(self, "create ibuilder!")
        self.designers = {}
        self.load_designers()

    def file_open(self, filename):
        fext = file_manager.get_file_extension(filename)
        if fext == DESIGNER_EXT:
            self.output.Debug(self, "Found designer extension")
            tab_manager = self.editor.get_tab_manager()

            name = filename.split(os.path.sep)[-1]

            fd = None
            index = -1
            filename = None

            if name in self.designers.keys():
                fd, index, filename = self.designers[name]
                #we have a reference to this in the local
                self.output.Debug(self, "Manager open vaue: %d" % tab_manager.is_open(fd))
                #Check to see if the widget is in the tab manager
                if tab_manager.is_open(fd) == -1:
                    self.output.Debug(self, "Did not find name in opened tabs")
                    if name in self.designers.keys():
                        del self.designers[name]

                else:
                    tab_manager.move_to_open(fd)
                    self.output.Debug(self, "It already is open")


            if name not in self.designers.keys():
                self.output.Debug(self, "Open up a new tab")
                #Not Opened
                fd = FPGADesigner(actions=None, parent=tab_manager, output=self.output)
                index = tab_manager.add_tab(fd, name)
                self.designers[name] = (fd, index, filename)
                fd.initialize_slave_lists()

            return True

        return False

    def file_closed(self, filename):
        self.output.Debug(self, "Filename: %s" % filename)
        name = filename.split(os.path.sep)[-1]
        
        if filname in self.designers.keys():
            fd = None
            index = -1
            filename = None
            fd, index, filename = self.designers[name]
            self.output.Debug(self, "Remove: %s from designer" % filename)
            tab_manager = self.editor.get_tab_manager()
            #Go to the correct tab
            tab_manager.remove_tab(index)
            name = filename.split(os.path.sep)[-1]
            self.designers.remove(filename)
            


    def load_designers(self):
        tab_manager = self.editor.get_tab_manager()

 
