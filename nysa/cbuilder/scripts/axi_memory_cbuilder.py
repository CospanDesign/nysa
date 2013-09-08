#! /usr/bin/python
import os

from generic_slave_cbuilder import CBuilderSlave

class AxiMemoryCBuilder(CBuilderSlave):

  def __init__(self, pdict):
    CBuilderSlave.__init__(self, pdict)

if __name__ == "__main__":
  AMCB = AxiMemoryCBuilder()
  print "Hello World"
