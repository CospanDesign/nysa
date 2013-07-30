#!/usr/bin/env python

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Cospan Design (dave.mccoy@cospandesign.com)

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

import os
import sys
import json
import copy
import glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *


"""
This code was inspired by
    hipersayanx.blogspot.com

On this post:

http://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes-using-python


"""

class FileWatcherError (Exception):
    '''
    Errors associated with watching files:
        File list is empty.
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class FileWatcher(QObject):

    def __init__(self):
        super(FileWatcher, self).__init__()
        self.paths = []
        self.file_watcher = None
        self.aggressive = False

    def watch(self,
              paths,
              aggressive = False,
              directory_changed_cb = None,
              file_changed_cb = None,
              file_added_cb = None):
        '''
        sets up the callbacks to get notified when the directory or files in
        paths has changed. The user sets up callbacks to be notified when either
        the file(s) within the list has changed or the diretory(s) have changed.
        The function will receive a string identifying which file or directory
        has changed. The 'aggressive' flag will add files that it finds in a
        directory.
        
        NOTE: USE 'aggressive' FOR AMOUNT OF FILES!!
        
        the format of the functions are as
        follows:

        Directory change callback:
            directory_change_cb(path_of_change)

        Function change callback:
            file_change_cb(path_of_change)

        If the user calls this function a second time the previous files and
        directory that were watched are overwritten

        Args:
            paths (list of strings): A list of directories or files to watch
            aggressive (boolean):
                True: Add files that are added to a directory
                False: Do not add files that are added to a directory

            directory_change_cb (function): a function to call when the
                directory changes
            file_change_cb (function): a function to call when one of the
                file changes
            file_added_cb (function): A function to call when a file is added
                to the watch list (Applicable only with 'aggressive')

        Returns:
            Nothing

        Raises:
            Nothing
        '''
        if len(paths) == 0:
            raise FileWatcherError("List of paths cannot be empty")
        
        self.aggressive = aggressive
        self.directory_changed_cb = directory_changed_cb
        self.file_changed_cb = file_changed_cb
        self.file_added_cb = file_added_cb
        self.file_watcher = QFileSystemWatcher(paths)
        if self.aggressive:
            for path in paths:
                if os.path.isdir(path):
                    self.directory_changed(path)


        self.file_watcher.connect(self.file_watcher,
                                  SIGNAL("directoryChanged(QString)"),
                                  self.directory_changed)
        self.file_watcher.connect(self.file_watcher,
                                  SIGNAL("fileChanged(QString)"),
                                  self.file_changed)



    def file_changed(self, path):
        #print "File Changed: %s" % path
        if self.file_changed_cb is not None:
            self.file_changed_cb(path)

    def directory_changed(self, path):
        #print "Directory Changed: %s" % path
        path = str(path)
        if self.directory_changed_cb is not None:
            self.directory_changed_cb(path)

        if self.aggressive:
            print "Look for any files that might need adding"
            lst = os.listdir(path)
            files = []
            for item in lst:
                print "item: %s" % item
                new_path = os.path.join(path, item)
                print "new path: %s" % new_path
                if os.path.isfile(new_path):
                    files.append(new_path)

            existing_files = self.file_watcher.files()
            self.file_watcher.removePaths(existing_files)

            self.file_watcher.addPaths(files)
            self.file_added_cb(files)


class FileWatcherWidget(QWidget):
    def __init__(self):
        super(FileWatcherWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.directory_line_edit = QPlainTextEdit()
        self.file_line_edit = QPlainTextEdit()
        self.file_add_line_edit = QPlainTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Directory Changed"))
        layout.addWidget(self.directory_line_edit)
        layout.addWidget(QLabel("File Changed"))
        layout.addWidget(self.file_line_edit)
        layout.addWidget(QLabel("File Added"))
        layout.addWidget(self.file_add_line_edit)
        self.setLayout(layout)
        self.show()

    def fc(self, path):
        self.file_line_edit.insertPlainText("%s\n" % path)

    def dc(self, path):
        self.directory_line_edit.insertPlainText("%s\n" % path)
        print "Available files:"
        files = os.listdir(path)
        for f in files:
            print "%s" % f

    def fa(self, paths):
        for p in paths:
            self.file_add_line_edit.insertPlainText("%s\n" % paths)


if __name__ == "__main__":
    print "started"
    fw = FileWatcher()
    app = QApplication(sys.argv)
    fww = FileWatcherWidget()
    fw.watch(["/home/cospan/Projects/ibuilder_projects/image_builder_test/output/_xmsgs"],
             aggressive = True,
             directory_changed_cb = fww.dc,
             file_changed_cb = fww.fc,
             file_added_cb = fww.fa)

    sys.exit(app.exec_())
