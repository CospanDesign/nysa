# Copyright (c) 2014 name (dave.mccoy@cospandesign.com)

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


"""
I2C Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import csv

class I2CConfigParseError (Exception):
    pass


class I2CConfigController(object):

    def __init__(self, file_location = None):
        super (I2CConfigController, self).__init__()
        self.file_location = file_location


    def _populate_row(self, row_data):
        row_list = []
        for d in row_data:
            if d["type"] == "Start":
                if d["reading"]:
                    row_list.append("Start R 0x%02X" % d["address"])
                else:
                    row_list.append("Start W 0x%02X" % d["address"])
            elif d["type"] == "Stop":
                row_list.append(d["type"])
            elif d["type"] == "Repeat Start":
                row_list.append(d["type"])
            elif d["type"] == "Write":
                row_list.append("0x%02X" % d["data"])
                '''
                if d["require_ack"]:
                    row_list.append("A 0x%02X" % d["data"])
                else:
                    row_list.append("N 0x%02X" % d["data"])
                '''
            elif d["type"] == "Read":
                row_list.append('R')
                '''
                if d["require_ack"]:
                    #row_list.append("A 0x%02X" % d["data"])
                    row_list.append("A")
                else:
                    #row_list.append("N 0x%02X" % d["data"])
                    row_list.append("N")
                '''
        return row_list

    def _extract_row(self, row_list):
        row_data = []
        reading = False
        if len(row_list) == 0:
            return None
        for token in row_list:
            token = token.strip()
            d = {}
            if token.lower().startswith("start"):
                orig = token
                d["type"] = "Start"
                token = token.partition("Start")[2]
                token = token.strip()
                read_char = token[0]
                if token[0] == "R":
                    d["reading"] = True
                    reading = True
                elif token[0] == "W":
                    d["reading"] = False
                    reading = False
                else:
                    raise I2CConfigParseError("R/W flag not set for %s, %s should be either R or W" % (orig, read_char))
                token = token[1:]
                token = token.strip()
                try:
                    d["address"] = int(token, 16)
                except ValueError:
                    raise I2CConfigParseError("Address was incorrect: %s is not a valid hex number" % token)

            elif token.lower() == "stop":
                d["type"] = "Stop"
            elif token.lower() == "repeat start":
                d["type"] = "Repeat Start"
            else:
                #print "token: %s" % token
                #Should be a read or write
                if reading:
                    d["reading"] = []
                    #print "\tReading"
                    '''
                    if token.lower() == "a":
                        d["require_ack"] = True
                    elif token.lower() == "n":
                        d["require_ack"] = False
                    else:
                        raise I2CConfigParseError("Invalid 'ack/nack' value: %s should be either 'A' or 'N'" % token)
                    '''
                else:
                    #print "\tWriting"
                    '''
                    require_ack = token[0]
                    token = token[1:].strip()
                    '''
                    try:
                        d["data"] = int(token, 16)
                    except ValueError:
                        raise I2CConfigParseError("Value: %s is not a valid Hex value" % token)
                    
                    '''
                    if require_ack.lower() == "a":
                        d["require_ack"] = True
                    elif require_ack.lower() == "n":
                        d["require_ack"] = False
                    else:
                        raise I2CConfigParseError("Invalid 'ack/nack' value: %s should be either 'A' or 'N'" % token)
                    '''
            
            row_data.append(d)
        return row_data


    def save_data(self, file_location, start_data, loop_data):
        with open(file_location, 'wb') as csv_file:
            print "Save File is open"
            csv_writer = csv.writer(csv_file, delimiter = ',')
            #First Set the info for the user on line 0
            csv_writer.writerow(["#Start Sequence"])
            start_list = []
            for d in start_data:
                rl = self._populate_row(d)
                csv_writer.writerow(rl)

            csv_writer.writerow(["#Loop Sequence"])
            for d in loop_data:
                rl = self._populate_row(d)
                csv_writer.writerow(rl)

    def load_data(self, file_location = None):
        start_commands = []
        loop_commands = []
        with open(file_location, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')
            print "Load File is open"
            #Go through line by line 
            reader_list = []
            for row in csv_reader:
                reader_list.append(row)

            loop_pos = 0

            for index in range (len(reader_list)):
                #print "Reader List: %s" % str(reader_list[index][0])
                if reader_list[index][0].lower().startswith("#loop sequence"):
                    loop_pos = index
                    break

            for index in range (0, loop_pos):
                if reader_list[index][0].lower().startswith("#"):
                    continue
                cmd = self._extract_row(reader_list[index])
                if cmd is not None:
                    start_commands.append(cmd)

            for index in range (loop_pos, len(reader_list)):
                if reader_list[index][0].lower().startswith("#"):
                    continue
                cmd = self._extract_row(reader_list[index])
                if cmd is not None:
                    loop_commands.append(cmd)


            #print "Start: %s" % str(start_commands)
            #print "Loop: %s" % str(loop_commands)

        #Get the loop data
        return (start_commands, loop_commands)

