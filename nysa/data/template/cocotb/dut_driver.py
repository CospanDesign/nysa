#PUT LICENCE HERE!

"""
${SDB_NAME} Driver

"""

import sys
import os
import time
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))
from nysa.host.driver import driver

#Sub Module ID
#Use 'nysa devices' to get a list of different available devices
DEVICE_TYPE             = "${DEVICE_NAME}"
SDB_ABI_VERSION_MINOR   = ${SDB_ABI_VERSION_MINOR}
SDB_VENDOR_ID           = ${SDB_VENDOR_ID}

#Register Constants
CONTROL_ADDR            = 0x00000000
ZERO_BIT                = 0

class ${SDB_NAME}Driver(driver.Driver):

    """ ${SDB_NAME}

        Communication with a DutDriver ${SDB_NAME} Core
    """
    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return driver.get_device_id_from_name(DEVICE_TYPE)

    @staticmethod
    def get_abi_minor():
        return SDB_ABI_VERSION_MINOR

    @staticmethod
    def get_vendor_id():
        return SDB_VENDOR_ID

    def __init__(self, nysa, urn, debug = False):
        super(${SDB_NAME}, self).__init__(nysa, urn, debug)

    def set_control(self, control):
        self.write_register(CONTROL_ADDR, control)

    def get_control(self):
        return self.read_register(CONTROL_ADDR)

    def enable_control_0_bit(self, enable):
        self.enable_register_bit(CONTROL_ADDR, ZERO_BIT, enable)

    def is_control_0_bit_set(self):
        return self.is_register_bit_set(CONTROL_ADDR, ZERO_BIT)
