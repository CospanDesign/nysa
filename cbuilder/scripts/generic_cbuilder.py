#! /usr/bin/python

import os
import sys
import json
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'drt'))

CBUILDER_BASE = os.path.join(os.path.join(os.path.dirname(__file__), 
                                os.pardir))
TEMPLATE_BASE = os.path.abspath(
                  os.path.join( os.path.join(os.path.dirname(__file__), 
                                os.pardir, "template")))

class CBuilderError(Exception):
  """CBuilderError

  Errors associated with generting slaves or host in particular:
    setting incorrect parameters.
    setting incorrect bindings
  """
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)



class GenericCBuilder(object):
  
  pdict = None

  def __init__(self, pdict):
    #print "Generic CBuilder Init"
    self.pdict = pdict

  def create_project_dir(self):
    #get the project directory:
    pd = self.get_project_dir()
    if not os.path.exists(pd):
      #print "Generating directory: %s" % pd
      try:
        os.makedirs(pd)
      except os.error:
        print "Error: Failed to create directory"

  def remove_project(self):
    #get the project directory
    pd = self.get_project_dir()
    if os.path.exists(pd):
      #print "Removing the project directory"
      try:
        shutil.rmtree(pd)
      except shutil.error, err:
        print "No files in that directory"

  def get_project_dir(self):
    #base, type, subtype, name
    project_dir = os.path.join( self.pdict["base"],
                                #self.pdict["type"],
                                #self.pdict["subtype"],
                                self.pdict["name"])
    return project_dir

  def get_template_dir(self):
    return TEMPLATE_BASE

if __name__ == "__main__":
  print "Hello World"
