#! /usr/bin/python

import os
import sys

from wishbone_peripheral_cbuilder import WishbonePeripheralCBuilder
from wishbone_memory_cbuilder import WishboneMemoryCBuilder
from axi_peripheral_cbuilder import AxiPeripheralCBuilder
from axi_memory_cbuilder import AxiMemoryCBuilder

class CBuilderFactory(object):

    def __init__(self, cb_dict):
      #Go through the dictionary and call the appropriate cbuilder factory
      if cb_dict["bus_type"] == "slave":
        slave_project = None
        #Slave
        if cb_dict["type"] == "wishbone":
          #Wishbone
          if cb_dict["subtype"] == "peripheral":
            #Peripheral
            slave_project = WishbonePeripheralCBuilder(cb_dict)
          else:
            #Memory
            slave_project = WishboneMemoryCBuilder(cb_dict)
        else:
          #Axi
          if cb_dict["subtype"] == "peripheral":
            #Peripheral
            slave_project = AxiPeripheralCBuilder(cb_dict)
          else:
            #Memory
            slave_project = AxiMemoryCBuilder(cb_dict)

        slave_project.create_project_dir()
        slave_project.process_slave_template()
        slave_project.copy_slave_files()

      else:
        host_interface_project = None
        #Host Interface
        print "Host Interface Not implemented yet!"


