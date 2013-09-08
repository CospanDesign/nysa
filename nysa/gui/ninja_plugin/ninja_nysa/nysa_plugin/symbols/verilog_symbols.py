# -*- coding: utf-8 *-*

import re

from ninja_ide.core import plugin
from ninja_ide.core import plugin_interfaces

EXTENSION = 'v'

class VerilogSymbolsHandler(plugin_interfaces.ISymbolsHandler):
  def __init__(self):
    self.patSpace = re.compile('^\s+')

  def obtain_symbols(self, source):
    """Returns a dict with the verilog symbols for sources."""
    symbols = {}
    attributes = {}
    whitespaces = {}
    comments = {}
    operator = {}
    number = {}
    string = {}
    identifer = {}
    keywork = {}

    source = source.split('\n')

    #for nvo, ine in enumerate(source):
      
    return symbols
