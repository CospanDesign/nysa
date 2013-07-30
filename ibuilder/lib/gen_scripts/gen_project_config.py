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

""" Output Project Configuration Generator"""

"""
Log:
07/17/2013:
    Initial Commit
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import json
from string import Template

from gen import Gen

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import utils


class GenProjectConfig(Gen):
    """Generate the Project Configuration for the Output Project"""

    def __init__(self):
        return

    def gen_script(self, tags = {}, buf = "", user_paths = [], debug = False):
        #print "tags: %s" % str(tags)
        #Get the configuration in a dictionary form
        config = json.loads(buf)
        board_config = utils.get_board_config(tags["board"])

        #Specify the part  
        config["device"] = board_config["fpga_part_number"]
        config["board"] = board_config["board_name"]
        #if "image" in board_config.keys():
            #config["board_image"] = board_config["image"]

        #Specify the top module
        config["top_module"] = "top"

        #Check if there is any configuration flags for the build
        if "build_flags" in board_config.keys():
            for key in board_config["build_flags"]:
                #Replace whatever is in the configuration dictionary
                config[key] = {}
                config[key] = board_config["build_flags"][key]

        return json.dumps(config, sort_keys = True, indent = 4, separators = [',', ':'])


    def gen_name(self):
        print "Generate Project Configuration"
