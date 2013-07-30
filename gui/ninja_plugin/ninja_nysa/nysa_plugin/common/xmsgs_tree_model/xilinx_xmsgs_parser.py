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

import xml.etree.ElementTree as ET

from xilinx_builder import XilinxBuilder

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir,
                                "gui_utils"))

from file_watcher import FileWatcher

white = '\033[0m'
gray = '\033[90m'
red = '\033[91m'
green = '\033[92m'
yellow = '\033[93m'
blue = '\033[94m'
purple = '\033[95m'
cyan = '\033[96m'

test = '\033[97m'


class XilinxXmsgsParserError(Exception):
    """
    Errors associated with the Xilinx Xmsgs Parser

    Error associated with:
        -findinig the xml file
        -parsing the file
        -requested builder is not in builder folders
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class XilinxXmsgsParser(object):
    def __init__(self, changed_cb):
        super(XilinxXmsgsParser, self).__init__()
        self.path = ""
        self.tree = None
        self.builders = {}
        self.fw = FileWatcher()
        self.changed_cb = changed_cb

    def update_watch(self, path):
        self.watch_path(path)

    def watch_path(self, path):
        print "XML Path: %s" % path
        if not os.path.isdir(path):
            raise XilinxXmsgsParserError("Path %s is not a directory")
        self.path = path
        self.parse_files_in_directory()
       
    def parse_files_in_directory(self):
        listings = os.listdir(self.path)
        file_list = []
        print "listings: %s" % str(listings)
        for l in listings:
            lpath = os.path.join(self.path, l)
            if os.path.isfile(lpath):
                self.file_changed(lpath)

    def get_builder_names(self):
        return self.builders.keys()

    def setup_file_watcher(self):
        """Setup a file watcher to track all the builders in a specific
            directory, this is designed to work with the _xmsgs generated
            during a build of a Xilinx FPGA image"""
        self.fw.watch(self.path,
                      aggressive = True,
                      directory_changed_cb = self.directory_changed,
                      file_changed_cb = self.file_changed,
                      file_added_cb = self.file_added)

    def directory_changed(self, path):
        print "Directory Changed"

    def file_changed(self, path):
        #print "File Changed"
        #call the iterparse function
        #for path in paths:
        #print "Path: %s" % path
        name = os.path.split(path)[1]
        name = os.path.splitext(name)[0]
        file_reference = None
        ftime = os.path.getctime(path)
        data = ""

        if name not in self.builders.keys():
            #print "Found: %s" % name
            file_reference = open(path, "r")
            self.builders[name] = XilinxBuilder(name)
        else:
            print "Update: %s" % name
            if self.builders[name].finished():
                #New messages
                file_reference = open(path, "r")
            else:
                #Continus, get the handle to the data
                file_reference =self.builder[name].get_file_reference()

        data = file_reference.read()
        self.builders[name].new_xmsgs_data(data, ftime, file_reference)
        if self.builders[name].finished():
            print "%s is finished" % name
            file_reference.close()
        #print "Parsing: %s" % name

        if self.changed_cb:
            self.changed_cb(name)

    def file_added(self, paths):
        print "File Added"
        for path in paths:
            self.file_changed(path)
        
    def get_messages(self, builder,
                    type_filters = [],
                    only_new_messages = False):
        if builder not in self.builders:
            raise XilinxXmsgsParserError("builder %s is not in builders" % builder)
        return self.builders[builder].get_messages(type_filters,
                                                   only_new_messages)
    def builder_exists(self, builder):
        if builder in self.builders:
            return True
        return False

    def get_message_count(self, builder):
        return len(self.builder[builder])

    def errors(self, builder):
        '''Returns None if no errors or the errors associated with the build'''
        messages = self.get_messages(builder, type_filters = ["error"])
        if len(messages) == 0:
            return None
        return messages


    def warnings(self, builder):
        '''Returns None if no warnings or the errors associated with the build'''
        messages = self.get_messages(builder, type_filters = ["warning"])
        if len(messages) == 0:
            return None
        return messages

    def infos(self, builder):
        '''Returns None if no infos or the infos associated with the build'''
        messages = self.get_messages(builder, type_filters = ["info"])
        if len(messages) == 0:
            return None
        return messages

    def all_messages(self, builder):
        '''Returns all messages'''
        return self.get_messages(builder)

    def new_messages(self, builder):
        '''Returns new messages'''
        return self.get_messages(builder, type_filters = [], only_new_messages = True)

    def pretty_print_messages(self, type_filters = [], only_new_messages = False):
        messages = self.get_messages(type_filters, only_new_messages)
        type_color = white
        print "length of messages: %d" % len(messages)
        for message in messages:
            print "%s%s%s " % (blue, message.get('file'), white),
            if message.get('type') == 'info':
                type_color = green
            elif message.get('type') == 'warning':
                type_color = yellow
            elif message.get('type') == 'error':
                type_color = red

            print "%s%s%s" % (type_color, message.get('type'), white),

            index = 0
            for text in message.itertext():
                if index % 2 == 1:
                    print "%s%s%s" % (cyan, text, white),
                else:
                    print "%s" % (text),
                index += 1

            #print ""
        print white

if __name__ == "__main__":
    xxp = XilinxXmsgsParser()
    #this might need
    xst_msgs_path = os.path.join(os.path.expanduser("~"),
                                "Projects",
                                "ibuilder_projects",
                                "image_builder_test",
                                "output",
                                "_xmsgs")
    xxp.watch_path(xst_msgs_path)
    #tf = ['warning']
    #xxp.pretty_print_messages(type_filters = tf, only_new_messages = False)

