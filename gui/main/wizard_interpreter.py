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

import os
import sys

import wx
import wx.wizard as wizmod
import wx.lib.agw.aui as aui

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))

from nysa.gui.main import main_status
from nysa.gui.main.main_status import StatusLevel

'''
This code was inspried by

wiki.wxpython.org/wxWizard

Mike Miller
'''

class WizardPage (wizmod.PyWizardPage):

  page_dict = None
  parent = None
  next_page = None
  prev_page = None
  response_dict = None

  def __init__(self, parent, page_dict):
    self.parent = parent
    self.page_dict = page_dict
    self.parse_dict(page_dict)
    response_dict = {}
    
  def process_dictionary(self, page_dict):
    #add the image
    #add the title
    #add the description

    #calculate the number of extra boxes required for all the items

    #go through each of the items and add all the components
    #add the image
    #add the title
    #add the description
    #if the gui component is checkbox_set call add_checkbox_set
    #if the gui component is radiobutton_set call add_radio_buttons_set
    #if the gui component is textbox call add_text_box
    #if the gui component is combobox check to see if the list is static or dynamic
    #   if the list is static just call add_combo_box with the list
    #   if the list is dynamic call the function provided to get the data then call add_combo_box
    pass

  def add_checkbox_set(self, data):
    pass

  def add_radio_buttons_set(self, data):
    pass

  def add_text_box(self, data):
    pass

  def add_num_text_box(self, data):
    pass

  def add_combo_box(self, data):
    #is this a static list, or a list from data?
    pass

  def get_resposne(self):
    return response_dict


class WizardInterpreter(wizmod.Wizard):
  
  wizard_dict = None
  response_dict = None
  pages = []

  def __init__(self, wizard_dict = None, output = None, project = None, dbg = False):
    if output is None:
      self.output = main_status.Dummy()
      if dbg:
        self.output.SetLevel(StatusLevel.VERBOSE)
      else:
        self.output.SetLevel(StatusLevel.INFO)
    else:
      self.output = output

    self.wizard_dict = wizard_dict

    image = wx.NullBitmap
    if "image" in wizard_dict.keys():
      image = wizard_dict["image"]
      
    title = "Wizard"
    if "title" in wizard_dict.keys():
      title = wizard_dict["title"]

    #extrapolate the name and if there is an image from the dicationary
    wizmod.Wizard.__init__(self, None, wx.ID_ANY, title, image)

    self.Bind(wizmod.EVT_WIZARD_PAGE_CHANGED, self.on_page_changed)
    self.Bind(wizmod.EVT_WIZARD_PAGE_CHANGING, self.on_page_changing)
    self.Bind(wizmod.EVT_WIZARD_CANCEL, self.on_cancel)
    self.Bind(wizmod.EVT_WIZARD_FINISHED, self.on_finished)

  def process_wizard(self):
    pass

  def add_page (self, page_dict):
    pass

  def run(self):
    pass

  def on_page_changed(self, evt):
    pass

  def on_page_changing(self, evt):
    pass

  def on_cancel(self, evt):
    pass

  def on_finished(self, evt):
    pass
