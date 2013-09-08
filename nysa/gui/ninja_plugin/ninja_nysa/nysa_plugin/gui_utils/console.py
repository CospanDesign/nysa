# -*- coding: utf-8 -*-

# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ninja_ide import resources

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir))
import nysa_actions

"""
LOG:
    7/19/2013:
        Initial Commit
"""


class Console(QObject):

    def __init__(self, locator):
        QObject.__init__(self)
        self.locator = locator
        self.explorer = self.locator.get_service('explorer')
        self.builder = self.locator.get_service('misc')._misc
        rw = self.builder._runWidget

        #Setup the QProcess
        self.proc = QProcess()
        rw.connect(self.proc, SIGNAL("finished(int, QProcess::ExitStatus)"),
            self.finish_execution)
        rw.connect(self.proc, SIGNAL("readyReadStandardOutput()"),
            self.refresh_output)
        rw.connect(self.proc, SIGNAL("readyReadStandardError()"),
            self.refresh_error)
        rw.connect(self.proc, SIGNAL("error(QProcess::ProcessError)"),
            self.process_error)
        rw.connect(self.proc, SIGNAL("started()"), self.proc_started)

        self.actions = nysa_actions.NysaActions()

    def run_command(self, work_dir, command, flags = []):
        self.proc.setWorkingDirectory(work_dir)
        env = QProcessEnvironment()
        system_environment = self.proc.systemEnvironment()
        for e in system_environment:
            key, value = e.split('=', 1)
            env.insert(key, value)
        env.insert('PYTHONIOENCODING', 'utf-8')
        self.proc.setProcessEnvironment(env)

        self.proc.closeWriteChannel()
        self.builder.show()
        self.builder._item_changed(1)

        self.proc.start(command, flags)

    def proc_started(self):
        print "process started"

    def finish_execution(self, exit_code, exit_status):
        print "Finished"
        rw = self.builder._runWidget
        rw.postExec = None
        rw.currentProcess = self.proc
        rw.finish_execution(exit_code, exit_status)

    def refresh_output(self):
        rw = self.builder._runWidget
        rw.currentProcess = self.proc
        rw.output._refresh_output()
        rw.output.moveCursor(QTextCursor.End)
        #self.moveCursor(QTextCursorEnd)
        return

    def refresh_error(self):
        rw = self.builder._runWidget
        rw.currentProcess = self.proc
        rw.output._refresh_error()
        return

    def process_error(self, error):
        """Listen to the error signals from the running process."""
        if error == 0:
            print "Command Return Success"
        else:
            print "Command Returned  Error: %d" % error


