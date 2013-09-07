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
        sim_tag = copy.deepcopy(tags)
        sim_tag["INTERFACE"] = {}
        sim_tag["INTERFACE"]["filename"] = "sim_interface.v"
        sim_tag["INTERFACE"]["bind"] = {}

        sim_tag["INTERFACE"]["bind"]["o_sim_master_ready"] = {
                "loc":"sim_master_ready",
                "direction":"output"}
        sim_tag["INTERFACE"]["bind"]["i_sim_in_reset"] = {
                "loc":"sim_in_reset",
                "direction":"input"}
        sim_tag["INTERFACE"]["bind"]["i_sim_in_ready"] = {
                "loc":"sim_in_ready",
                "direction":"input"}

        sim_tag["INTERFACE"]["bind"]["i_sim_in_command"] = {
                "loc":"sim_in_command[31:0]",
                "direction":"input"}
        sim_tag["INTERFACE"]["bind"]["i_sim_in_address"] = {
                "loc":"sim_in_address[31:0]",
                "direction":"input"}
        sim_tag["INTERFACE"]["bind"]["i_sim_in_data"] = {
                "loc":"sim_in_data[31:0]",
                "direction":"input"}
        sim_tag["INTERFACE"]["bind"]["i_sim_in_data_count"] = {
                "loc":"sim_in_data_count[27:0]",
                "direction":"input"}
  
        sim_tag["INTERFACE"]["bind"]["i_sim_out_ready"] = {
                "loc":"sim_out_ready",
                "direction":"input"}
        sim_tag["INTERFACE"]["bind"]["o_sim_out_en"] = {
                "loc":"sim_out_en",
                "direction":"output"}

        sim_tag["INTERFACE"]["bind"]["o_sim_out_status"] = {
                "loc":"sim_out_status[31:0]",
                "direction":"output"}
        sim_tag["INTERFACE"]["bind"]["o_sim_out_address"] = {
                "loc":"sim_out_address[31:0]",
                "direction":"output"}
        sim_tag["INTERFACE"]["bind"]["o_sim_out_data"] = {
                "loc":"sim_out_data[31:0]",
                "direction":"output"}
        sim_tag["INTERFACE"]["bind"]["o_sim_out_data_count"] = {
                "loc":"sim_out_data_count[27:0]",
                "direction":"output"}


        top = gen_top.GenTop()
        buf = top.gen_script(sim_tag, buf, user_paths, debug)
        return buf


