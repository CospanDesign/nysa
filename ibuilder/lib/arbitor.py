#Distributed under the MIT licesnse.
#Copyright (c) 2012 Cospan Design (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import os
from string import Template
import utils


from ibuilder_error import ArbitorError


"""Arbitor Factory

Analyzes the project tags and determine if one or many arbitors are required
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

"""Changes:
  06/12/2012
    -Added Documentation and licsense
"""


def get_number_of_arbitor_hosts(module_tags = {}, debug = False):
  """get_number_of_arbitor_hosts

  returns the number of arbitor hosts found inside the module

  Args:
    module_tags: the tags for this module
      can be obtained with utils.get_module_tags

  Return:
    the number of arbitor hosts associated with this module

  Raises:
    Nothing
  """

  #go through all the ports and verify that after the first
  #'_' there is a a wbm and hte wbm has all the arbitor
  #host components

  if debug:
    print "Module Name: %s" % (module_tags["module"])
    print "ports: "

  wb_bus = [  ["o", "_we"],
              ["i", "_dat"],
              ["i", "_int"],
              ["i", "_ack"],
              ["o", "_adr"],
              ["o", "_stb"],
              ["o", "_cyc"],
              ["o", "_dat"],
              ["o", "_sel"]
      ]
  possible_prefix = {}
  prefixes = []
  for io_ports in module_tags["ports"]:
    if debug:
      print "\tio_ports: " + io_ports
    for name in module_tags["ports"][io_ports]:
      if debug:
        print "\t\t: " + str(name)
      #throw out obvious false
      if "_" not in name:
        continue

      for wbm_wire in wb_bus:
        if wbm_wire[1] in name:
          io      = name.partition("_")[0]
          if io not in wbm_wire[0]:
            continue

          prefix = name.partition("_")[2]
          #wbm_post = prefix.partition("_")[1] + prefix.partition("_")[2]
          wbm_post = wbm_wire
          prefix = prefix.partition(wbm_wire[1])[0]
          if prefix not in possible_prefix.keys():
            possible_prefix[prefix] = list(wb_bus)
            if debug:
              print "found a possible arbitor: %s" % (prefix)

          #wbm_post = name.partition("_")[2]
          if wbm_post in possible_prefix[prefix]:
            possible_prefix[prefix].remove(wbm_post)



  for prefix in possible_prefix.keys():
    if debug:
      print "examining: %s" % (prefix)
      print "\tlength of prefix list: %s" % (str(possible_prefix[prefix]))
    if len (possible_prefix[prefix]) == 0:
      if debug:
        print "%s is an arbitor host" % (prefix)
      prefixes.append(prefix)

  return prefixes


def is_arbitor_host(module_tags = {}, debug = False):
  """is_arbitor_host

  Determins if a slave can be an arbitor host

  Args:
    module_tags: The tags that are associated with this modue
      can be obtained with utils.get_module_tags

  Return:
    True: Slave is an arbitor host
    False: Slave is not an arbitor host

  Raises:
    Nothing
  """
  return (len(get_number_of_arbitor_hosts(module_tags, debug)) > 0)

def is_arbitor_required(tags = {}, debug = False):
  """is_arbitor_required

  Analyzes the project tags and determines if an arbitor is requried

  Args:
    tags: Project tags

  Return:
    True: An arbitor is required
    False: An arbitor is not required

  Raises:
    Nothing
  """
  if debug:
    print "in is_arbitor_required()"
  #count the number of times a device is referenced

  #SLAVES
  slave_tags = tags["SLAVES"]
  for slave in slave_tags:
    if debug:
      print "found slave " + str(slave)
    if ("BUS" in slave_tags[slave]):
      if (len(slave_tags[slave]["BUS"]) > 0):
        return True
#XXX: FOR THIS FIRST ONE YOU MUST SPECIFIY THE PARTICULAR MEMORY SLAVE AS APPOSED TO JUST MEMORY WHICH IS THAT ACTUAL MEMORY INTERCONNECT

  return False

def generate_arbitor_tags(tags = {}, debug = False):
  """generate_arbitor_tags

  generate a dictionary (tags) that is required to generate all the
  arbitors and how and where to connect all the arbitors

  Args:
    tags: Project tags

  Return:
    dictionary of arbitors to generating

  Raises:
    Nothing
  """
  arb_tags = {}
  if (not is_arbitor_required(tags)):
    return {}

  if debug:
    print "arbitration is required"

  slave_tags = tags["SLAVES"]
  for slave in slave_tags:
    if ("BUS" in slave_tags[slave]):
      if (len(slave_tags[slave]["BUS"]) == 0):
        continue
      if debug:
        print "slave: " + slave + " is an arbtrator master"
      for bus in slave_tags[slave]["BUS"].keys():
        if debug:
          print "bus for " + slave + " is " + bus
        arb_slave = slave_tags[slave]["BUS"][bus]
        if debug:
          print "adding: " + arb_slave + " to the arb_tags for " + bus

        if (not already_existing_arb_bus(arb_tags, arb_slave)):
          #create a new list
          arb_tags[arb_slave] = {}

        arb_tags[arb_slave][slave] = bus

  return arb_tags

def generate_arbitor_buffer(master_count, debug = False):
  """generate_arbitor_buffer

  generate a buffer for an arbitor with the specified master_count

  Args:
    master_count: The number of masters that this arbitor must control

  Return:
    A buffer that contains a verilog based Arbitor with

  Raises:
    IOError
    ArbitorError
  """
#need to open up the arbitor file and create a buffer

  if not isinstance(master_count, (int, long)):
    raise ArbitorError("master_count is not a number")

  if master_count <= 1:
    raise ArbitorError("master_count must be > 1")

  filename = os.path.join(  utils.get_nysa_base(), 
                            "cbuilder", 
                            "verilog", 
                            "wishbone", 
                            "arbitor", 
                            "wishbone_arbitor.v")
  filein = open(filename)
  buf = filein.read()
  filein.close()


  template = Template(buf)

  port_buf = ""
  port_def_buf = ""
  master_count_buf = ""
  master_sel_buf = ""
  priority_sel_buf = ""
  write_buf = ""
  strobe_buf = ""
  cycle_buf = ""
  select_buf = ""
  address_buf = ""
  data_buf = ""
  assign_buf = ""

  #generate the ports
  for i in range (master_count):
    #add the ports
    port_buf = port_buf + "\tm" + str(i) + "_we_i,\n"
    port_buf = port_buf + "\tm" + str(i) + "_cyc_i,\n"
    port_buf = port_buf + "\tm" + str(i) + "_stb_i,\n"
    port_buf = port_buf + "\tm" + str(i) + "_sel_i,\n"
    port_buf = port_buf + "\tm" + str(i) + "_ack_o,\n"
    port_buf = port_buf + "\tm" + str(i) + "_dat_i,\n"
    port_buf = port_buf + "\tm" + str(i) + "_dat_o,\n"
    port_buf = port_buf + "\tm" + str(i) + "_adr_i,\n"
    port_buf = port_buf + "\tm" + str(i) + "_int_o"
    port_buf = port_buf + ",\n"

    port_buf = port_buf + "\n\n"

  if (debug):
    print "port_buf: " + port_buf

  #generate the port defines
  for i in range (master_count):
    port_def_buf = port_def_buf + "input\t\t\tm" + str(i) + "_we_i;\n"
    port_def_buf = port_def_buf + "input\t\t\tm" + str(i) + "_cyc_i;\n"
    port_def_buf = port_def_buf + "input\t\t\tm" + str(i) + "_stb_i;\n"
    port_def_buf = port_def_buf + "input\t[3:0]\tm" + str(i) + "_sel_i;\n"
    port_def_buf = port_def_buf + "input\t[31:0]\tm" + str(i) + "_adr_i;\n"
    port_def_buf = port_def_buf + "input\t[31:0]\tm" + str(i) + "_dat_i;\n"
    port_def_buf = port_def_buf + "output\t[31:0]\tm" + str(i) + "_dat_o;\n"
    port_def_buf = port_def_buf + "output\t\t\tm" + str(i) + "_ack_o;\n"
    port_def_buf = port_def_buf + "output\t\t\tm" + str(i) + "_int_o;\n"
    port_def_buf = port_def_buf + "\n\n"

  if (debug):
    print "port define buf: \n\n" + port_def_buf

  master_count_buf = str(master_count);

  #generate the master_select logic
  master_sel_buf = "//master select block\n"
  master_sel_buf += "parameter MASTER_NO_SEL = 8'hFF;\n"
  for i in range(master_count):
    master_sel_buf += "parameter MASTER_" + str(i) + " = " + str(i) + ";\n"

  master_sel_buf += "\n\n"

  #master_sel_buf += "always @(rst or master_select or priority_select or s_ack_i or s_stb_o "
  #for i in range(master_count):
  #  master_sel_buf += "or m" +str(i) + "_cyc_i or m" + str(i) + "_stb_i "

  #master_sel_buf += ") begin\n"

  master_sel_buf += "always @ (posedge clk) begin\n"
  #master_sel_buf += "always @ (*) begin\n"
  master_sel_buf += "\tif (rst) begin\n"
  master_sel_buf += "\t\tmaster_select <= MASTER_NO_SEL;\n"
  master_sel_buf += "\tend\n"

  master_sel_buf += "\telse begin\n"
  master_sel_buf += "\t\tcase (master_select)\n"

  for i in range(master_count):
    master_sel_buf += "\t\t\tMASTER_" + str(i) + ": begin\n"
    master_sel_buf += "\t\t\t\tif (~m" + str(i) + "_cyc_i && ~s_ack_i) begin\n"
    master_sel_buf += "\t\t\t\t\tmaster_select <= MASTER_NO_SEL;\n"
    master_sel_buf += "\t\t\t\tend\n"
    master_sel_buf += "\t\t\tend\n"

  master_sel_buf += "\t\t\tdefault: begin\n"
  master_sel_buf += "\t\t\t\t//nothing selected\n"

  first_if_flag = True
  for i in range(master_count):
    if (first_if_flag):
      first_if_flag = False
      master_sel_buf += "\t\t\t\tif (m" + str(i) + "_cyc_i) begin\n"
    else:
      master_sel_buf += "\t\t\t\telse if (m" + str(i) + "_cyc_i) begin\n"

    master_sel_buf += "\t\t\t\t\tmaster_select <= MASTER_" + str(i) + ";\n"
    master_sel_buf += "\t\t\t\tend\n"
  master_sel_buf += "\t\t\tend\n"
  master_sel_buf += "\t\tendcase\n"
  master_sel_buf += "\t\tif ((master_select != MASTER_NO_SEL) && (priority_select < master_select) && (!s_stb_o && !s_ack_i))begin\n"
  master_sel_buf += "\t\t\tmaster_select  <=  MASTER_NO_SEL;\n"

  #first_if_flag = True
  #for i in range(master_count):
  #  if (first_if_flag):
  #    first_if_flag = False
  #    master_sel_buf += "\t\t\t\tif (m" + str(i) + "_cyc_i) begin\n"
  #  else:
  #    master_sel_buf += "\t\t\t\telse if (m" + str(i) + "_cyc_i) begin\n"

  #  master_sel_buf += "\t\t\t\t\tmaster_select <= MASTER_" + str(i) + ";\n"
  #  master_sel_buf += "\t\t\t\tend\n"

  master_sel_buf += "\t\tend\n"
  master_sel_buf += "\tend\n"
  master_sel_buf += "end\n"

  if debug:
    print "master select buffer:\n\n" + master_sel_buf


  #generate the priority_select logic
  prirotiy_sel_buf = "//priority select block"

  priority_sel_buf += "\n\n"
  #priority_sel_buf += "parameter PRIORITY_NO_SEL = 8'hFF;\n"
  #first_if_fag = True
  #for i in range (master_count):
  #  priority_sel_buf += "parameter PRIORITY_" + str(i) + " = " + str(i) + ";\n"

  priority_sel_buf += "\n\n"
  #priority_sel_buf += "always @(rst or master_select or priority_select "
  #for i in range (master_count):
  #  priority_sel_buf += "or m" + str(i) + "_cyc_i "

  #priority_sel_buf += ") begin\n"

  priority_sel_buf += "always @ (posedge clk) begin\n"
  #priority_sel_buf += "always @ (*) begin\n"
  priority_sel_buf += "\tif (rst) begin\n"
  #priority_sel_buf += "\t\tpriority_select <= PRIORITY_NO_SEL;\n"
  priority_sel_buf += "\t\tpriority_select <= MASTER_NO_SEL;\n"
  priority_sel_buf += "\tend\n"
  priority_sel_buf += "\telse begin\n"
  priority_sel_buf += "\t\t//find the highest priority\n"
  first_if_flag = True
  for i in range (master_count):
    if first_if_flag:
      first_if_flag = False
      priority_sel_buf += "\t\tif (m" + str(i) + "_cyc_i) begin\n"
    else:
      priority_sel_buf += "\t\telse if (m" + str(i) + "_cyc_i) begin\n"

    #priority_sel_buf += "\t\t\tpriority_select  <= PRIORITY_" + str(i) + ";\n"
    priority_sel_buf += "\t\t\tpriority_select  <= MASTER_" + str(i) + ";\n"
    priority_sel_buf += "\t\tend\n"

  priority_sel_buf += "\t\telse begin\n"
  #priority_sel_buf += "\t\t\tpriority_select  <= PRIORITY_NO_SEL;\n"
  priority_sel_buf += "\t\t\tpriority_select  <= MASTER_NO_SEL;\n"
  priority_sel_buf += "\t\tend\n"
  priority_sel_buf += "\tend\n"
  priority_sel_buf += "end\n"

  if debug:
    print "priority_sel_buf: \n\n" + priority_sel_buf



  #generate the write logic
  write_buf = "//write select block\n"
  #write_buf += "assign master_we_o[MASTER_NO_SEL] = 0;\n"
  for i in range (master_count):
    write_buf += "assign master_we_o[MASTER_%d] = m%d_we_i;\n" % (i, i)
  write_buf += "\n"

  #generate the strobe logic
  strobe_buf = "//strobe select block\n"
  #strobe_buf += "assign master_stb_o[MASTER_NO_SEL] = 0;\n"
  for i in range (master_count):
    strobe_buf += "assign master_stb_o[MASTER_%d] = m%d_stb_i;\n" % (i, i)
  strobe_buf += "\n"

  #generate the cycle logic
  cycle_buf = "//cycle select block\n"
  #cycle_buf += "assign master_cyc_o[MASTER_NO_SEL] = 0;\n"
  for i in range (master_count):
    cycle_buf += "assign master_cyc_o[MASTER_%d] = m%d_cyc_i;\n" % (i, i)
  cycle_buf += "\n"

  #generate the select logic
  select_buf = "//select select block\n"
  #select_buf += "assign master_sel_o[MASTER_NO_SEL] = 0;\n"
  for i in range (master_count):
    select_buf += "assign master_sel_o[MASTER_%d] = m%d_sel_i;\n" % (i, i)
  select_buf += "\n"

  #generate the address_logic
  address_buf = "//address seelct block\n"
  #address_buf += "assign master_adr_o[MASTER_NO_SEL] = 0;\n"
  for i in range (master_count):
    address_buf += "assign master_adr_o[MASTER_%d] = m%d_adr_i;\n" % (i, i)
  address_buf += "\n"

  #generate the data logic
  data_buf = "//data select block\n"
  #data_buf += "assign master_dat_o[MASTER_NO_SEL] = 0;\n"
  for i in range (master_count):
    data_buf += "assign master_dat_o[MASTER_%d] = m%d_dat_i;\n" % (i, i)
  data_buf += "\n\n"


  #generate the assigns
  assign_buf = "//assign block\n"
  for i in range(master_count):
    assign_buf += "assign m" + str(i) + "_ack_o = (master_select == MASTER_" + str(i) + ") ? s_ack_i : 0;\n"
    #assign_buf += "assign m" + str(i) + "_dat_o = (master_select == MASTER_" + str(i) + ") ? s_dat_i : 0;\n"
#XXX: This is a little messy
    assign_buf += "assign m" + str(i) + "_dat_o = s_dat_i;\n"
    assign_buf += "assign m" + str(i) + "_int_o = (master_select == MASTER_" + str(i) + ") ? s_int_i : 0;\n"
    assign_buf += "\n"

  arbitor_name = "arbitor_" + str(master_count) + "_masters"

  buf = template.substitute ( ARBITOR_NAME=arbitor_name,
                PORTS=port_buf,
                NUM_MASTERS=master_count_buf,
                PORT_DEFINES=port_def_buf,
                PRIORITY_SELECT=priority_sel_buf,
                MASTER_SELECT=master_sel_buf,
                WRITE=write_buf,
                STROBE=strobe_buf,
                CYCLE=cycle_buf,
                SELECT=select_buf,
                ADDRESS=address_buf,
                DATA=data_buf,
                ASSIGN=assign_buf);
  return buf




def already_existing_arb_bus(arb_tags = {}, arb_slave = "", debug = False):
  """already_existing_arb_bus

  Check if the arbitrated slave already exists in the arbitor tags

  Args:
    arb_tags: arbitor tags
    arb_slave: possible arbitor slave

  Return:
    True: There is already an arbitor bus associated with this slave
    False: There is not already an arbitor bus associated with this slave

  Raises:
    Nothing
  """
  for arb_item in arb_tags.keys():
    if (arb_item == arb_slave):
      return True
  return False

