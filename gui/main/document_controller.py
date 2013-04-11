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
import os
import sys

import main_status
from main_status import StatusLevel


sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


from nysa.gui.plugins.document_plugin_manager import DocumentPluginManager as DPM

class DocumentError(Exception):
  """DocumentError

  Errors associated with documents in particular:
    Document Type Not Found
    Document with name already exists
    Document Not Found
  """
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


class DocumentController():
  output = None
  dbg = False
  dpm = None
  focused_doc = None

  def __init__(self, output=None, dbg=False):
    self.dbg = dbg
    self.output = None

    if output is None:
      self.output = main_status.Dummy()
      if self.dbg:
        self.output.SetLevel(StatusLevel.VERBOSE)
      else:
        self.output.SetLevel(StatusLevel.INFO)
    else:
      self.output = output

    self.dpm = DPM(output = self.output, dbg=dbg)
    self.output.Debug(self, "Started")


  def new_document(self, document_type, name):
    """Create a new document of the type 'document type'
    with the name 'name' and return a reference to it"""
    self.output.Debug(self, "Create a new document of type %s with name: %s" % (document_type, name))
    if document_type not in self.dpm.get_plugin_names():
      raise DocumentError("Document Type: %s not found, available types include %s" % 
                            (document_type, self.dpm.get_plugin_names()))

    #instantiate a new document with type name
    doc = self.dpm.new_document(document_type, name)
    return doc

  def open_document(self, document_type, file_path):
    """open a new document of the type: document_type at locatoin file_path"""
    self.output.Debug(self, "Opening File of type: %s" % document_type)
    if document_type not in self.dpm.get_plugin_names:
      raise DocumentError("Document Type: %s not found, available types include %s" % 
                            (document_type, self.dpm.get_plugin_names()))
    return None

  def save_document(self, document, file_path):
    """Saves a document to the file path specified"""
    self.output.Debug(self, "Saving document to: %s" % file_path)

  def get_types(self):
    return self.dpm.get_plugin_names() 

  def set_focused_document(self, doc):
    self.output.Debug(self, "New Focused document: %s" % doc.get_name)
    self.focused_doc = doc

  def lose_focus(self):
    self.output.Debug(self, "Unfocus all docuemnts")
    self.focused_doc = None

  def toolevent(self, evt):
    """Redirect toolevents to the focused document"""
    if self.focused_doc is None:
      raise DocumentError("Received event (%s) for a document even though there is no focues docuemnt" % str(evt))
    self.output.Debug(self, "Redirecting event %s to %s" % (str(evt), self.focused_doc.get_name()))
    self.focus_doc.handle_toolevent(evt)

  def activate_tools(self):
    """Activate a tool for the focuesed document"""
    #I need a reference to all the document widgets that are available
    #only load toolbars for documents that are active
    self.output.Debug(self, "Activate tools for %s" % self.focused_doc.get_name())
    

