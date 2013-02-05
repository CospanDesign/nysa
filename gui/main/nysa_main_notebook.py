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

#Classes
class TabPanelOne(wx.Panel):
  def __init__(self, parent):
    ''''''
    wx.Panel.__init__(self, parent=parent, id = wx.ID_ANY)
    sizer = wx.BoxSizer(wx.VERTICAL)
    #txtone = wx.TextCtrl(self, wx.ID_ANY, "")
    #sizer.Add(txtone, 0, wx.ALL, 5)
    self.SetSizer(sizer)


class NysaNotebook( aui.AuiNotebook ) :
    """ AUI Notebook class
      Useful Functions:
        GetCurrentPage
        SetFocusedPage
    """
    def __init__( self, parent ) :
        """  """
        aui.AuiNotebook.__init__( self, parent=parent )
        self.default_style = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER
        self.SetWindowStyleFlag( self.default_style )

    def AddPage (self, text):
      page = TabPanelOne(self)
      aui.AuiNotebook.AddPage( self, page, text )


