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
import glob
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ninja_ide import resources

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir))
import nysa_actions

"""
Log:
    7/8/2013:
        Added custom build option
"""
'''
Functions independent of the project used to build/simulate/debug
'''

image_path = os.path.join(os.path.dirname(__file__),
                          os.pardir,
                          os.pardir,
                          "images")

CBUILDER_EXT = 'cbldr'
PROJECT_TYPE = "Verilog Core Builder"



class CBuilder (QObject):
    output = None

    def __init__(self, output, locator):
        QObject.__init__(self)
        self.output = output
        self.locator = locator
        self.explorer = self.locator.get_service('explorer')
        self.builder = self.locator.get_service('misc')._misc
        self.editor = self.locator.get_service('editor')
        rw = self.builder._runWidget

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
        self.actions.set_cbuilder(self)
        self.current_core = None

    def build_core(self):
        curr_dir = os.path.dirname(__file__)
        post_build = os.path.join(curr_dir, "post_build")
        self.output.Debug(self, "Building file")
        editor = self.locator.get_service('editor')
        project = editor.get_project_owner()
        core_path = ""
        core_file = glob.glob(project + os.path.sep + "*.cbldr")

        self.output.Debug(self, "Core Files: %s" % core_file)

        if len(core_file) == 0:
            self.output.Debug(self, "This is not a core builder project")
            return

        try:
            f = open(core_file[0], 'r')
            j = json.load(f)
            f.close()
            core_path = j["core"]
        except IOError, err:
            self.output.Error(self, "Error: %s" % str(err))

        core_path = os.path.join (project, core_path)
        print "building: %s" % core_path
        prev_dir = os.getcwd()
        os.chdir(core_path)

        self.builder.show()
        self.builder._item_changed(1)
        rw = self.builder._runWidget
        rw.input.hide()


        rw.output.setPlainText("\n\n")
        rw.output.setCurrentCharFormat(rw.output.plain_format)
        rw.output.moveCursor(QTextCursor.Down)
        rw.output.textCursor().insertText('Running: %s (%s)\n\n' %
            ("build", time.ctime()), rw.output.plain_format)
        rw.output.moveCursor(QTextCursor.Down)


        self.builder.currentProcess = self.proc
        
        self.proc.setWorkingDirectory(core_path)
        env = QProcessEnvironment()
        system_environment = self.proc.systemEnvironment()
        for e in system_environment:
            key, value = e.split('=', 1)
            env.insert(key, value)
        env.insert('PYTHONIOENCODING', 'utf-8')
        self.proc.setProcessEnvironment(env)

        print "Starting..."
        #self.proc.start('/usr/bin/python', ['-u', 'scons', 'build'])
        #print "retval: %s" % str(retval)
        self.proc.closeWriteChannel()
        #self.proc.start('ls')
        #self.proc.execute('ls')
        #self.proc.execute('scons -u build')



        self.current_core = core_path
        self.proc.start('scons', ['build'])
        #self.proc.waitForStarted()
        #print "started"
        #self.proc.closeWriteChannel()
        #self.proc.waitForFinished()
        #so = self.proc.readAllStandardOutput()
        #eo = self.proc.readAllStandardError()

        #print "standard out:\n%s" % str(so)
        #print "error out:\n%s" % str(eo)
        #print "exit code:\n%d" % self.proc.exitCode()
        #if self.proc.exitCode() == 0:

        os.chdir(prev_dir)


    def proc_started(sef):
        print "process started"

    def refresh_output(self):
        rw = self.builder._runWidget
        rw.currentProcess = self.proc
        rw.output._refresh_output()
        return
        #output = self.builder._runWidget.output
        #text = self.proc.readAllStandardOutput().data().decode('utf8')
        #vertical_scroll = output.verticalScrollBar()
        #self.actualValue = vertical_scroll.value()
        #self.max_value = vertical_scroll.maximum()
        #output.textCursor().insertText(text, output.plain_format)

    def refresh_error(self):
        rw = self.builder._runWidget
        rw.currentProcess = self.proc
        rw.output._refresh_error()
        return

        output = self.builder._runWidget.output
        cursor = output.textCursor()
        text = self.proc.readAllStandardError().data().decode('utf8')
        text_lines = text.split('\n')
        vertical_scroll = output.verticalScrollBar()
        self.actualValue = vertical_scroll.value()
        self.max_value = vertical_scroll.maximum()
        for t in text_lines:
            cursor.insertBlock()
            if self.patLink.match(t):
                cursor.insertText(t, output.error_format)
            else:
                cursor.insertText(t, output.plain_format)

    def finish_execution(self, exit_code, exit_status):
        #print "Finished:"
        #print "\tExit Code: %d" % exit_code
        #print "\tExit Status: %s" % str(exit_status)
        rw = self.builder._runWidget
        rw.postExec = None
        rw.currentProcess = self.proc
        rw.finish_execution(exit_code, exit_status)

        if exit_code == 0:
            print "Emitting module_built"
            self.emit(SIGNAL("module_built(QString)"), os.path.split(self.current_core)[1])

        else:
            print "Error"

    def process_error(self, error):
        """Listen to the error signals from the running process."""
        if error == 0:
            print "Failed to start"
        else:
            print "Build error: %d" % error

    def simulate_core(self):
        self.output.Debug (self, "Simulate Core")

    def waveforms(self, info):
        self.output.Debug (self, "Waveforms")
        self.editor = self.locator.get_service('editor')
        project = self.editor.get_project_owner()
        core_path = ""
        core_file = glob.glob(project + os.path.sep + "*.cbldr")

        self.output.Debug(self, "Core Files: %s" % core_file)
        if len(core_file) == 0:
            self.output.Debug(self, "This is not a core builder project")
            return

        try:
            f = open(core_file[0], 'r')
            j = json.load(f)
            f.close()
            core_path = j["core"]
        except IOError, err:
            self.output.Error(self, "Error: %s" % str(err))

        core_path = os.path.join (project, core_path)
        self.output.Debug(self, "Project: %s" % str(project))
        self.output.Debug(self, "Core Path: %s" % str(core_path))
        prev_dir = os.getcwd()
        #self.output.Debug(self, "Current dir: %s" % str(prev_dir))
        os.chdir(core_path)
        self.builder.run_application(fileName = 'wave', pythonPath='scons')
        os.chdir(prev_dir)



    def simulate(self, info):
        self.output.Debug (self, "Simulate")
        self.editor = self.locator.get_service('editor')
        project = self.editor.get_project_owner()
        core_path = ""
        core_file = glob.glob(project + os.path.sep + "*.cbldr")

        self.output.Debug(self, "Core Files: %s" % core_file)
        if len(core_file) == 0:
            self.output.Debug(self, "This is not a core builder project")
            return

        try:
            f = open(core_file[0], 'r')
            j = json.load(f)
            f.close()
            core_path = j["core"]
        except IOError, err:
            self.output.Error(self, "Error: %s" % str(err))

        core_path = os.path.join (project, core_path)
        self.output.Debug(self, "Project: %s" % str(project))
        self.output.Debug(self, "Core Path: %s" % str(core_path))
        prev_dir = os.getcwd()
        #self.output.Debug(self, "Current dir: %s" % str(prev_dir))
        os.chdir(core_path)
        self.builder.run_application(fileName = 'sim', pythonPath='scons')
        os.chdir(prev_dir)

    def get_makefile_path(self):
        path = self.editor.get_project_owner()
        if path is None:
            #the current document is not selected, we need to get the project
            #from the tree
            explorer = self.locator.get_service('explorer')
            path = explorer.get_actual_project()
            if path is None:
                return None

        #check to see if this is a cbuilder project
        self.output.Debug(self, "Project Path: %s" % path)

    def is_cbuilder_project(self, item):
        if item.isProject and item.projecType == PROJECT_TYPE:
            return True
        return False

    def cbuilder_menu(self, menu, item):
        print "Ibuilder project"

        tp = self.editor._explorer._treeProjects

        menu.addSeparator()
        actionRunProject = menu.addAction(QIcon(
            resources.IMAGES['play']), "Compile Project")
        tp.connect(actionRunProject, SIGNAL("triggered()"),
                     SIGNAL("runProject()"))
        actionMainProject = menu.addAction("Set as Main Project")
        tp.connect(actionMainProject, SIGNAL("triggered()"),
                     lambda: tp.set_default_project(item))

    def get_file_icon(self, filename, extension):
        if extension == "v":
            print "verilog file"
            fd_icon = os.path.join(image_path, "verilog.png")
            #fd_icon = os.path.join(image_path, "fpga_designer.png")
            return QIcon(fd_icon)
        return None

