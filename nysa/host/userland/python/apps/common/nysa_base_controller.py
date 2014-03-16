# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


""" nysa base controller
"""


from PyQt4.Qt import QObject



class ScriptPlugin(type):
    def __init__(cls, name, bases, attrs):
        if cls is None:
            return
        if not hasattr(cls, 'plugins'):
            '''
            This is only implemented when the metaclass is first instantiated

            Create the class variable
            '''
            cls.plugins = []
        else:
            print "Adding: %s" % str(cls)
            '''
            This is a plugin class so add it to the plugins class variable
            '''
            cls.plugins.append(cls)

class NysaBaseController:

    __metaclass__ = ScriptPlugin

    def __init__(self):
        self.actions = None
        self.status = None
        super(NysaBaseController, self).__init__()

    def start_standalone_app(self):
        raise NotImplemented("Start standalone app not implemented!")

    def set_nysa_viewer_controls(self, actions, status):
        self.actions = actions
        self.status = status
   
    @staticmethod
    def get_name():
        raise NotImplemented("get_name is not implemented")

    @staticmethod
    def get_unique_image_id():
        raise NotImplemented("get_unique_image_id is not implemented! if not using return None")

    @staticmethod
    def get_device_id():
        raise NotImplemented("get_device_id is not implemented! if not using return None")

    @staticmethod
    def get_device_sub_id():
        raise NotImplemented("get_device_sub_id is not implemented! if not using return None")

    @staticmethod
    def get_device_unique_id():
        raise NotImplemented("get_device_unique_id is not implemented! If not using return None")

