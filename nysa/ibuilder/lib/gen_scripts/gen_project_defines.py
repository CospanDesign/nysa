#gen_project_defines.py
import sys
import os

from gen import Gen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
import utils
from string import Template

class GenProjectDefines(Gen):
    """Generate the top module for a project"""

    def __init__(self):
        #print "in GenProjectDefines"
        return

    def gen_script (self, tags={}, buf="", user_paths = [], debug = False):
        """Generate the project_defines.v"""


        template = Template(buf)
        vendor_string = "VENDOR_FPGA"

        board_dict = utils.get_board_config(tags["board"])
        if board_dict["build_tool"] == "xilinx":
        #if (tags["BUILD_TOOL"] == "xilinx"):
            buf = template.safe_substitute(VENDOR_FPGA = "VENDOR_XILINX")
            vendor_string = "VENDOR_XILINX"

        num_of_entities = self.get_rom_length(tags, user_paths, debug)
        buf = template.substitute(PROJECT_NAME = tags["PROJECT_NAME"],  \
                                  NUMBER_OF_DEVICES=num_of_entities,    \
                                  VENDOR_FPGA=vendor_string,            \
                                  CLOCK_RATE=tags["CLOCK_RATE"])

        return buf

    def get_rom_length(self, tags, user_paths, debug):
        from gen_sdb import GenSDB
        gs = GenSDB()
        return gs.get_number_of_records(tags, user_paths, debug)

    def get_name(self):
        print "Generate the project defines"


