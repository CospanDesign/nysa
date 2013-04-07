#! /usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
#print "Append: %s" % str(os.path.join(os.path.dirname(__file__), os.pardir))
#import nysa

import wx
import wx.lib.agw.aui as aui
from main.main_status import MainStatus
from main.main_navigator import MainNavigator
from main.workspace_manager import WorkspaceManager
from main.nysa_main import NysaMain
from plugins import plugin_manager

class NysaGui (wx.App):
  '''Nysa App Class'''
  _wm = None
  _pm = None
  output = None
  main = None

  def __init__(self):
    wx.App.__init__(self)

  def OnInit(self):
    self.SetAppName("Nysa")
    self.main = NysaMain()
    self._pm = None

    self.output = self.getOutput()

    #Load the plugin manager
    self._pm = plugin_manager.PluginManager(self.main.getOutput())

    #load the workspace manager
    self._wm = WorkspaceManager(self, self.main, self._pm, self.main.getOutput())

    #load the consistent GUI components from the plugins
    self.setup_persistant_gui_components()

    self.main.Show()
    return True

  def setup_persistant_gui_components(self):
    mi_dict = self._pm.get_persistent_gui_menu_items()
    for mi in mi_dict.keys():
      ip = mi_dict[mi]["location"] + "." + mi
      handler = mi_dict[mi]["function"]

      desc = ""
      if "description" in mi_dict[mi].keys():
        desc = mi_dict[mi]["description"]
      accel = None
      if "accellerator" in mi_dict[mi].keys():
        if len(mi_dict[mi]["accellerator"]) > 0:
          accel = mi_dict[mi]["accellerator"]

      self.main.add_menu_item(ip, desc, accel, handler)

    tb_dict = self._pm.get_persistent_gui_toolbar_items()
    for tbi in tb_dict.keys():
      img = tb_dict[tbi]["image"]
      tts = None
      ttl = None
      hdl = tb_dict[tbi]["function"]
      if "tooltip_short" in tb_dict[tbi].keys():
        tts = tb_dict[tbi]["tooltip_short"]

      if "tooltip_long" in tb_dict[tbi].keys():
        ttl = tb_dict[tbi]["tooltip_long"]

      self.main.add_toolbar_item(name = tbi, image_path = img, tooltip_short=tts, tooltip_long=ttl, handler=hdl)

  def getOutput(self):
    return self.main.getOutput()

  def add_project(self, project, project_name, doc_types, image):
    self.main.add_project(project, project_name, doc_types, image)

  def add_project_document(self, project, doc_type, doc_name):
    self.main.add_project_document(project, doc_type, doc_name)



if __name__ == "__main__":
  #print "start"
  app = NysaGui()
  app.MainLoop()
