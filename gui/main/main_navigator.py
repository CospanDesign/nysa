
import os
import wx

import wx.gizmos as gizmos
from wx.lib.buttons import GenBitmapTextButton

class MainNavigator(wx.Panel):
  '''IDE Navigator (Singleton)'''
  def __init__(self, parent):
    wx.Panel.__init__(  self,
                        parent=parent,
                        id = wx.ID_ANY,
                        pos = wx.DefaultPosition,
                        size = (250, -1))
    self.SetName("main_navigator")

    self.workspace_choices = []

    self.workspaceCombo = wx.ComboBox(  self,
                                        value='',
                                        pos = wx.DefaultPosition,
                                        size= wx.DefaultSize,
                                        choices = [],
                                        style = 0,
                                        validator = wx.DefaultValidator,
                                        name = wx.ComboBoxNameStr)

    self.output = parent.getOutput()
    self.output.Verbose(self, "Starting Navigator")
    #Add the Tree to the bottom

    self.createNavigationTree()
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(self.workspaceCombo, 0)
    sizer.Add(self.nav, 1)

    self.SetSizer(sizer)

  def createNavigationTree(self):
    self.nav = wx.TreeCtrl(self, size= (200, -1), style=wx.TR_HIDE_ROOT)
    self.nav.SetSizeHints(300, -1, -1, -1)
    #self.nav.AddColumn("Project")
    #self.nav.SetMainColumn(0)
    #self.nav.AddColumn("Type")
    #self.nav.AddColumn("File")
    self.nav.AddRoot("Root")
    self.nav.Expand(self.nav.GetRootItem())

  def addWorkspace(self, workspace_name):
    self.output.Verbose(self, "Adding workspace %s" % workspace_name)
    self.workspaceCombo.Insert(workspace_name, 0)
    self.workspaceCombo.SetSelection(0)


  def add_project(self, project, name, doc_types, image):
    type_image_path = os.path.join(os.path.dirname(__file__), "images", "project_type.png")
    #create a new entry into the project into the navigator
    self.output.Debug(self, "Adding New Project, image: %s" % str(name))
    root = self.nav.GetRootItem()
    #project_button = GenBitmapTextButton(self, wx.ID_ANY, wx.Bitmap(image), name, (10, 10), (10, 10))
    p_ref = self.nav.AppendItem(root, name)
    image_list = wx.ImageList(32, 16)
    p_img     = image_list.Add(wx.Image(image, wx.BITMAP_TYPE_PNG).Scale(32,16).ConvertToBitmap())
    type_img  = image_list.Add(wx.Image(type_image_path, wx.BITMAP_TYPE_PNG).Scale(32, 16).ConvertToBitmap())
    self.nav.AssignImageList(image_list)
    self.nav.SetItemPyData(p_ref, project)
    self.nav.SetItemImage(p_ref, p_img, wx.TreeItemIcon_Normal)
    for item in doc_types:
      t = self.nav.AppendItem(p_ref, item)
      self.nav.SetPyData(t, None)
      self.nav.SetItemImage(t, type_img, wx.TreeItemIcon_Normal)

    self.nav.Expand(p_ref)

  def add_project_document(self, project, doc_type, doc_name):
    root = self.nav.GetRootItem()
    if not self.nav.ItemHasChildren(root):
      return -1

    cookie = None
    child = None
    child, cookie = self.nav.GetFirstChild(root)
    self.output.Debug(self, "Project Name: %s" % self.nav.GetItemPyData(child).get_name())
    if self.nav.GetItemPyData(child) is not project:
      if self.nav.GetChildrenCount(root) > 1:
        for a in range(1, self.nav.GetChildrenCount(root)):
          child =  self.nav.GetNextChild(root)

    self.output.Debug(self, "Found Project %s" % project.get_name())

      #implement the image and the title
    #create all the document type folders

