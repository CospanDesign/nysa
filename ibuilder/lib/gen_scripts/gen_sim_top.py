import sys
import os
import string
import copy
from string import Template

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import utils
import arbitor
import gen_top

class GenSimTop(Gen):

    def __init__(self):
        return

    def get_name (self):
        print "generate sim top!"

    def gen_script (self, tags = {}, buf = "", user_paths = [], debug = False):
        sim_tag = copy.deepcopy(tags)
        sim_tag["INTERFACE"] = {}
        sim_tag["INTERFACE"]["filename"] = "sim_interface.v"
        sim_tag["INTERFACE"]["bind"] = {
            "o_sim_master_ready",
            "i_sim_in_reset",
            "i_sim_in_ready",
  
            "i_sim_in_command",
            "i_sim_in_address",
            "i_sim_in_data",
            "i_sim_in_data_count",
  
            "i_sim_out_ready",
            "o_sim_out_en",
  
            "o_sim_out_status",
            "o_sim_out_address",
            "o_sim_out_data",
            "o_sim_out_data_count"
        }


        top = gen_top.GenTop()
        buf = top.gen_script(sim_tag, buf, user_paths, debug)
        return buf


