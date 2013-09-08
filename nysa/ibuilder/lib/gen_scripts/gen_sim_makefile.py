import sys
import os
import string
import copy
from string import Template

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import utils
import xilinx_utils
import cocotb_utils

from gen import Gen



class GenSimMakefile(Gen):
    def __init__(self):
        return

    def get_name (self):
        print "generate sim makefile!"

    def gen_script (self, tags = {}, buf = "", user_paths = [], debug = False):
        template = Template(buf)
        #Find out if cocotb is installed on the system
        #TODO: Incorporate command line options to allow the user to specify
            #the location of cocotb
        cocotb_base = cocotb_utils.find_cocotb_base()
        #Find out where the Xilinx toolchain is located
        xilinx_base = xilinx_utils.find_xilinx_path()
        #Find out what simulation files are to be included
        #Get a reference to the base Nysa Class
        base = utils.get_nysa_base()
        buf = template.safe_substitute (COCOTB=cocotb_base,
                                        XILINX=xilinx_base,
                                        NYSA=base)
        return buf
 
