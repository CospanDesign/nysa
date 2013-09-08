#! /usr/bin/python
import os
from string import Template

from generic_cbuilder import CBuilderError

from generic_slave_cbuilder import CBuilderSlave

class WishbonePeripheralCBuilder(CBuilderSlave):

  def __init__(self, pdict):
    CBuilderSlave.__init__(self, pdict)

  

if __name__ == "__main__":
  WPCB = WishbonePeripheralCBuilder()
  print "Hello World"
