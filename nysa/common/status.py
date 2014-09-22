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

import os
import inspect

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)


white = '\033[0m'
gray = '\033[90m'
red = '\033[91m'
green = '\033[92m'
yellow = '\033[93m'
blue = '\033[94m'
purple = '\033[95m'
cyan = '\033[96m'

if os.name == "nt":
    white  = ''
    gray   = ''
    red    = ''
    green  = ''
    yellow = ''
    blue   = ''
    purple = ''
    cyan   = ''


StatusLevel = enum ('FATAL', 'ERROR', 'WARNING', 'INFO', 'IMPORTANT', 'DEBUG', 'VERBOSE')

_status_instance = None

def Status(*args, **kw):
    global _status_instance
    if _status_instance is None:
        _status_instance = _Status(*args, **kw)
    return _status_instance


class _Status(object):
    @staticmethod
    def is_command_line():
        return True

    def __init__(self):
        super(_Status, self).__init__()
        self.level = StatusLevel.INFO

    def Verbose (self, text):
        if self.CheckLevel(StatusLevel.VERBOSE):
            self.status_output("Verbose", text, color = cyan)

    def Debug (self, text):
        if self.CheckLevel(StatusLevel.DEBUG):
            self.status_output("Debug", text, color = green)

    def Info (self, text):
        if self.CheckLevel(StatusLevel.INFO):
            self.status_output("Info", text, color = white)

    def Important (self, text):
        if self.CheckLevel(StatusLevel.IMPORTANT):
            self.status_output("Important", text, color = blue)

    def Warning (self, text):
        if self.CheckLevel(StatusLevel.WARNING):
            self.status_output("Warning", text, color = yellow)

    def Error (self, text):
        if self.CheckLevel(StatusLevel.ERROR):
            self.status_output("Error", text, color=red)

    def Fatal (self, text):
        if self.CheckLevel(StatusLevel.FATAL):
            self.status_output("Fatal", text, color=red)

    def Print (self, text):
        self.status_output("", None, text)

    def PrintLine(self, text):
        self.status_output("", None, text)

    def status_output(self, level, text, color=white):
        
        function_name = str(inspect.stack()[2][3])
        #print "function_name: %s" % function_name
        if function_name == "<module>":
            function_name = str(inspect.stack()[2][1]).rpartition("./")[2] + ":main"

        class_name = None

        if "self" in inspect.stack()[2][0].f_locals.keys():
            
            class_name = str(inspect.stack()[2][0].f_locals["self"])
            while class_name.find(".") != -1:
                class_name = class_name.partition(".")[2]
            class_name = class_name.partition(" ")[0]

            class_name = class_name.strip("(")
            class_name = class_name.strip(")")

        if class_name is not None and (len(class_name) > 0) and (class_name.strip() != "<module>"):
            d = "%s:%s: " % (class_name, function_name)
        else:
            d = "%s: " % (function_name)

        text = d + text
        print "%s%s: %s%s" % (color, level, text, white)

    def set_level(self, level):
        self.level = level

    def GetLevel(self):
        return self.level

    def CheckLevel(self, requestLevel):
        if requestLevel == StatusLevel.FATAL:
            return True
        elif requestLevel is StatusLevel.VERBOSE:
            if  self.level == StatusLevel.VERBOSE:
                return True
        elif requestLevel is StatusLevel.DEBUG:
            if  self.level == StatusLevel.VERBOSE or \
                self.level == StatusLevel.DEBUG:
                return True
        elif requestLevel is StatusLevel.INFO:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO:
                return True
        elif requestLevel is StatusLevel.IMPORTANT:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO or    \
                self.level == StatusLevel.IMPORTANT:
                return True
        elif requestLevel is StatusLevel.WARNING:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO  or   \
                self.level == StatusLevel.IMPORTANT or \
                self.level == StatusLevel.WARNING:
                return True
        elif requestLevel is StatusLevel.ERROR:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO  or   \
                self.level == StatusLevel.IMPORTANT or \
                self.level == StatusLevel.WARNING or \
                self.level == StatusLevel.ERROR:
                return True
       
        return False

    def cl_status(level = 2, text = ""):

        if level == 0:
            print "%sVerbose: %s%s" % (cyan, text, white)
        elif level == 1:
            print "%sDebug: %s%s" % (green, text, white)
        elif level == 2:
            print "%sInfo: %s%s" % (white, text, white)
        elif level == 3:
            print "%sImportant: %s%s" % (blue, text, white)
        elif level == 4:
            print "%sWarning: %s%s" % (yellow, text, white)
        elif level == 5:
            print "%sError: %s%s" % (red, text, white)
        elif level == 6:
            print "%sCritical: %s%s" % (red, text, white)
        else:
            print "Unknown Level (%d) Text: %s" % (level, text)




