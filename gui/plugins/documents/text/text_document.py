import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))

from nysa.gui.plugins import plugin_document

class TextDocument(plugin_document.PluginDocument):

  def __init__(self, output=None, dbg=False):
    self.dbg = dbg
    plugin_document.PluginDocument.__init__(self, output, dbg)
    self.output.Debug(self, "Hello from text document plugin")

  def setup(self):
    self.output.Debug(self, "Setup text document")

  def save(self, file_path):
    self.output.Debug(self, "Save file to location %s" % file_path)

  def load(self, file_path):
    self.output.Debug(self, "Load file from location %s" % file_path)

