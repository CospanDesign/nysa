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

"""
Changes:

12/13/2011
    -Changed the response from 25 characters to 32
12/02/2011
    -Changed the D R T size from 4 to 8
07/17/2013
    -Added license
"""

#gen_sdb.py
import sys
import os
import json

from gen import Gen
from nysa.ibuilder.lib import utils
import nysa.ibuilder.lib.verilog_utils as vutils
from string import Template
from string import atoi


class GenSDB(Gen):
    """Generate the SDB ROM"""

    def __init__(self):
        #print "in GenSDB"
        return


    def gen_script(self, tags = {}, buf = "", user_paths = [], debug = False):
        out_buf = ""
        self.user_paths = user_paths
        board_name = tags["board"].lower()

        if not utils.is_board_id_in_dict(board_name):
            utils.update_board_id_dict()

        board_id = utils.get_board_id(board_name)

        image_id = 0
        for key in tags.keys():
            if key.lower() == "image_id":
                image_id = tags[key]

        #image_id = board_dict[tags["image_id"]]

        #Get the SDB version from the SDB info
        version = 0x0005
        version_string = "{0:0=4X}".format(version)
        id_string = "{0:0=4X}".format(0xC594)
        number_of_devices = 0
        #print "tags: %s" % str(tags)
        number_of_devices += len(tags["SLAVES"])

        if debug:
            print "number of slaves: " + str(number_of_devices)

        if ("MEMORY" in tags):
            if debug:
                print "num of mem devices: " + str(len(tags["MEMORY"]))
            number_of_devices += len(tags["MEMORY"])

        if debug:
            print "number of entities: " + str(number_of_devices)
        num_dev_string = "{0:0=8X}".format(number_of_devices)
        board_string = "{0:0=8X}".format(board_id)
        image_string = "{0:0=8X}".format(image_id)

        if "IMAGE_ID" in tags:
            image_string = "{0:0=8X}".format(tags["IMAGE_ID"])


        #header
        out_buf = version_string + id_string + "\n"
        out_buf += num_dev_string   + "\n"
        out_buf += "00000000"       + "\n"
        out_buf += board_string     + "\n"
        out_buf += image_string     + "\n"
        out_buf += "0000"              
        out_buf += "00000000"       + "\n"
        out_buf += "00000000"       + "\n"



        #peripheral slaves
        for i in range (0, len(tags["SLAVES"])):
            if debug: print "Working on slave: %d" % i
            key = tags["SLAVES"].keys()[i]
            name = tags["SLAVES"][key]["filename"]
            absfilename = utils.find_rtl_file_location(name, self.user_paths)
            slave_keywords = [
                "SDB_CORE_ID",
                "SDB_SIZE",
                "SDB_SUB_ID"
            ]
            slave_tags = vutils.get_module_tags(filename = absfilename, bus = "wishbone", keywords = slave_keywords)

            sdb_id_buffer = "{0:0=4X}"
            sdb_offset_buffer = "{0:0=8X}"
            sdb_size_buffer = "{0:0=8X}"

            offset = 0x01000000 * (i + 1)
            sdb_id_buffer = sdb_id_buffer.format(atoi(slave_tags["keywords"]["SDB_ID"].strip()))
            sdb_sub_id_buffer = "0000"
            if "SDB_SUB_ID" in slave_tags["keywords"]:
                sdb_sub_id_buffer = "{0:0=4X}".format(atoi(slave_tags["keywords"]["SDB_SUB_ID"].strip()))
            #print "SDB_SUB_ID: %s" % sdb_sub_id_buffer
            sdb_offset_buffer = sdb_offset_buffer.format(offset)
            sdb_size_buffer = sdb_size_buffer.format(atoi(slave_tags["keywords"]["SDB_SIZE"]))
            unique_id_buffer = "00000000"
            if "unique_id" in tags["SLAVES"][key].keys():
                unique_id_buffer = "{0:0=8X}".format(tags["SLAVES"][key]["unique_id"])

            out_buf += sdb_sub_id_buffer + sdb_id_buffer + "\n"
            out_buf += sdb_offset_buffer + "\n"
            out_buf += sdb_size_buffer + "\n"
            out_buf += unique_id_buffer + "\n"
            out_buf += "00000000\n"
            out_buf += "00000000\n"
            out_buf += "00000000\n"


        #memory slaves
        if ("MEMORY" in tags):
            if debug: print "Working on memory: %d" % i
            mem_offset = 0
            for i in range (0, len(tags["MEMORY"])):
                key = tags["MEMORY"].keys()[i]
                name = tags["MEMORY"][key]["filename"]
                absfilename = utils.find_rtl_file_location(name, self.user_paths)
                slave_keywords = [
                    "SDB_ID",
                    "SDB_SIZE"
                ]
                slave_tags = vutils.get_module_tags(filename = absfilename, bus = "wishbone", keywords = slave_keywords)

                sdb_id_buffer = "{0:0=8X}"
                sdb_flags_buffer = "{0:0=8X}"
                sdb_offset_buffer = "{0:0=8X}"
                sdb_size_buffer = "{0:0=8X}"
#add the offset from the memory
                sdb_id_buffer = sdb_id_buffer.format(atoi(slave_tags["keywords"]["SDB_ID"]))
                sdb_offset_buffer = sdb_offset_buffer.format(mem_offset)
                sdb_size_buffer = sdb_size_buffer.format(atoi(slave_tags["keywords"]["SDB_SIZE"]))
                mem_offset += atoi(slave_tags["keywords"]["SDB_SIZE"])
                unique_id_buffer = "00000000"
                if "unique_id" in tags["MEMORY"][key].keys():
                    unique_id_buffer = "{0:0=8X}".format(tags["MEMORY"][key]["unique_id"])



                out_buf += sdb_id_buffer + "\n"
                out_buf += sdb_flags_buffer + "\n"
                out_buf += sdb_offset_buffer + "\n"
                out_buf += sdb_size_buffer + "\n"
                out_buf += unique_id_buffer + "\n"
                out_buf += "00000000\n"
                out_buf += "00000000\n"
                out_buf += "00000000\n"


        if debug: print "SDB:\n%s" % out_buf
        return out_buf

    def gen_name(self):
        print "generate a ROM"
