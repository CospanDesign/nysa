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
import inspect

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

PADDING = 5

class WizardPage (wizmod.PyWizardPage):

  page_dict = None
  parent = None
  next_page = None
  prev_page = None
  response_dict = None
  output = None
  sizer = None
  window = None


  def __init__(self, parent = None, page_dict = None, output = None):

    #output.Debug(self, str("Parent: %s" % str(parent)))
    wx.wizard.PyWizardPage.__init__(self, parent)
    self.parent = parent
    self.page_dict = page_dict
    self.output = output

    #use the GridBagSizer to support adding items across multiple cells
    szr = wx.BoxSizer(wx.VERTICAL)
    title = wx.StaticText(self, wx.ID_ANY, page_dict["title"])
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

    #add the title to the top of the wizard
    szr.AddWindow(title, 0, wx.ALIGN_LEFT|wx.ALL, PADDING)
    #Create a main window
    self.window = wx.Panel(self)
    #Add it to the wizard
    szr.Add(self.window, flag=(wx.EXPAND | wx.ALL))

    #Add all the items to the wizard
    self.SetSizer(szr)

    #creat a flexible grid wizard to use with the main window
    self.sizer = wx.GridBagSizer()
    self.window.SetSizer(self.sizer)


    self.process_dictionary(page_dict)
    response_dict = {}

  def process_dictionary(self, page_dict):
    #add the image
    image = None
    if "image" in page_dict.keys():
      self.output.Debug(self, str("\timage path: %s" % page_dict["image"]))
    #add the title
    self.output.Debug(self, str("\ttitle: %s" % page_dict["title"]))
    #add the description
    self.output.Debug(self, str("\tdescription: %s" % page_dict["description"]))


    self.sizer.Add(wx.StaticText(self, wx.ID_ANY, page_dict["title"]), (0, 0), (0, 14), wx.ALIGN_LEFT, border = 0, userData = 0)
    desc = wx.StaticText(self, wx.ID_ANY, page_dict["description"])
    #desc.Wrap()
    if image is None:
      self.sizer.Add(desc, (1, 0), (3, 14), wx.ALIGN_LEFT, border = 0, userData = 0)
    else:
      image = wx.Image(page_dict["image"], wx.BITMAP_TYPE_PNG).ConvertToBitmap()
      page_image = wx.StaticBitmap(self.window, wx.ID_ANY, image)
      self.sizer.Add(page_image, (1,0), (3, 3), wx.ID_ANY)
      self.sizer.Add(desc(1,3), (3, 11), wx.ALIGN_LEFT, border = 0, userData = 0)

    #set the initial height to just the title/descriptor/image height
    page_width  = 14

    page_height = 4

    #calculate the number of extra boxes required for all the items
    #for every item add 3 blocks
    #page_height = page_height + (len(page_dict["items"]) * 3)
    item_list = page_dict["items"]


    #go through each of the items and add all the components
    for i in xrange(len(item_list)):
      item_height = 3
      item_handle = None
      item = item_list[i]

      position = 0
      self.output.Debug(self, str("Processing: %s" % item["title"]))
      if "gui" not in item.keys():
#XXX: This should really be a raised event
        self.output.Error(self, str("gui key not found in the item dictionary"))

      if "text_box" == item["gui"]:
        #if the gui component is textbox call add_text_box
        item_handle, item_height = self.add_text_box(item)
      elif "checkbox_set" == item["gui"]:
        #if the gui component is combobox check to see if the list is static or dynamic
        item_handle, item_height = self.add_checkbox_set(item)
      elif "radiobutton_set" == item["gui"]:
        #if the gui component is radiobutton_set call add_radio_buttons_set
        item_handle, item_height = self.add_radio_buttons_set(item)
      elif "combobox" == item["gui"]:
        #if the gui component is checkbox_set call add_checkbox_set
        item_handle, item_height = self.add_combobox(item)
      elif "spinner" == item["gui"]:
        item_handle, item_height = self.add_spinner(item)

      else:
        self.output.Error(self, str("Item: (%s) in wizard was not recognized" % item["gui"]))

      if item_handle is None:
        self.output.Error(self, str("gui component (%s) is None, Can't add a 'None' to a GUI panel" % item["title"]))

      self.output.Debug(self, "Got GUI component")

      #add the count
      text = wx.StaticText(self.window, label=str(i + 1))
      self.sizer.Add(text, (((i * 3) + page_height), 0), (3, 0))
      position = position + 1
      if "image" in item.keys():
        image = wx.Image(item["image"], wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        item_image = wx.StaticBitmap(self.window, wx.ID_ANY, image)
        self.sizer.Add(item_image, (((i * 3) + page_height), 1), (3, 3))
        position = position + 3

      #add the title and the description
      self.sizer.Add(wx.StaticText( self.window,
                                    wx.ID_ANY,
                                    item["title"]),
                                    (((i * item_height) + page_height), position),
                                    (1, (page_width - 3 - position)))

      self.sizer.Add(wx.StaticText( self.window,
                                    wx.ID_ANY,
                                    item["description"]),
                                    (((i * item_height) + page_height), position),
                                    (2, (page_width - 3 - position)))



  def add_checkbox_set(self, data):
    self.output.Debug(self, "Adding checkboxs")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    size = 0
    #Need a callback that will fill in the values for the user when they change a textbox value
    for cbox_item in data["list"]:
      cbox = wx.CheckBox(panel, label=cbox_item)
      szr.Add(cbox, -1, flag=wx.EXPAND, userData=(data, cbox_item))
      wx.EVT_CHECKBOX(self, cbox.GetId(), self.update_checkbox_response)
      size = size + 1

    if size < 3:
      size = 3

    return panel, size

  def add_radio_buttons_set(self, data):
    self.output.Debug(self, "Adding radiobuttons")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    size = 0
    for rbtn_item in data["list"]:
      rbtn = wx.RadioButton(panel, label=rbtn_item)
      szr.Add(rbtn, -1, flag=wx.EXPAND, userData=(data, rbtn_item))
      wx.EVT_RADIOBUTTON(self, rbtn.GetId(), self.update_radio_response)

      size = size + 1

    if size < 3:
      size = 3

    return panel, size

  def add_text_box(self, data):
    self.output.Debug(self, "Adding Text Box")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    txt = wx.TextCtrl(panel, value="")
    if "default" in data.keys():
      txt.SetValue(data["default"])

    szr.Add(txt, -1, flag=wx.EXPAND, userData=data)
    return panel, 3

  def add_spinner(self, data):
    self.output.Debug(self, "Adding Spinner")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    num = wx.SpinCtrl(panel)
    num.SetRange(data["min"], data["max"])
    if "default" in data.keys():
      num.SetValue(data["default"])

    szr.Add(num, -1, flag=wx.EXPAND, userData=data)


    return panel, 3

  def add_combobox(self, data):
    self.output.Debug(self, "Adding Spinner")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    if type(data["list"]) == list:
      #is this a static list, or a list from data?
      #if the list is static just call add_combobox with the list
      choices = data["list"]
    else:
      #if the list is dynamic call the function provided to get the data then call add_combobox
      if callable(data["list"]):
        choices = data["list"]()
      else:
        self.output.Error(self, "This should be a method!!!: %s" % data["list"])
        choices = []


    cb = wx.ComboBox(panel, choices = choices)
    szr.Add(cb, -1, flag=wx.EXPAND, userData = data)

    return panel, 3

  def get_response(self):
    #need to read the response from the text entry items
    return response_dict

  def update_checkbox_response(self, event):
    #I should be able to extract the user data and update the entry for the response in here (match tag with the
    #name in the response key
    item_name = ""
    item, item_name = event.GetClientData()
    self.output.Debug(self, str("Event entered checkbox response event for: %s checkbox item: %s" % (item, item_name)))

  def update_radio_response(self, event):
    item_name = ""
    item, item_name = event.GetClientData()
    self.output.Debug(self, str("Event entered radiobutton response event for: %s radio button: %s" % (item, item_name)))


class WizardInterpreter(wx.wizard.Wizard):

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
      image = wx.Image(wizard_dict["image"], wx.BITMAP_TYPE_PNG).ConvertToBitmap()

    title = "Wizard"
    if "title" in wizard_dict.keys():
      title = wizard_dict["title"]

    #extrapolate the name and if there is an image from the dicationary
    wx.wizard.Wizard.__init__(self, None, wx.ID_ANY, title, image)
    self.process_wizard()


    self.Bind(wizmod.EVT_WIZARD_PAGE_CHANGED, self.on_page_changed)
    self.Bind(wizmod.EVT_WIZARD_PAGE_CHANGING, self.on_page_changing)
    self.Bind(wizmod.EVT_WIZARD_CANCEL, self.on_cancel)
    self.Bind(wizmod.EVT_WIZARD_FINISHED, self.on_finished)

  def process_wizard(self):
    pages_dict = self.wizard_dict["pages"]

    for page in pages_dict.keys():
      pd = pages_dict[page]
      self.output.Debug(self, str("Added: %s" % page))
      self.add_page(pd)

  def add_page (self, page_dict):
    wp  = WizardPage(parent = self, page_dict = page_dict, output = self.output)
    self.pages.append(wp)

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
