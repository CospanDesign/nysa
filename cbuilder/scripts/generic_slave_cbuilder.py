import os
import sys
import json
import shutil
import glob

from string import Template

from generic_cbuilder import CBUILDER_BASE
from generic_cbuilder import GenericCBuilder
from generic_cbuilder import CBuilderError

class CBuilderSlave(GenericCBuilder):

  def __init__(self, pdict):
    GenericCBuilder.__init__(self, pdict)

  def slave_exists(self):
    #Check if the slave exists
    print "Slave Exists"

  def remove_slave_dir(self):
    #Remove files and directories
    print "Remove Slave Dir"

  def process_slave_template(self):
    template = None
    stp = os.path.join(self.get_template_dir(), "USER_SLAVE.v")
    slave_file = os.path.join(self.get_project_dir(), self.pdict["name"] + ".v")
    #Open template slave file
    f = open(stp)
    template = Template(f.read())
    f.close()
    #Led the calling code handle errors

    #Apply Substitution
    buf = template.safe_substitute(
      DRT_ID=self.pdict["drt_id"],
      DRT_FLAGS=self.pdict["drt_flags"],
      DRT_SIZE=self.pdict["drt_size"],
      NAME=self.pdict["name"]
    )

    #Create output file
    f = open(slave_file, "w")
    #Write new slave file
    f.write(buf)
    f.close()
    #Let the calling code handle errors

  def copy_slave_files(self, base_dir=None):
    #copy all the slave files to the new directory, recursively generate
    #the destination side
    glob_cmd = None

    if base_dir is None:
      glob_cmd = os.path.join(self.get_template_dir(), "*")
    else:
      glob_cmd = os.path.join(self.get_template_dir(), base_dir, "*")

    node_list = glob.glob(glob_cmd)

    #Create all the directories first
    for node in node_list:
      if os.path.isdir(node):
        print "Directory: %s" % node
        d = os.path.basename(node)
        dest_path = ""
        if base_dir is None:
          dest_path = os.path.join(self.get_project_dir(), d)
        else:
          dest_path = os.path.join(self.get_project_dir(), base_dir, d)
        print "Creating directory: %s" % dest_path

        os.makedirs(dest_path)
        if base_dir is not None:
          d = os.path.join(base_dir, d)
        self.copy_slave_files(d)

    #Put all the files in the correct place
    for node in node_list:
      if os.path.isfile(node):
        #filename = os.path.split(filepath)[-1]
        filename = os.path.basename(node)
        if filename == "USER_SLAVE.v":
          #We already modified this file
          print "Do not copy over USER_SLAVE.v"
          continue


        #print "File to copy: %s" % filename

        dest_path = ""
        if base_dir is None:
          dest_path = os.path.join(self.get_project_dir(), filename)
        else:
          #print "Copy to sub dir: %s" % base_dir
          dest_path = os.path.join(self.get_project_dir(), base_dir, filename)

        print "Destintion File Path: %s" % dest_path
        shutil.copy(node, dest_path)

        if filename == "file_list.txt":
          self.fix_project_file_list(dest_path)

  def get_template_dir(self):
    tb = GenericCBuilder.get_template_dir(self)
    tb = os.path.join(  tb,
                        self.pdict["type"],
                        "slave",
                        self.pdict["subtype"])
    return tb

  def fix_project_file_list(self, fl_path):
    f = open(fl_path)
    template = Template(f.read())
    f.close()

    buf = template.safe_substitute(
      CBUILDER_DIR=CBUILDER_BASE,
      USER_SLAVE=self.pdict["name"]
    )

    f = open(fl_path, "w")
    f.write(buf)


