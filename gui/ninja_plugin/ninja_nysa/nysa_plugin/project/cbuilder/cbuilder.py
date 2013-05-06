# -*- coding: utf-8 -*-

import os
import json
import glob

'''
Functions independent of the project used to build/simulate/debug
'''


class CBuilder ():
    output = None

    def __init__(self, output, locator):
        self.output = output
        self.locator = locator
        self.explorer = self.locator.get_service('explorer')
        self.builder = self.locator.get_service('misc')._misc

    def build_core(self):
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
        self.output.Debug(self, "Project: %s" % str(project))
        self.output.Debug(self, "Core Path: %s" % str(core_path))
        prev_dir = os.getcwd()
        #self.output.Debug(self, "Current dir: %s" % str(prev_dir))
        os.chdir(core_path)
        self.builder.run_application(fileName = '', pythonPath='scons')
        os.chdir(prev_dir)


    def simulate_core(self):
        self.output.Debug (self, "Simulate Core")


    def waveforms(self, info):
        self.output.Debug (self, "Waveforms")
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
        self.output.Debug(self, "Project: %s" % str(project))
        self.output.Debug(self, "Core Path: %s" % str(core_path))
        prev_dir = os.getcwd()
        #self.output.Debug(self, "Current dir: %s" % str(prev_dir))
        os.chdir(core_path)
        self.builder.run_application(fileName = 'wave', pythonPath='scons')
        os.chdir(prev_dir)



    def simulate(self, info):
        self.output.Debug (self, "Simulate")
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
        self.output.Debug(self, "Project: %s" % str(project))
        self.output.Debug(self, "Core Path: %s" % str(core_path))
        prev_dir = os.getcwd()
        #self.output.Debug(self, "Current dir: %s" % str(prev_dir))
        os.chdir(core_path)
        self.builder.run_application(fileName = 'sim', pythonPath='scons')
        os.chdir(prev_dir)



    def get_makefile_path(self):
        path = editor.get_project_owner()
        if path is None:
            #the current document is not selected, we need to get the project
            #from the tree
            explorer = self.locator.get_service('explorer')
            path = explorer.get_actual_project()
            if path is None:
                return None

        #check to see if this is a cbuilder project
        self.output.Debug(self, "Project Path: %s" % path)
