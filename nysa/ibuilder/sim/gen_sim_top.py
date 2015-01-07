import sys
import os
import string
import copy
from string import Template

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import utils
import arbiter
import gen_top

import verilog_utils as vutils
import module_builder as mb
import sim_utils as sutils


from gen import Gen

class GenSimTop(Gen):

    def __init__(self):
        return

    def get_name (self):
        print "generate sim top!"

    def gen_script (self, tags = {}, buf = "", user_paths = [], debug = False):
        #Copy the interface so we don't modify the original
        sim_tags = copy.deepcopy(tags)
        sim_tags = self.inject_sim_interface(sim_tags)


        top = gen_top.GenTop()
        buf = top.gen_script(sim_tags, buf, user_paths, debug)

        #Add the waveform file
        return buf

    def inject_sim_interface(self, tags):
        tags["INTERFACE"] = {}
        tags["INTERFACE"]["filename"] = "sim_interface.v"
        tags["INTERFACE"]["bind"] = {}

        tags["INTERFACE"]["bind"]["o_sim_master_ready"] = {
           "loc":"sim_master_ready",
           "direction":"output"}
        tags["INTERFACE"]["bind"]["i_sim_in_reset"] = {
           "loc":"sim_in_reset",
           "direction":"input"}
        tags["INTERFACE"]["bind"]["i_sim_in_ready"] = {
           "loc":"sim_in_ready",
           "direction":"input"}

        tags["INTERFACE"]["bind"]["i_sim_in_command"] = {
           "loc":"sim_in_command[31:0]",
           "direction":"input"}
        tags["INTERFACE"]["bind"]["i_sim_in_address"] = {
           "loc":"sim_in_address[31:0]",
           "direction":"input"}
        tags["INTERFACE"]["bind"]["i_sim_in_data"] = {
           "loc":"sim_in_data[31:0]",
           "direction":"input"}
        tags["INTERFACE"]["bind"]["i_sim_in_data_count"] = {
           "loc":"sim_in_data_count[31:0]",
           "direction":"input"}

        tags["INTERFACE"]["bind"]["i_sim_out_ready"] = {
           "loc":"sim_out_ready",
           "direction":"input"}
        tags["INTERFACE"]["bind"]["o_sim_out_en"] = {
           "loc":"sim_out_en",
           "direction":"output"}

        tags["INTERFACE"]["bind"]["o_sim_out_status"] = {
           "loc":"sim_out_status[31:0]",
           "direction":"output"}
        tags["INTERFACE"]["bind"]["o_sim_out_address"] = {
           "loc":"sim_out_address[31:0]",
           "direction":"output"}
        tags["INTERFACE"]["bind"]["o_sim_out_data"] = {
           "loc":"sim_out_data[31:0]",
           "direction":"output"}
        tags["INTERFACE"]["bind"]["o_sim_out_data_count"] = {
                "loc":"sim_out_data_count[27:0]",
                "direction":"output"}
        return tags

