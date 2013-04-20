#!/usr/bin/python
import sys
import os
import json

from string import Template

def main():
  nysa_config = None
  path = os.path.expanduser('~')
  path = os.path.join(path, ".config", "nysa", "nysa.json")

  #The user should know about errors... or I should handle them gracefully o_0

  #Open the configuration file from the default location
  try:
    f = open(path)
    s = f.read()
    nysa_config = json.loads(s)
    f.close()
    #print "Opened up the configuration file"
  except IOError, err:
    print "Error user has not set up configuration file, \
      run 'init_settings.py' in nysa base directory"

  #Open the user command file
  f = open('cmd_file.txt')
  template = Template(f.read())
  f.close()
  #print "Opened up the command file"

  #Apply the configuration directory
  buf = template.safe_substitute(
    NYSA=nysa_config["dir"]
  )

  #Write the outptu file
  #print "Opened up the temp file"
  f = open('temp.txt', 'w')
  f.write(buf)
  f.close()
  #print "Wrote the temp file"

  

if __name__ == '__main__':
  main()
