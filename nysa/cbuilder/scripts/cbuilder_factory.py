#! /usr/bin/python

import os
import sys

from wishbone_peripheral_cbuilder import WishbonePeripheralCBuilder
from wishbone_memory_cbuilder import WishboneMemoryCBuilder
from axi_peripheral_cbuilder import AxiPeripheralCBuilder
from axi_memory_cbuilder import AxiMemoryCBuilder

""" @package docstring
CBuilder Factor Script

"""



class CBuilderFactory(object):
    """
    Factory core generator
    
    A factory Class to that looks at 3 different settings within the passed
    dictionary: cb_dict

    - bus_type:
    -- slave: Generate a slave
    -- host_interface: Generate a host interface
    - type:
    -- wishbone: Generate a wishbone style core
    -- axi: Generate an Axi style core
    - subtype:
    -- peripheral: Generate a peripheral core
    -- memory: Generate a memory core

    """

    def __init__(self, cb_dict):
      """
      Pass in the cb_dict to generate the correct core
      """
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


