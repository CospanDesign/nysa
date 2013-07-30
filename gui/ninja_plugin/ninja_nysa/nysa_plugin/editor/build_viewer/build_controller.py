# -*- coding: utf-8 *-*

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
  07/24/2013: Initial commit
'''

import os
import sys
import json
import glob
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from build_status import STATUS as bs

from defines import GEN_ID
from defines import SYNTHESIZER_ID
from defines import TRANSLATOR_ID
from defines import MAP_ID
from defines import PAR_ID
from defines import BITGEN_ID
from defines import TRACE_ID

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "gui_utils"))

import console

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common",
                             "xmsgs_tree_model"))

import xmsgs_tree_model

builders = [SYNTHESIZER_ID, TRANSLATOR_ID, MAP_ID, PAR_ID, BITGEN_ID, TRACE_ID]
all_target = TRACE_ID

class BuildControllerError(Exception):
    """
    Errors associated with the Build Controller

    Error associated with:
        -findinig the project directory
        -executing scons
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BuildController(QObject):

    def __init__(self, locator, info_view, build_flow_viewer, xmsgs_viewer):
        super(BuildController, self).__init__()
        self.info = info_view
        self.bfv = build_flow_viewer
        self.bfv.set_build_callback(self.builder_activated)
        self.xv = xmsgs_viewer
        self.xmodel = xmsgs_tree_model.XmsgsTreeModel()
        self.path = ""
        #Some processes I want to keep local
        self.proc = QProcess()
        #Some processes I want to display the output
        self.console = console.Console(locator)
        self.locator = locator

        self.connect(self.proc, SIGNAL("finished(int, QProcess::ExitStatus)"),
            self.finish_execution)
        self.connect(self.proc, SIGNAL("readyReadStandardOutput()"),
            self.refresh_output)
        self.connect(self.proc, SIGNAL("readyReadStandardError()"),
            self.refresh_error)
        self.connect(self.proc, SIGNAL("error(QProcess::ProcessError)"),
            self.process_error)
        self.connect(self.proc, SIGNAL("started()"), self.proc_started)

        self.config = {}
        self.project_config = {}
        self.gen_dir = ""
        self.path = ""
        self.status_busy = False
        self.builder_index = -1

        self.build_busy = False
        self.target_builder_index = -1

        self.locator = locator
        self.explorer = self.locator.get_service('explorer')
        self.builder = self.locator.get_service('misc')._misc
        self.rw = self.builder._runWidget

    def reset(self):
        self.path = ""
        self.gen_dir = ""
        self.config = {}
        self.project_config = {}
        self.xv.set_model(None)

        self.info.reset_labels()

    def update(self, path):
        self.xv.set_model(self.xmodel)
        #print "set build path"
        self.bfv.reset_status()
        if path == "":
            self.reset()
            return

        self.path = path
        #Open the configuratio file
        project_dir = os.path.split(self.path)[0]
        self.project_config = None
        self.gen_dir = None
        try:
            self.project_config = json.load(open(self.path, "r"))
        except IOError as err:
            raise BuildControllerError(
                    "Project Path does not exit: %s" %
                    str(err))
        except ValueError as err:
            raise BuildControllerError(
                    "JSON Error: %s" % str(err))
        except KeyError as err:
            raise BuildControllerErrro(
                    "JSON Error: %s" % str(err))

        #self.gen_dir = os.path.join(project_dir, self.config["output"])
        #print "ibuilder project config: %s" % str(self.project_config)
        main_file_path = os.path.join(project_dir, self.project_config["mainFile"])
        #print "main file path: %s" % main_file_path
        self.config = None
        try:
            self.config = json.load(open(main_file_path, "r"))
        except IOError as err:
            raise BuildControllerError(
                    "Main File Path does not exit: %s" %
                    str(err))
        except ValueError as err:
            raise BuildControllerError(
                    "JSON Error: %s" % str(err))
        except KeyError as err:
            raise BuildControllerErrro(
                    "JSON Error: %s" % str(err))

        #print "ibuilder config: %s" % str(self.config)
        self.gen_dir = self.config["BASE_DIR"]
        #Check for _xmsgs directory
        self.xmsgs_path = os.path.join(self.gen_dir, "_xmsgs")
        if os.path.exists(self.xmsgs_path):
            self.xmodel.set_path(self.xmsgs_path)
        else:
            self.xmodel.set_path(None)
        self.update_build_status()


    def update_build_status(self):
        #print "update build status"
        if not os.path.exists(self.gen_dir):
            raise BuildControllerError(
                    "Build Path does not exists: %s" %
                    str(self.gen_dir))

        #look for the sConstruct files
        self.sconstruct_path = None
        for dl in os.listdir(self.gen_dir):
            dl_path = os.path.join(self.gen_dir, dl)
            #print "Checking: %s" % dl_path
            if os.path.isfile(dl_path) and dl.lower() == "sconstruct":
                self.sconstruct_path = dl_path

        if self.sconstruct_path is None:
            raise BuildControllerError(
                    "Build path does not contain SConstruct file: %s" %
                    str(self.gen_dir))


        #XXX: Need a better check of the project gen status
        self.set_builder_status(GEN_ID, bs.pass_build)
        self.builder_index = -1
        self.get_builders_states()
        #for builder in builders:
        #    self.find_builder_state(builder)

    def get_builders_states(self):
        #Check if we got the state of the last builder
        #print "Get Builder state!"
        while self.build_busy:
            self.proc.waitForFinished()
            self.info.set_status("Wait for build to finish...")
            time.sleep(.5)
            self.info.set_status("checking...")
            if self.status_busy:
                time.sleep(.5)
            else:
                self.info.set_status("Status Updates finished")


        if self.builder_index != -1 and (self.builder_index == len(builders) - 1):
            self.info.set_status("Found all builder's status")
            self.status_busy = False
            self.builder_index = -1
            return
        self.status_busy = True
        self.builder_index += 1
        builder = builders[self.builder_index]
        self.info.set_status("Find state of: %s" % builder)
        self.find_builder_state(builder)

    def find_builder_state(self, target):
        #print "check %s" % str(target)
        #run the scons command with 'xst' and the flags set to '-n'
        #if the return value is 0 then it is finished, if not 0 then
        #the builder is not up to date
        #print "self.gen: %s " % self.gen_dir
        self.proc.setWorkingDirectory(self.gen_dir)
        env = QProcessEnvironment()
        system_environment = self.proc.systemEnvironment()
        for e in system_environment:
            key, value = e.split('=', 1)
            env.insert(key, value)
        self.proc.setProcessEnvironment(env)
        self.proc.closeWriteChannel()
        self.proc.start("scons", ["-q", target])

    def builder_activated(self, builder):
        print "Builder: %s activated" % builder
        while self.status_busy:
            print "status busy"
            self.proc.waitForFinished()
            self.info.set_status("Wait for staus update to finish...")
            time.sleep(.5)
            self.info.set_status("checking...")
            if self.status_busy:
                time.sleep(.5)
            else:
                self.info.set_status("Status Updates finished")


        self.builder_index = -1
        if builder is None:
            builder = all_target

        self.target_builder_index = builders.index(builder)
        self.builder_manager()

       
    def builder_manager(self):
        if self.builder_index == self.target_builder_index:
            self.info.set_status("All Requested Targets Built")
            self.builder_index = -1
            self.target_builder_index = -1
            self.build_busy = False
            return

        self.build_busy = True
        self.builder_index += 1
        builder = builders[self.builder_index]
        self.info.set_status("Building %s" % builder)
        self.build(builder)

    def build(self, builder):
        self.proc.setWorkingDirectory(self.gen_dir)
        env = QProcessEnvironment()
        system_environment = self.proc.systemEnvironment()
        for e in system_environment:
            key, value = e.split('=', 1)
            env.insert(key, value)
        self.proc.setProcessEnvironment(env)
        self.proc.closeWriteChannel()
        self.proc.start("scons", [builder])

    def set_builder_status(self, builder, status):
        #print "update: %s to status: %s" % (builder, str(status))
        self.bfv.set_status(builder, status)

    def proc_started(self):
        #print "process started"
        if self.build_busy:
            builder = builders[self.builder_index]
            self.set_builder_status(builder, bs.build)

    def finish_execution(self, exit_code, exit_status):
        target = builders[self.builder_index]
        status = ""
        self.rw.output.textCursor().insertText(
                "\n",
                self.rw.output.plain_format)
        print "Finish execution: for %s: Exit Code: %d, Exit Status: %d" % (target, exit_code, exit_status)

        if exit_code == 0:
            if self.xmodel.pass_with_warnings(target):
                self.set_builder_status(target, bs.pass_with_warnings)
                status = "Built with warnings"
            else:
                self.set_builder_status(target, bs.pass_build)
                status = "Built"

            self.rw.output.textCursor().insertText(
                    "Found Status for %s: %s" % (target, status),
                    self.rw.output.plain_format)
            self.rw.output.moveCursor(QTextCursor.End)

            if self.status_busy:
                self.get_builders_states()
            elif self.build_busy:
                self.builder_manager()
            return

        if self.xmodel.failed(target):
            self.set_builder_status(target, bs.fail)
            status = "Errors"
        else:
            self.set_builder_status(target, bs.stop)
            status = "Not up to date"

        self.rw.output.textCursor().insertText(
                "Found Status for %s: %s" % (target, status),
                self.rw.output.plain_format)
        self.rw.output.moveCursor(QTextCursor.End)

        if self.status_busy:
            self.get_builders_states()
            return
        else:
            self.rw.postExec = None
            self.rw.currentProcess = self.proc
            self.rw.finish_execution(exit_code, exit_status)
            self.builder_manager()
            return


    def process_error(self, error):
        print "Process error"
        target = builders[self.builder_index]
        if self.build_busy:
            self.rw.output.textCursor().insertText(
                "Error while building %s" % target,
                self.rw.output.plain_format)
        if self.status_busy:
            self.rw.output.textCursor().insertText(
                "Error while finding status for %s" % target,
                self.rw.output.plain_format)

        self.rw.output.moveCursor(QTextCursor.End)
        self.set_builder_status(target, bs.fail)
        self.build_busy = False
        self.status_busy = False
        self.builder_index = -1
        self.target_builder_index = -1


    def refresh_output(self):
        if self.build_busy:
            self.rw.currentProcess = self.proc
            self.rw.output._refresh_output()
            self.rw.output.moveCursor(QTextCursor.End)

    def refresh_error(self):
        print "refresh error"
        if self.build_busy:
            self.rw = self.builder._runWidget
            self.rw.currentProcess = self.proc
            self.rw.output._refresh_error()




