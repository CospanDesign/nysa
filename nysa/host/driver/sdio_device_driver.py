#PUT LICENCE HERE!

"""
SDIODevice Driver

"""

import sys
import os
import time
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))
from nysa.host.driver import driver

white = '\033[0m'
gray = '\033[90m'
red = '\033[91m'
green = '\033[92m'
yellow = '\033[93m'
blue = '\033[94m'
purple = '\033[95m'
cyan = '\033[96m'

if os.name == "nt":
    white  = ''
    gray   = ''
    red    = ''
    green  = ''
    yellow = ''
    blue   = ''
    purple = ''
    cyan   = ''



#Sub Module ID
#Use 'nysa devices' to get a list of different available devices
DEVICE_TYPE             = "SDIO Device"
SDB_ABI_VERSION_MINOR   = 0x01
SDB_VENDOR_ID           = 0x800000000000C594

BUFFER_SIZE             = 0x00000400

#Register Constants
CONTROL_ADDR            = 0x00000000
STATUS_ADDR             = 0x00000001
CLOCK_COUNT_ADDR        = 0x00000002
DEBUG_SD_CMD            = 0x00000003
DEBUG_SD_CMD_ARG        = 0x00000004
DEBUG_SD_PHY_STATE      = 0x00000005
DEBUG_SD_CONTROL_STATE  = 0x00000006
SD_DELAY_VALUE          = 0x00000007
SD_DBG_CRC_GEN          = 0x00000023
SD_DBG_CRC_RMT          = 0x00000024



BUFFER_OFFSET           = 0x00000400

CNTRL_BIT_ENABLE            = 0
CNTRL_BIT_INTERRUPT         = 1
CNTRL_BIT_SEND_INTERRUPT    = 2
CNTRL_BIT_ENABLE_DEBUG_INT  = 3
CNTRL_BIT_USER_RESET        = 4


class SDIODeviceDriver(driver.Driver):

    """ SDIODevice

        Communication with a DutDriver SDIODevice Core
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
        super(SDIODeviceDriver, self).__init__(nysa, urn, debug)

    def set_control(self, control):
        self.write_register(CONTROL_ADDR, control)

    def get_control(self):
        return self.read_register(CONTROL_ADDR)

    def get_status(self):
        return self.read_register(STATUS_ADDR)

    def get_clock_count(self):
        return self.read_register(CLOCK_COUNT_ADDR)

    def get_sd_cmd(self):
        return self.read_register(DEBUG_SD_CMD)

    def get_sd_cmd_arg(self):
        return self.read_register(DEBUG_SD_CMD_ARG)

    def reset_core(self):
        self.set_register_bit(CONTROL_ADDR, CNTRL_BIT_USER_RESET)

    def write_local_buffer(self, addr, data):
        #Make sure data is 32-bit Aligned
        data = Array('B', data)
        while len(data) % 4 > 0:
            data.append(0x00)

        self.write(BUFFER_OFFSET + addr, data)

    def read_local_buffer(self, addr, length):
        return self.read(BUFFER_OFFSET + addr, length)

    def enable_interrupt(self, enable):
        self.enable_register_bit(CONTROL_ADDR, CNTRL_BIT_INTERRUPT, enable)

    def is_interrupt_enable(self):
        return self.is_register_bit_set(CONTROL_ADDR, CNTRL_BIT_INTERRUPT)

    def enable_sdio_device(self, enable):
        self.enable_register_bit(CONTROL_ADDR, CNTRL_BIT_ENABLE, enable)

    def is_sdio_device_enabled(self):
        return self.is_register_bit_set(CONTROL_ADDR, CNTRL_BIT_ENABLE)

    def enable_interrupt_to_host(self, enable):
        self.enable_register_bit(CONTROL_ADDR, CNTRL_BIT_SEND_INTERRUPT, enable)

    def is_interrupt_to_host_enabled(self):
        return self.is_register_bit_set(CONTROL_ADDR, CNTRL_BIT_SEND_INTERRUPT)

    def set_input_delay(self, delay):
        delay = delay % 256
        self.write_register(SD_DELAY_VALUE, delay)

    def get_input_delay(self):
        return self.read_register(SD_DELAY_VALUE)

    def display_control(self):
        control = self.get_control()
        print yellow,
        print "SDIO Device Control"
        if (control & (1 << CNTRL_BIT_ENABLE)) > 0:
            print "\tSDIO Device Enabled"
        if (control & (1 << CNTRL_BIT_INTERRUPT)) > 0:
            print "\tSDIO Device Interrupt Enabled"
        if (control & (1 << CNTRL_BIT_SEND_INTERRUPT)) > 0:
            print "\tSDIO Device Send Interrupt"
        if (control & (1 << CNTRL_BIT_ENABLE_DEBUG_INT)) > 0:
            print "\tSDIO Device Enable Debug Interrupt When Command Arrives"
        if (control & (1 << CNTRL_BIT_USER_RESET)) > 0:
            print "\tSDIO Device User Reset %s" % white

    def read_phy_state(self):
        return self.read_register(DEBUG_SD_PHY_STATE)

    def read_control_state(self):
        return self.read_register(DEBUG_SD_CONTROL_STATE)

    def get_gen_crc(self):
        return self.read_register(SD_DBG_CRC_GEN)
        
    def get_rmt_crc(self):
        return self.read_register(SD_DBG_CRC_RMT)
 
    def display_crcs(self):
        gen_crc = self.get_gen_crc()
        rmt_crc = self.get_rmt_crc()
        print "SDIO Device CRCs:"
        print "\tGen CRC:       0x%02X" % gen_crc
        print "\tRemote CRC:    0x%02X" % rmt_crc

    def display_status(self):
        status = self.get_status()
        phy_state = self.read_phy_state()
        cntrl_state = self.read_control_state()
        print purple,
        print "SDIO Device Status:"
        if (status & 0x01) > 0:
            print "\tPLL Locked"
        if (status & 0x02) > 0:
            print "\tSDIO Function Ready for Data"
        if (status & 0x04) > 0:
            print "\tSDIO Function is Busy"
        if (status & 0x08) > 0:
            print "\tSDIO Function is ready"
        if (status & 0x10) > 0:
            print "\tSDIO Phy Layer is IDLE"
        if (status & 0x20) > 0:
            print "\tSDIO Command Strobe Detected"

        print "\tSDIO Phy State: 0x%02X" % phy_state
        print "\tSDIO Control State: 0x%02X %s" % (cntrl_state, white)


