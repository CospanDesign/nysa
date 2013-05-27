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


"""Resolves defines from verilog files much like a pre-processor for c

Defines in verilog can be dependent on verilog include file. The ibuilder
script will sometimes need the evaluated values to generate all the files
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

"""Changes:
  06/07/2012
    -Added Documentation and liscense
"""

import os
import sys
import string
from ibuilder_error import PreProcessorError

def generate_define_table(filestring="", debug = False):
  """Reads in a module as a buffer and returns a dictionary of defines

  Generates a table of defines that can be used to resolve values.
  If all the defines cannot be evaluated directly by the
  current module then this will search all the included modules

  Args:
    filestring: A buffer from the module's file

  Returns:
    A dictionary of defines

  Raises:
    PreProcessorError
  """
  import utils
  define_dict = {}
  #from a file string find all the defines and generate an entry into a
  #dictionary
  filestring = utils.remove_comments(filestring)
  str_list = filestring.splitlines()

  for item in str_list:
    if debug: print "Working on: %s" % item
    item = item.strip()
    #look for include files
    if item.startswith("`include"):
      if debug:
        print "found an include: " + item
      #read int the include file, strip away the comments
      #then append everything to the end
      item = item.partition("`include")[2]
      item = item.strip()
      item = item.strip("\"")
      inc_file = utils.find_rtl_file_location(item)
      if debug: print "include file location: " + inc_file

      #try and open the include file
      try:
        ifile = open(inc_file)
        fs = ifile.read()
        ifile.close()
      except:
        if item != "project_defines.v":
          raise PreProcessorError("Error while attempting to the include file: %s" %
                    inc_file)

      try:
        if debug:
          print "got the new file string"
        include_defines = generate_define_table(fs)
        if debug:
          print "after include_define"
          print "length of include defines: " + str(len(include_defines.keys()))
        for key in include_defines.keys():
          #append the values found in the include back in the local dictionary
          if debug:
            print "working on: " + key
          if (not define_dict.has_key(key)):
            define_dict[key] = include_defines[key]


        if debug:
          print "added new items onto the list"
#      except TypeError as terr:
#        print "Type Error: " + str(terr)
      except:
        if item != "project_defines.v":
          raise PreProcessorError("Error while processing: %s: %s" %(item, sys.exc_info()[0]))
          #print "error while processing : ", item, ": ",  sys.exc_info()[0]
      continue

    if item.startswith("`define"):
      #if the string starts with `define split the name and value into the dictionary
#      if debug:
#        print "found a define: " + item
      item = item.partition("`define")[2]
      item = item.strip()
      if (len(item.partition(" ")[2]) > 0):
        name = item.partition(" ")[0].strip()
        value = item.partition(" ")[2].strip()
        if debug:
          print "added " + name + "\n\tWith value: " + value
        define_dict[name] = value
        continue
      if (len(item.partition("\t")[2]) > 0):
        name = item.partition("\t")[0].strip()
        value = item.partition("\t")[2].strip()
        if debug:
          print "added " + name + "\n\tWith value: " + value
        define_dict[name] = value
        continue
      if debug:
        print "found a define without a value: " + item

  return define_dict


def resolve_defines(work_string="", define_dict={}, debug = False):
  """Evauate define

  Reads a string expression and returns a string with all expressions evaluated

  Args:
    work_string: string to be evaluated
    define_dict: the dictionary of defines used for evaluation

  Returns:
    A string with no define references only complete values

  Raises:
    PreProcessorError

  """
  #loop through the string until all the defines are resolved
  #there could be nested defines so the string might go through the same loop

  #a few times
  if debug:
    print "starting string: " + work_string
  work_string = work_string.strip()
  #while there is still a tick mark in the string
  while (work_string.__contains__("`")):
    if debug:
      print "found debug marker"
    #look through the filedict
    #only need to look after the ` portion
    def_string = work_string.partition("`")[2]
    #if there are any white spaces in the line we only want the first one
    def_string = def_string.split()[0]
  #  if (len(def_string.split()) > 0)
  #    def_string = def_string.split()[0]

    if debug:
      print "found the first occurance of a define: " + def_string
    #now I'm working with only the definition and any characters afterwards
    #attempt to match up this entire string to one wihtin the keys
    def_len = len(def_string)
    while ( (def_len > 0) and (not define_dict.keys().__contains__(def_string[0: def_len]))):
      if debug:
        print "def_string: " + def_string[0:def_len]
      #didn't find the string yet
      def_len = def_len - 1
    #check to see if the item found is unique
    #actually the solution must be unique because dictionaries cannot contain multiple keys with the same name
    if (def_len > 0):
      key = def_string[0:def_len]
      value = str(define_dict[key])
      if debug:
        print "found define! " + key
        print "replacement value: " + value
      work_string = work_string.replace("`" + key, value, 1)
      if debug:
        print "final string: " + work_string

    else:
      if debug:
        print "Error in resolve_define(): didn't find define status in %s" % \
              work_string
      raise PreProcessorError("Unable to resolve the defines for %s, are all \
              the defined variables declared?" % work_string)
      return ""


  return work_string


def evaluate_range(in_string = "", define_dict = {}, debug = False):
  """Resolve the range of a statement

  There are times when registers, wires and ports do not have the true value
  of a range. The ibuilder needs to evaluate the defines. this function will
  evaluate all the non-numeric characters to their numeric values

  Args:
    in_string: The string to be evaluated
    define_dict: dictionary that has all the define values

  Returns:
    an output string with all the define's evaluated

  Raises:
    PreProcessorError

  Example:
    `define SIZE 32
    `define MIN 0

    reg bus[(`SIZE - 1):`MIN]

    output  = evaluate_range(\"reg bus[(`SIZE - 1): `MIN]\", {SIZE:32, MIN:0})

    outputs: bus[31:0]
  """

  #resolve all the defines
  #work_string = resolve_defines(in_string, define_dict)
  if ("[" in in_string):
    pre = str(eval(in_string[in_string.index("[") + 1: in_string.index(":")]))
    if debug:
      print "pre: " + pre
    post = str(eval(in_string[in_string.index(":") + 1: in_string.index("]")]))
    if debug:
      print "post: " + post
    in_string = in_string[:in_string.index("[") + 1] + pre + ":" + post + \
      in_string[in_string.index("]")]

  if debug:
    print in_string
  return in_string

