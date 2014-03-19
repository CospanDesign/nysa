import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


os.path.join(os.path.dirname(__file__),
             os.pardir,
             os.pardir,
             os.pardir)

import status
import actions


from properties_base import PropertiesBase

class HostInterfaceProperties(PropertiesBase):

    def __init__(self):
        super (HostInterfaceProperties, self).__init__()

        self.actions = actions.Actions()
        self.status = status.Status()
        self.initialize_default_form_view()

        self.set_name("Host Interface")
        self.set_info("Facilitates communication between host and nysa platfrom")
                        
        self.hide()


    def set_config_dict(self, config_dict):
        self.config_dict = config_dict
        #Setup the reset of the config dict
