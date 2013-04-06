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
  response_dict = {}
  output = None
  sizer = None
  window = None
  next_page = None
  prev_page = None
  wizard_page_size = None
  title = ""
  id_map = {}


  def __init__(self, parent = None, page_dict = None, output = None):

    #output.Debug(self, str("Parent: %s" % str(parent)))
    wx.wizard.PyWizardPage.__init__(self, parent)
    self.response_dict = {}
    self.parent = parent
    self.page_dict = page_dict
    self.output = output
    self.title = page_dict["title"]

    #use the GridBagSizer to support adding items across multiple cells
    szr = wx.BoxSizer(wx.VERTICAL)
    title = wx.StaticText(self, wx.ID_ANY, page_dict["title"])
    title.SetFont(wx.Font(18, wx.ROMAN, wx.NORMAL, wx.BOLD))

    #add the title to the top of the wizard
    #szr.AddWindow(title, 0, (wx.EXPAND | wx.ALIGN_LEFT | wx.ALL), PADDING)
    szr.Add(title, flag = (wx.EXPAND | wx.ALIGN_LEFT | wx.ALL))
    #Create a main window
    self.window = wx.Panel(self)
    #Add it to the wizard

    #Add all the items to the wizard

    #creat a flexible grid wizard to use with the main window
    self.sizer = wx.GridBagSizer()
    self.window.SetSizer(self.sizer)

    self.id_map = {}
    self.process_dictionary(page_dict)
    szr.Add(self.window, flag=(wx.EXPAND | wx.ALL))
    self.wizard_page_size = szr
    self.SetSizer(szr)

    #self.SetAutoLayout(True)
    #self.Bind(wx.EVT_SIZE, self.OnSize)
    #self.output.Info(self, "Compute Fitted window size: %s" % self.wizard_page_size.ComputeFittingClientSize(self))
    #self.output.Info(self, "Compute Fitted window size: %s" % self.wizard_page_size.ComputeFittingWindowSize(self))

  def GetTitle(self):
    return self.title

  def process_dictionary(self, page_dict):
    #add the image
    image = None
    page_width  = 15
    item_width = 4
    num_size = 1

    self.sizer.SetVGap(5)
    self.sizer.SetHGap(5)
    if "image" in page_dict.keys():
      self.output.Debug(self, str("\timage path: %s" % page_dict["image"]))
      image = page_dict["image"]

    #add the title
    self.output.Debug(self, str("\ttitle: %s" % page_dict["title"]))
    #add the description
    self.output.Debug(self, str("\tdescription: %s" % page_dict["description"]))

    st = wx.StaticText(self.window, wx.ID_ANY, page_dict["title"])
    self.sizer.Add(st, (0, 0), (1, page_width), wx.ALIGN_LEFT | wx.EXPAND)
    desc = wx.StaticText(self.window, wx.ID_ANY, page_dict["description"])
    if image is None:
      self.sizer.Add(desc, (1, 0), (3, page_width), wx.ALIGN_LEFT | wx.EXPAND, border = 0, userData = 0)
    else:
      image = wx.Image(page_dict["image"], wx.BITMAP_TYPE_PNG).ConvertToBitmap()
      page_image = wx.StaticBitmap(self.window, wx.ID_ANY, image)
      self.sizer.Add(page_image, (1,0), (3, 3), wx.ID_ANY)
      self.sizer.Add(desc, (1,3), (3, 11), wx.ALIGN_LEFT | wx.EXPAND, border = 0, userData = 0)

    #set the initial height to just the title/descriptor/image height

    page_height = 4

    #calculate the number of extra boxes required for all the items
    #for every item add 3 blocks
    #page_height = page_height + (len(page_dict["items"]) * 3)
    item_list = page_dict["items"]
    yloc = page_height


    #go through each of the items and add all the components
    for i in xrange(len(item_list)):
      item_height = 3
      item_handle = None
      item = item_list[i]

      position = 0
      #self.output.Debug(self, str("Processing: %s" % item["title"]))
      if "gui" not in item.keys():
#XXX: This should really be a raised event
        self.output.Error(self, str("gui key not found in the item dictionary"))
        self.response_dict[data["tag"]] = None

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
      else:
        self.sizer.Add(item_handle, (yloc, 11), (item_height, 3))

      #self.output.Debug(self, "Got GUI component")

      #add the count
      num = str(i + 1)
      st = wx.StaticText(self.window, wx.ID_ANY, num)
      st.SetFont(wx.Font(18, wx.ROMAN, wx.NORMAL, wx.BOLD))
      self.sizer.Add(st, (yloc, 0), (3, 1), wx.ALIGN_CENTER, PADDING)

      position = position + 1
      if "image" in item.keys():
        image = wx.Image(item["image"], wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        item_image = wx.StaticBitmap(self.window, wx.ID_ANY, image)
        self.sizer.Add(item_image, (yloc, 1), (3, 3), PADDING)
        position = position + 3
      #add the title and the description
      st = wx.StaticText(self.window, wx.ID_ANY, item["title"])
      self.sizer.Add( st,
                      (yloc, position),
                      (1, (page_width - item_width - position)))

      st = wx.StaticText(self.window, wx.ID_ANY, item["description"])
      self.sizer.Add(st,
                     (yloc + 1, position),
                     (2, (page_width - item_width - position)))

      yloc = yloc + item_height

    self.sizer.Layout()
    self.Layout()

  def add_checkbox_set(self, data):
    #self.output.Debug(self, "Adding checkboxs")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(szr)
    size = 0
    self.output.Debug(self, "Tag: %s" % data["tag"])
    self.response_dict[data["tag"]] = {}
    #Need a callback that will fill in the values for the user when they change a textbox value
    for cbox_item in data["list"]:
      self.response_dict[data["tag"]][cbox_item] = False
      cbox = wx.CheckBox(panel, label=cbox_item)
      szr.Add(cbox, flag=wx.EXPAND | wx.ALL)
      self.id_map[cbox.GetId()] = cbox_item, data["tag"]
      cbox.Bind(wx.EVT_CHECKBOX, self.update_checkbox_response)
      size = size + 1

    if size < 3:
      size = 3

    return panel, size

  def add_radio_buttons_set(self, data):
    #self.output.Debug(self, "Adding radiobuttons")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(szr)
    size = 0
    for rbtn_item in data["list"]:
      rbtn = wx.RadioButton(panel, label=rbtn_item)
      self.id_map[rbtn.GetId()] = rbtn_item, data["tag"]
      szr.Add(rbtn, flag=wx.EXPAND | wx.ALL)
      rbtn.Bind(wx.EVT_RADIOBUTTON, self.update_radio_response)
      size = size + 1

    if size < 3:
      size = 3

    return panel, size

  def add_text_box(self, data):
    #self.output.Debug(self, "Adding Text Box")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(szr)
    txt = wx.TextCtrl(panel, value="")
    self.response_dict[data["tag"]] = ""
    if "default" in data.keys():
      txt.SetValue(data["default"])
      self.id_map[txt.GetId()] = txt, data["tag"]
      txt.Bind(wx.EVT_TEXT, self.update_text_box)
      self.response_dict[data["tag"]] = data["default"]

    szr.Add(txt, -1, flag=wx.EXPAND | wx.ALL, userData=data)
    return panel, 3

  def add_spinner(self, data):
    #self.output.Debug(self, "Adding Spinner")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    num = wx.SpinCtrl(panel)
    num.SetRange(data["min"], data["max"])
    self.response_dict[data["tag"]] = data["min"]
    panel.SetSizer(szr)
    self.id_map[num.GetId()] = data["title"], data["tag"]
    if "default" in data.keys():
      num.SetValue(data["default"])
      self.response_dict[data["tag"]] = data["default"]

    szr.Add(num, -1, flag=wx.EXPAND, userData=data)
    num.Bind(wx.EVT_SPINCTRL, self.update_spinner)
    return panel, 3

  def add_combobox(self, data):
    #self.output.Debug(self, "Adding Spinner")
    panel = wx.Panel(self.window)
    szr = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(szr)
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
    cb.SetSelection(0)
    self.response_dict[data["tag"]] = cb.GetCurrentSelection()
    szr.Add(cb, -1, flag=wx.EXPAND, userData = data)

    self.id_map[cb.GetId()] = data["title"], data["tag"]
    self.Bind(wx.EVT_COMBOBOX, self.update_combobox)

    return panel, 3

  def get_response(self):
    #need to read the response from the text entry items
    return self.response_dict

  def update_checkbox_response(self, event):
    #I should be able to extract the user data and update the entry for the response in here (match tag with the
    #name in the response key
    item, tag = self.id_map[event.GetId()]
    self.output.Debug(self, str("Event entered checkbox response event for: %s->%s" % (tag, item)))
    if event.IsChecked():
      self.output.Debug(self, "\tis checked")
    else:
      self.output.Debug(self, "\tis not checked")

    self.response_dict[tag][item] = event.IsChecked()

  def update_radio_response(self, event):
    item, tag = self.id_map[event.GetId()]
    self.output.Debug(self, str("Event entered radiobutton response event for: %s->%s" % (tag, item)))
    self.response_dict[tag] = item

  def update_text_box(self, event):
    item, tag = self.id_map[event.GetId()]
    self.output.Debug(self, str("Event entered text changed for: %s: %s" % (tag, event.GetString())))
    self.response_dict[tag] = event.GetString()

  def update_spinner(self, event):
    item, tag = self.id_map[event.GetId()]
    self.output.Debug(self, str("Event entered Spinner value changed for: %s to %d" % (tag, event.GetInt())))
    self.response_dict[tag] = event.GetInt()

  def update_combobox(self, event):
    item, tag = self.id_map[event.GetId()]
    self.output.Debug(self, str("Event entered combobox value changed %s to %s" % (tag, event.GetString())))
    self.response_dict[tag] = event.GetString()

  def SetNext(self, next_page):
    self.next_page = next_page

  def SetPrev(self, prev_page):
    self.prev_page = prev_page

  def GetNext(self):
    return self.next_page

  def GetPrev(self):
    return self.prev_page


class WizardInterpreter(wx.wizard.Wizard):

  wizard_dict = None
  response_dict = None
  pages = []
  first_page = None
  response_dict = {}

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

    #self.output.Debug(self, "Image path: %s" % wizard_dict["image"])
    image = wx.NullBitmap
    if "image" in wizard_dict.keys():
      image = wx.Image(wizard_dict["image"], wx.BITMAP_TYPE_PNG).ConvertToBitmap()

    title = "Wizard"
    if "title" in wizard_dict.keys():
      title = wizard_dict["title"]

    #extrapolate the name and if there is an image from the dicationary
    wx.wizard.Wizard.__init__(self, None, -1, title, image)
    self.process_wizard()

    self.Bind(wizmod.EVT_WIZARD_PAGE_CHANGED, self.on_page_changed)
    self.Bind(wizmod.EVT_WIZARD_PAGE_CHANGING, self.on_page_changing)
    self.Bind(wizmod.EVT_WIZARD_CANCEL, self.on_cancel)
    self.Bind(wizmod.EVT_WIZARD_FINISHED, self.on_finished)

  def process_wizard(self):
    pages_dict = self.wizard_dict["pages"]

    for page in pages_dict.keys():
      pd = pages_dict[page]
      self.output.Info(self, str("Added: %s" % page))
      self.add_page(pd)

  def add_page (self, page_dict):
    wp  = WizardPage(parent = self, page_dict = page_dict, output = self.output)
    if self.pages:
      prev_page = self.pages[-1]
      wp.SetPrev(prev_page)
      prev_page.SetNext(wp)

    else:
      self.first_page = wp

    self.pages.append(wp)

  def run(self):
    self.GetPageAreaSizer().Add(self.first_page)
    self.RunWizard(self.pages[0])

  def on_page_changed(self, evt):
    '''Executes after page has changed'''
    if evt.GetDirection():
      direction = "forward"
    else:
      direction = "backward"

    page = evt.GetPage()
    #self.SetPageSize(self.GetPageAreaSizer().ComputeFittingClientSize(page))
    #self.Layout()
    #self.SetSize(self.SetPageSize(pgsize.ComputeFittingClientSize(self)))
    self.output.Info(self, "Page Change: %s" % direction)

  def on_page_changing(self, evt):
    '''Execute before page has changed, we can get the information from the page to find out where to go next'''
    if evt.GetDirection():
      direction = "forward"
    else:
      direction = "backward"

    page = evt.GetPage()
    self.output.Info(self, "Page Changing: %s, %s" % (direction, page.__class__))

  def on_cancel(self, evt):
    '''Cancel button has been pressed, Clean up and exit without continuing'''
    page = evt.GetPage()
    self.output.Info(self, "Cancel pressed")

    #if page is self.pages[0]:
    #  wx.MessageBox("Cancelling on the first page has been prevented.", "Sorry")
    #  evt.Veto()

  def on_finished(self, evt):
    '''Finished button has been pressed. Clean up and exit'''
    self.output.Info(self, "Finished")
    for page in self.pages:
      self.response_dict[page.GetTitle()] = page.get_response()

    self.show_response(self.response_dict, 0)


  def show_response(self, rd, tab_depth):
    ts = ""
    for t in xrange(tab_depth):
      ts += "\t"

    for key in rd.keys():
      if type(rd[key]) == dict:
        self.output.Debug(self, "%s%s:" % (ts, key))
        self.show_response(rd[key], tab_depth + 1)
      else:
        self.output.Debug(self, "%s%s:%s" % (ts, key, str(rd[key])))

  def get_response(self):
    return self.response_dict
#  def OnSize(self, evt):
#
#    self.output.Info(self, "Wizard Size: %s" % str(self.GetSize()))
#    if self.GetAutoLayout():
#      self.Layout()



