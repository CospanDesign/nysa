#Distributed under the MIT licesnse.
#Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

# Imports
import os
import sys

import wx
import wx.lib.agw.aui as aui
import wx.lib.agw.persist.persistencemanager as PM

from main_status import MainStatus
from main_status import StatusLevel
from main_navigator import MainNavigator
from main_notebook import MainNotebook
from main_toolbar import MainToolBarManager
from main_menu    import MainMenuBarManager

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

#Classes
class AUIManager (aui.AuiManager):
  def __init__(self, managed_window):
    aui.AuiManager.__init__(self)
    self.SetManagedWindow(managed_window)

class NysaMain(wx.Frame):
  #Top Level Window of Nysa
  _mgr  = None
  _mbm  = None
  _pgl  = None

  def __init__(self):
    wx.Frame.__init__(self, None, wx.ID_ANY, "Nysa", size = (600, 400))
    self._mgr = aui.AuiManager()
    self._mgr.SetManagedWindow(self)

    self.SetName("nysa_main")

    module_dir = os.path.dirname(__file__)
    #print "module directory: %s" % module_dir
    icon_file = os.path.join(module_dir, "images", "cospandesign.ico")
    self.SetIcon(wx.Icon(icon_file, wx.BITMAP_TYPE_ICO))

    #Status Output Window
    self.output = MainStatus(self, "Nysa Started")

    #Main View
    self.notebook = MainNotebook(self)
    #Workspace/Project Navigator
    self.nav    = MainNavigator(self)

    #Add the main Notebook View
    self._mgr.AddPane(self.output, wx.BOTTOM, "Output")
    self._mgr.AddPane(self.nav, wx.LEFT, "Navigator")
    self._mgr.AddPane(self.notebook, aui.AuiPaneInfo().Name("notebook_content").CenterPane().PaneBorder(False))

    #Add the Menubar

    self._mbm = MainMenuBarManager(self, self.output)
    self.SetDefaultMenuItems()

    #Test out adding and removing items from the main_menubar
    #self._mbm.add_item(item_path = "test.test1.test2", handler=None)
    #self._mbm.remove_item(item_path = "test.test1.test2")

    #self._mbm.add_item(item_path = "test.test1.test2", handler=None)
    #self._mbm.remove_item(item_path = "test.test1")

    self.CreateTB()
    self.CreateSB()

    #PM.PersistenceManager.RegisterAndRestore(self.notebook)
    self.SetName("nysa_main")
    self.output.Verbose (self, "cwd: %s" % os.getcwd())

    #self._pm = PM.PersistenceManager.Get()
    #_configFile = os.path.join(os.getcwd(), self.GetName())
    #self.output.Verbose(self, "Config File: %s" %self._pm.GetPersistenceDirectory())
    #self._pm.RegisterAndRestore(self)

    #Add the workspace manager
    #_wm = WorkspaceManager(self.output)

    self._mgr.Update()

  def SetDefaultMenuItems(self):
    self._mbm.add_item(item_path = "File.&Exit\tAlt+F4", description = "Exit Program", handler=self.OnExit)
    self._mbm.add_item(item_path= "Options.Disable Current Tab", handler=self.OnDisableTab)
    self._mbm.add_item(item_path= "Options.Enable Current Tab", handler=self.OnEnableTab)
    self._mbm.add_item(item_path= "Options.Add Page", handler=self.OnCreatePage)
    self._mbm.add_item(item_path= "Options.Add a test workspace", handler=self.OnCreateWorkspace)

  def add_menu_item(self, item_path, description, accellerator, handler):
    self._mbm.add_item(item_path = item_path, description = description, accellerator = accellerator, handler = handler)

  def add_toolbar_item(self, name, image_path, tooltip_short=None, tooltip_long=None, handler=None):
    '''Adds a toolbar item to the main view'''
    self.tbm.add_tool(name, image_path, tooltip_short, tooltip_long, handler, user_data=None)

  def AddPage(self, name):
    self.notebook.AddPage(None, name)
    self.output.Verbose(self, "Add Page \'%s\'" % name)
    self._mgr.Update()

  def OnDisableTab(self, event):
    """Disables the current tab"""
    page  = self.notebook.GetCurrentPage()
    page_index  = self.notebook.GetPageIndex(page)

    self.notebook.EnableTab(page_index, False)
    self.notebook.AdvanceSelection()

  def OnEnableTab(self, event):
    """Enable the curret tab"""
    page = self.notebook.GetCurrentPage()
    page_index  = self.notebook.GetPageIndex(page)
    self.notebook.EnableTab(page_index, False)
    self.notebook.AdvanceSelection()

  def OnCreatePage (self, event):
    page_count  = self.notebook.GetPageCount()
    name = "p%d" % (page_count)
    self.AddPage(name)

  def OnCreateWorkspace(self, event):
    self.nav.addWorkspace("test")

  def CreateTB(self):
    tb = self.CreateToolBar()
    self.tbm = MainToolBarManager(tb, self)
    self.tbm.set_default_tools()

  def CreateSB(self):
    self.sb = self.CreateStatusBar()
    '''
    self.sb.SetStatusText("Testing status")
    '''

  def get_menu_bar_manager(self):
    return self._mbm

  def getOutput(self):
    return self.output

  def OnExit(self, name):
    #PM.PersistanceManager.SaveAndUnregister()
    #self._pm.SaveAndUnregister(self)
    self.Close()


#Functions
