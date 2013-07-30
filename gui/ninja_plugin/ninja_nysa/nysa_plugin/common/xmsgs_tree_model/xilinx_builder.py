# -*- coding: UTF-8 -*-

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


'''
LOG:
    07/28/2013: Initial Commit
'''

import os
import datetime

import xml.etree.ElementTree as ET

class XilinxBuilder(object):

    def __init__(self, name):
        super (XilinxBuilder, self).__init__()
        self.messages = None
        self.finished_parsing = False
        self.timestamp = None
        self.file_reference = None
        self.name = name
        self.builder = ET.XML("<builder>%s</builder>" % self.name) 

    def finished(self):
        '''Returns true if the builder is finished building'''
        if self.finished_parsing:
            return True
        return False

    def get_file_reference(self):
        return self.file_reference

    def message_timestamp(self):
        '''Returns timestamp in seconds to compare with other builds for out of date'''
        return self.timestamp

    def __len__(self):
        '''Returns the number of messages available'''
        return len(self.messges.getchildren())

    def get_messages(self, type_filters = [], only_new_messages = False):
        messages = self.messages.getchildren()
        type_messages = []
        new_messages = []
        #print "messages: %s" % str(messages)
        if len(type_filters) == 0:
            type_messages = messages
        else:
            for type_filter in type_filters:
                for message in messages:
                    #print "message type: %s" % str(message.get('type'))
                        
                    if type_filter == message.get('type'):
                        type_messages.append(message)

        if only_new_messages:
            for message in type_messages:
                if message.get('delta') == 'new':
                    new_messages.append(message)
            return new_messages

        return type_messages

    def new_xmsgs_data(self, data, timestamp, file_reference = None):
        '''
        If finished parsing then this data is new data to process, and will
        replace any previous messages.

        Returns:
            True: finished parsing messages
            False: Not finished parsing messages, this is a work in progress
        '''
        self.timestamp = timestamp
        #Look for the </messages> string, if it exists this is a complete message
        #if self.finished_parsing and "</messages>" in data:
        #    #This is a complete message, replace any previous message
        #    print "Found end of parsering message"
        #    self.messages = ET.XML(data)
        #    self.finished_parsing = True
        #    self.file_reference = None
        #    return True

        #if not this is an incomplete file
        #Check if this is a start of a message
        if "<messages>" in data:
            #print "Found messages"
            #This is the start of a message
            #Remove any previous version of the message
            #Create a root
            self.messages = ET.XML("<messages> </messages>")
            self.finished_parsing = False
            #Remove the <messages> tag from the data
            data = data.partition("<messages>")[2]

        #Parse out the messages
        msgs = data.split("</msg>")
        for msg in msgs:
            #Add the </msg> back into each element
            if "</messages>" in msg:
                self.finished_parsing = True
                self.file_reference = None
                print "Found end of parsering message"
                return True

            if "<msg" not in msg:
                continue

            #print "new sub message"
            msg = msg + "</msg>"
            #print "message: %s" % str(msg)
            element = ET.fromstring(msg)
            #inject the builder name into the XML
            element.append(self.builder)
            self.messages.append(element)

        self.file_reference = file_reference  
        return False

