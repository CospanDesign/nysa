#! /usr/bin/env python

import os
import sys
import json


def main():

  config_dir = os.path.join(os.path.expanduser('~'), ".config", "nysa")
  path = os.path.join(config_dir, "nysa.json")
  #print "Config Path: %s" % config_dir
  #print "Path: %s" % path

  data = {}
  if not os.path.exists(config_dir):
    #print "Making dir"
    os.makedirs(config_dir)

  if not os.path.exists(path):
    #print "Creating actual file"
    data["dir"] = os.path.abspath(os.path.dirname(__file__))
    try:
      f = open(path, 'w')
      json.dump(data, f)
      f.close()
    except IOError, err:
      #print str(err)
      sys.exit(3)
    sys.exit(0)

  try:
    #print "Openning pre-existing file: %s" % path
    f = open(path, 'r')
    s = f.read()
    #print "File Contents: %s" % s
    data = json.loads(s)
    
    f.close()
  except IOError, err:
    #print str(err)
    sys.exit(2)
  
  data["dir"] = os.path.abspath(os.path.dirname(__file__))
  try:
    #print "Writing the data to file"
    f = open(path, 'w')
    json.dump(data, f)
    f.close()
  except IOError, err:
    #print str(err)
    sys.exit(3)


if __name__ == "__main__":
  main()
