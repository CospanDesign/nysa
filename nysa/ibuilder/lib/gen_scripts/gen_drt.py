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
    -Changed the DRT size from 4 to 8
07/17/2013
    -Added license
"""

#gen_drt.py
import sys
import os
import json

from gen import Gen
import utils
import verilog_utils as vutils
from string import Template
from string import atoi


class GenDRT(Gen):
    """Generate the DRT ROM"""

    def __init__(self):
        #print "in GenDRT"
        return


    def gen_script(self, tags = {}, buf = "", user_paths = [], debug = False):
        out_buf = ""
        self.user_paths = user_paths
        board_fn = os.path.join(utils.get_nysa_base(), "ibuilder", "boards", "boards.json")
        #print "Board Filename: %s" % board_fn
        board_dict = json.load(open(board_fn, 'r'))
        board_id = board_dict[tags["board"]]

        #Get the DRT version from the DRT info
        version = 0x0005
        version_string = "{0:0=4X}".format(version)
        id_string = "{0:0=4X}".format(0xC594)
        number_of_devices = 0
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
        image_string = "{0:0=8X}".format(0)
        if "IMAGE_ID" in tags:
            image_string = "{0:0=8X}".format(tags["IMAGE_ID"])

        #header
        out_buf = version_string + id_string + "\n"
        out_buf += num_dev_string + "\n"
        out_buf += "00000000" + "\n"
        out_buf += board_string + "\n"
        out_buf += image_string + "\n"
        out_buf += "00000000" + "\n"
        out_buf += "00000000" + "\n"
        out_buf += "00000000" + "\n"



        #peripheral slaves
        for i in range (0, len(tags["SLAVES"])):
            key = tags["SLAVES"].keys()[i]
            name = tags["SLAVES"][key]["filename"]
            absfilename = utils.find_rtl_file_location(name, self.user_paths)
            slave_keywords = [
                "DRT_ID",
                "DRT_FLAGS",
                "DRT_SIZE",
                "DRT_SUB_ID"
            ]
            slave_tags = vutils.get_module_tags(filename = absfilename, bus = "wishbone", keywords = slave_keywords)

            drt_id_buffer = "{0:0=4X}"
            drt_flags_buffer = "{0:0=8X}"
            drt_offset_buffer = "{0:0=8X}"
            drt_size_buffer = "{0:0=8X}"

            offset = 0x01000000 * (i + 1)
            drt_id_buffer = drt_id_buffer.format(atoi(slave_tags["keywords"]["DRT_ID"].strip()))
            drt_sub_id_buffer = "0000"
            if "DRT_SUB_ID" in slave_tags["keywords"]:
                drt_sub_id_buffer = "{0:0=4X}".format(atoi(slave_tags["keywords"]["DRT_SUB_ID"].strip()))
            #print "DRT_SUB_ID: %s" % drt_sub_id_buffer
            drt_flags_buffer = drt_flags_buffer.format(0x00000000 + atoi(slave_tags["keywords"]["DRT_FLAGS"]))
            drt_offset_buffer = drt_offset_buffer.format(offset)
            drt_size_buffer = drt_size_buffer.format(atoi(slave_tags["keywords"]["DRT_SIZE"]))
            unique_id_buffer = "00000000"
            if "unique_id" in tags["SLAVES"][key].keys():
                unique_id_buffer = "{0:0=8X}".format(tags["SLAVES"][key]["unique_id"])

            out_buf += drt_sub_id_buffer + drt_id_buffer + "\n"
            out_buf += drt_flags_buffer + "\n"
            out_buf += drt_offset_buffer + "\n"
            out_buf += drt_size_buffer + "\n"
            out_buf += unique_id_buffer + "\n"
            out_buf += "00000000\n"
            out_buf += "00000000\n"
            out_buf += "00000000\n"


        #memory slaves
        if ("MEMORY" in tags):
            mem_offset = 0
            for i in range (0, len(tags["MEMORY"])):
                key = tags["MEMORY"].keys()[i]
                name = tags["MEMORY"][key]["filename"]
                absfilename = utils.find_rtl_file_location(name, self.user_paths)
                slave_keywords = [
                    "DRT_ID",
                    "DRT_FLAGS",
                    "DRT_SIZE"
                ]
                slave_tags = vutils.get_module_tags(filename = absfilename, bus = "wishbone", keywords = slave_keywords)

                drt_id_buffer = "{0:0=8X}"
                drt_flags_buffer = "{0:0=8X}"
                drt_offset_buffer = "{0:0=8X}"
                drt_size_buffer = "{0:0=8X}"
#add the offset from the memory
                drt_id_buffer = drt_id_buffer.format(atoi(slave_tags["keywords"]["DRT_ID"]))
                drt_flags_buffer = drt_flags_buffer.format(0x00010000 +  atoi(slave_tags["keywords"]["DRT_FLAGS"]))
                drt_offset_buffer = drt_offset_buffer.format(mem_offset)
                drt_size_buffer = drt_size_buffer.format(atoi(slave_tags["keywords"]["DRT_SIZE"]))
                mem_offset += atoi(slave_tags["keywords"]["DRT_SIZE"])
                unique_id_buffer = "00000000"
                if "unique_id" in tags["MEMORY"][key].keys():
                    unique_id_buffer = "{0:0=8X}".format(tags["SLAVES"][key]["unique_id"])



                out_buf += drt_id_buffer + "\n"
                out_buf += drt_flags_buffer + "\n"
                out_buf += drt_offset_buffer + "\n"
                out_buf += drt_size_buffer + "\n"
                out_buf += unique_id_buffer + "\n"
                out_buf += "00000000\n"
                out_buf += "00000000\n"
                out_buf += "00000000\n"


        return out_buf

    def gen_name(self):
        print "generate a ROM"
