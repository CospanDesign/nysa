import sys
import os
import string
import copy
from string import Template

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import utils
import arbitor
import gen_top

from gen import Gen

class GenSimTop(Gen):

    def __init__(self):
        return

    def get_name (self):
        print "generate sim top!"

    def gen_script (self, tags = {}, buf = "", user_paths = [], debug = False):
        #print "Generating Simulation Script"
        #print "tags:\n%s" % str(tags)
        #print "\n"
        #print "bindings tags:\n%s" % str(tags["bind"])

        self.tags = copy.deepcopy(tags)
        self.tags["INTERFACE"] = {}
        self.tags["INTERFACE"]["filename"] = "sim_interface.v"
        self.tags["INTERFACE"]["bind"] = {}

        self.tags["INTERFACE"]["bind"]["o_sim_master_ready"] = {
                "loc":"sim_master_ready",
                "direction":"output"}
        self.tags["INTERFACE"]["bind"]["i_sim_in_reset"] = {
                "loc":"sim_in_reset",
                "direction":"input"}
        self.tags["INTERFACE"]["bind"]["i_sim_in_ready"] = {
                "loc":"sim_in_ready",
                "direction":"input"}

        self.tags["INTERFACE"]["bind"]["i_sim_in_command"] = {
                "loc":"sim_in_command[31:0]",
                "direction":"input"}
        self.tags["INTERFACE"]["bind"]["i_sim_in_address"] = {
                "loc":"sim_in_address[31:0]",
                "direction":"input"}
        self.tags["INTERFACE"]["bind"]["i_sim_in_data"] = {
                "loc":"sim_in_data[31:0]",
                "direction":"input"}
        self.tags["INTERFACE"]["bind"]["i_sim_in_data_count"] = {
                "loc":"sim_in_data_count[31:0]",
                "direction":"input"}
  
        self.tags["INTERFACE"]["bind"]["i_sim_out_ready"] = {
                "loc":"sim_out_ready",
                "direction":"input"}
        self.tags["INTERFACE"]["bind"]["o_sim_out_en"] = {
                "loc":"sim_out_en",
                "direction":"output"}

        self.tags["INTERFACE"]["bind"]["o_sim_out_status"] = {
                "loc":"sim_out_status[31:0]",
                "direction":"output"}
        self.tags["INTERFACE"]["bind"]["o_sim_out_address"] = {
                "loc":"sim_out_address[31:0]",
                "direction":"output"}
        self.tags["INTERFACE"]["bind"]["o_sim_out_data"] = {
                "loc":"sim_out_data[31:0]",
                "direction":"output"}
        self.tags["INTERFACE"]["bind"]["o_sim_out_data_count"] = {
                "loc":"sim_out_data_count[27:0]",
                "direction":"output"}


        top = gen_top.GenTop()
        buf = top.gen_script(self.tags, buf, user_paths, debug)

        #Add the waveform file
        waveform_init_string = ("\n" +
            "initial begin\n"
            "  $dumpfile (\"waveform.vcd\");\n" +
            "  $dumpvars (0, top);\n" +
            "end\n\n")


        #put this in right before the 'endmodule'
        pre_end = buf.partition("endmodule")[0]
        buf = pre_end + waveform_init_string + "endmodule\n\n"

        return buf


