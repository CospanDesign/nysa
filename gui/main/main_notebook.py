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

import wx
import wx.lib.agw.aui as aui
import wx.lib.agw.flatnotebook as fnb

#Classes
class TabPanelOne(wx.Panel):
  def __init__(self, parent):
    ''''''
    wx.Panel.__init__(self, parent=parent, id = wx.ID_ANY)
    sizer = wx.BoxSizer(wx.VERTICAL)
    #txtone = wx.TextCtrl(self, wx.ID_ANY, "")
    #sizer.Add(txtone, 0, wx.ALL, 5)
    self.SetSizer(sizer)


class MainNotebook( aui.AuiNotebook ) :
    """ AUI Notebook class
      Useful Functions:
        GetCurrentPage
        SetFocusedPage
    """
    def __init__( self, parent ) :
      """  """
      aui.AuiNotebook.__init__( self, parent=parent )
      #self.default_style = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER | aui.AUI_NB_SMART_TABS | aui.AUI_NB_TAB_FLOAT
      self.default_style =  aui.AUI_NB_DEFAULT_STYLE | \
                            aui.AUI_NB_TAB_EXTERNAL_MOVE | \
                            aui.AUI_NB_SMART_TABS | \
                            aui.AUI_NB_TAB_FLOAT  | \
                            aui.AUI_NB_SUB_NOTEBOOK | \
                            aui.AUI_NB_DRAW_DND_TAB 

      self.SetName ("main_notebook")


      self.SetWindowStyleFlag( self.default_style )
      #mirror = ~(fnb.FNB_VC71 | fnb.FNB_VC8 | fnb.FNB_FANCY_TABS | fnb.FNB_FF2)
      #self.SetWindowStyleFlag( style )
      self.parent = parent
      self.output = parent.get_output()
      self.set_theme()

    def set_theme(self):
      self.SetArtProvider(aui.AuiDefaultTabArt())

    def AddPage (self, page = None, text = ""):
      if page is None:
        page = TabPanelOne(self)

      aui.AuiNotebook.AddPage( self, page, text )


