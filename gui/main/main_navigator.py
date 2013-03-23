import wx
import wx.gizmos as gizmos

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
    self.nav = gizmos.TreeListCtrl(self, size= (200, -1), style=wx.TR_HIDE_ROOT)
    self.nav.SetSizeHints(200, -1, -1, -1)
    self.nav.AddColumn("Project")
    self.nav.SetMainColumn(0)
    self.nav.AddColumn("File")
    self.nav.AddRoot("Root")
    self.nav.Expand(self.nav.GetRootItem())

  def addWorkspace(self, workspace_name):
    self.output.Verbose(self, "Adding workspace %s" % workspace_name)
    self.workspaceCombo.Insert(workspace_name, 0)
    self.workspaceCombo.SetSelection(0)
