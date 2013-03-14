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

import json

class PluginLoader ():
  def __init__(self):
    pass

  def load_gui_plugin(self, plugin_dir, main_frame, plugin_gui_config, plugin_module):
    """
      loads the main_frame with the GUI elements within plugin_config and sets up the
      events in plugin_module and sets

      Args:

        workspace_manager: Workspace manager in charge of

      Returns:
        Nothing upon success

      Raises:
        PluginGuiException
    """
    pass

  def load_workspace_project(self, plugin_dir, workspace_manager, plugin_ws_config, plugin_module):
    """
      loads the workspace manager with a project of the type plugin, uses the plugin_ws_config to setup the main view
      and the plugin_module to set up the module
    """
    pass

  def add_new_file_to_project(self, plugin_module, file_type):
    """
      adds a new file of the type 'file_type' to the plugin project
    """
    pass

  def unload_workspace_project(self):
    pass
