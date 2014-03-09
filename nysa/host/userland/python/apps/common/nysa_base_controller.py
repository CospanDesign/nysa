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

class NysaBaseController(QObject):

    def __init__(self):
        self.actions = None
        self.status = None
        super(NysaBaseController, self).__init__()

    def start_standalone_app(self):
        raise NotImplemented("Start standalone app not implemented!")

    def set_nysa_viewer_controls(self, actions, status):
        self.actions = actions
        self.status = status

    def get_unique_image_id(self):
        raise NotImplemented("get_unique_image_id is not implemented! if not using return None")

    def get_device_id(self):
        raise NotImplemented("get_device_id is not implemented! if not using return None")

    def get_device_sub_id(self):
        raise NotImplemented("get_device_sub_id is not implemented! if not using return None")

    def get_device_unique_id(self):
        raise NotImplemented("get_device_unique_id is not implemented! If not using return None")
