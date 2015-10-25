#PUT LICENCE HERE!

"""
wb_sd_host Driver

"""


import sys
import os
import time
from array import array as Array


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



sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from nysa.host.driver import driver

#Sub Module ID
#Use 'nysa devices' to get a list of different available devices
DEVICE_TYPE                     = "SD Host"
SDB_ABI_VERSION_MINOR           = 1
SDB_VENDOR_ID                   = 0x800000000000C594

#Register Constants
ZERO_BIT                        = 0

CONTROL                         = 0x000
STATUS                          = 0x001
REG_MEM_0_BASE                  = 0x002
REG_MEM_0_SIZE                  = 0x003
REG_MEM_1_BASE                  = 0x004
REG_MEM_1_SIZE                  = 0x005
SD_ARGUMENT                     = 0x006
SD_COMMAND                      = 0x007
SD_CONFIGURE                    = 0x008
SD_RESPONSE0                    = 0x009
SD_RESPONSE1                    = 0x00A
SD_RESPONSE2                    = 0x00B
SD_RESPONSE3                    = 0x00C
SD_DATA_BYTE_COUNT              = 0x00D
SD_F0_BLOCK_SIZE                = 0x010
SD_F1_BLOCK_SIZE                = 0x011
SD_F2_BLOCK_SIZE                = 0x012
SD_F3_BLOCK_SIZE                = 0x013
SD_F4_BLOCK_SIZE                = 0x014
SD_F5_BLOCK_SIZE                = 0x015
SD_F6_BLOCK_SIZE                = 0x016
SD_F7_BLOCK_SIZE                = 0x017
SD_MEM_BLOCK_SIZE               = 0x018

SD_DELAY_VALUE                  = 0x022
SD_BLOCK_SIZE_OFFSET            = 0x010
SD_DBG_CRC_GEN                  = 0x023
SD_DBG_CRC_RMT                  = 0x024

CONTROL_ENABLE_SD               = 0
CONTROL_ENABLE_INTERRUPT        = 1
CONTROL_ENABLE_DMA_WR           = 2
CONTROL_ENABLE_DMA_RD           = 3
CONTROL_ENABLE_SD_FIN_INT       = 4
CONTROL_DATA_WRITE_FLAG         = 5
CONTROL_DATA_BIT_ACTIVATE       = 6
CONTROL_DATA_BLOCK_MODE         = 7
CONTROL_FUNCTION_ADDRESS_LOW    = 8
CONTROL_FUNCTION_ADDRESS_HIGH   = 10

COMMAND_BIT_GO                  = 16
COMMAND_BIT_RSP_LONG_FLG        = 17

CONFIGURE_EN_CRC                = 4
CONFIGURE_READ_WAIT_SPRT_ADDR   = 8
CONFIGURE_READ_WAIT_SPRT_BIT    = 2

CMD_PHY_MODE                    = 0
CMD_SEND_RELATIVE_ADDR          = 3
CMD_OP_COND                     = 5
CMD_SEL_DESEL_CARD              = 7
CMD_GO_INACTIVE                 = 15
CMD_SINGLE_DATA_RW              = 52
CMD_DATA_RW                     = 53

DATA_RW_WRITE                   = 1
DATA_RW_READ                    = 0
DATA_WRITE_FLAG                 = 31
DATA_FUNC_INDEX                 = 28
DATA_FUNC_BITMASK               = 7
DATA_ADDR                       = 9
DATA_ADDR_BITMASK               = 0x1FFFF
DATA_MASK                       = 0xFF

DATA_RW_BLOCK_MODE              = 27
DATA_RW_OP_CODE                 = 26
DATA_RW_COUNT_BITMODE           = 0x1FF


OP_COND_BIT_EN_1P8V             = 24
OP_COND_BIT_OCR_LOW             = 0

STATUS_MEMORY_0_FINISHED        = 0
STATUS_MEMORY_1_FINISHED        = 1
STATUS_MEMORY_0_EMPTY           = 2
STATUS_MEMORY_1_EMPTY           = 3
STATUS_ENABLE                   = 4
STATUS_SD_BUSY                  = 5
STATUS_SD_DATA_BUSY             = 6
STATUS_SD_READY                 = 7
STATUS_ERROR_BIT_TOP            = 31
STATUS_ERROR_BIT_BOT            = 24


R1_OUT_OF_RANGE                 = 39
R1_COM_CRC_ERROR                = 38
R1_ILLEGAL_COMMAND              = 37
R1_ERROR                        = 19
R1_CURRENT_STATE                = 9
R1_CURRENT_STATE_BITMASK        = 0xF

R4_READY                        = 31
R4_NUM_FUNCS                    = 28
R4_NUM_FUNCS_BITMASK            = 0x7
R4_MEM_PRESENT                  = 27
R4_UHSII_AVAILABLE              = 26
R4_S18A                         = 24
R4_IO_OCR                       = 0
R4_IO_OCR_BITMASK               = 0xFFF

R5_COM_CRC_ERROR                = 15
R5_ILLEGAL_COMMAND              = 14
R5_CURRENT_STATE                = 12
R5_CURRENT_STATE_BITMASK        = 3
R5_ERROR                        = 3
R5_ERROR_FUNC                   = 1
R5_ERROR_OUT_OF_RANGE           = 0

R6_REL_ADDR_BITMASK             = 0xFF
R6_REL_ADDR                     = 16
R6_STS_CRC_COMM_ERR             = 15
R6_STS_ILLEGAL_CMD              = 13
R6_STS_ERROR                    = 12


IO_FUNC_ENABLE_ADDR             = 0x02
INT_ENABLE_ADDR                 = 0x04
INT_PENDING_ADDR                = 0x05

RESPONSE_DICT = {CMD_PHY_MODE           : 1,
                 CMD_SEND_RELATIVE_ADDR : 6,
                 CMD_OP_COND            : 4,
                 CMD_SEL_DESEL_CARD     : 1,
                 CMD_GO_INACTIVE        : None,
                 CMD_SINGLE_DATA_RW     : 5,
                 CMD_DATA_RW            : 5}

class SDHostException(Exception):
    pass

class SDHostDriver(driver.Driver):

    """ wb_sd_host

        Communication with a DutDriver wb_sd_host Core
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
        super(SDHostDriver, self).__init__(nysa, urn, debug)
        self.async_read_callback= None
        self.interrupt_callback = None
        self.async_read_mode = False
        self.block_timeout = 0
        self.byte_count = 0
        self.block_size = 0
        self.read_data = Array('B')
        self.read_in_progress = False
        size = 2048
        self.MEM_BASE_0 = 0x000
        self.MEM_BASE_1 = self.MEM_BASE_0 + size
        self.set_register_bit(CONTROL, CONTROL_DATA_WRITE_FLAG)
        self.dma_reader = driver.DMAReadController(device     = self,
                                            mem_base0  = self.MEM_BASE_0,
                                            mem_base1  = self.MEM_BASE_1,
                                            size       = self.MEM_BASE_1 - self.MEM_BASE_0,
                                            reg_status = STATUS,
                                            reg_base0  = REG_MEM_0_BASE,
                                            reg_size0  = REG_MEM_0_SIZE,
                                            reg_base1  = REG_MEM_1_BASE,
                                            reg_size1  = REG_MEM_1_SIZE,
                                            timeout    = 3,
                                            finished0  = STATUS_MEMORY_0_FINISHED,
                                            finished1  = STATUS_MEMORY_1_FINISHED,
                                            empty0     = STATUS_MEMORY_0_EMPTY,
                                            empty1     = STATUS_MEMORY_1_EMPTY)

        self.dma_writer = driver.DMAWriteController(device     = self,
                                            mem_base0  = self.MEM_BASE_0,
                                            #mem_base1  = 0x00100000,
                                            mem_base1  = self.MEM_BASE_1,
                                            size       = self.MEM_BASE_1 - self.MEM_BASE_0,
                                            reg_status = STATUS,
                                            reg_base0  = REG_MEM_0_BASE,
                                            reg_size0  = REG_MEM_0_SIZE,
                                            reg_base1  = REG_MEM_1_BASE,
                                            reg_size1  = REG_MEM_1_SIZE,
                                            timeout    = 3,
                                            empty0     = STATUS_MEMORY_0_EMPTY,
                                            empty1     = STATUS_MEMORY_1_EMPTY)

        #Error Conditions
        self.error_crc = False
        self.error_illegal_cmd = False
        self.error_unknown = False
        self.error_out_of_range = False
        self.current_state = 0
        self.error_func = 0

        self.relative_card_address = 0x00
        self.voltage_range = {}
        self.voltage_range[20] = False
        self.voltage_range[21] = False
        self.voltage_range[22] = False
        self.voltage_range[23] = False
        self.voltage_range[24] = False
        self.voltage_range[25] = False
        self.voltage_range[26] = False
        self.voltage_range[27] = False
        self.voltage_range[28] = False
        self.voltage_range[29] = False
        self.voltage_range[30] = False
        self.voltage_range[31] = False
        self.voltage_range[32] = False
        self.voltage_range[33] = False
        self.voltage_range[34] = False
        self.voltage_range[35] = False

        self.card_voltage_range = {}
        self.card_voltage_range[20] = False
        self.card_voltage_range[21] = False
        self.card_voltage_range[22] = False
        self.card_voltage_range[23] = False
        self.card_voltage_range[24] = False
        self.card_voltage_range[25] = False
        self.card_voltage_range[26] = False
        self.card_voltage_range[27] = False
        self.card_voltage_range[28] = False
        self.card_voltage_range[29] = False
        self.card_voltage_range[30] = False
        self.card_voltage_range[31] = False
        self.card_voltage_range[32] = False
        self.card_voltage_range[33] = False
        self.card_voltage_range[34] = False
        self.card_voltage_range[35] = False

        self.set_voltage_range(2.0, 3.6)
        self.relative_card_address = 0x00
        self.inactive = False
        self.register_interrupt_callback(self._callback)

#Low Level Functions
    def set_control(self, control):
        self.write_register(CONTROL, control)

    def enable_sd_host(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_ENABLE_SD, enable)

    def enable_crc(self, enable):
        self.write_register_bit(SD_CONFIGURE, CONFIGURE_EN_CRC, enable)

    def is_crc_enabled(self):
        return self.is_register_bit_set(SD_CONFIGURE, CONFIGURE_EN_CRC)

    def get_control(self):
        return self.read_register(CONTROL)

    def enable_control_0_bit(self, enable):
        self.enable_register_bit(CONTROL, ZERO_BIT, enable)

    def is_control_0_bit_set(self):
        return self.is_register_bit_set(CONTROL, ZERO_BIT)

    def send_command(self, cmd, cmd_arg = 0x00, long_rsp = False, timeout = 0.2):
        #Generate a command bit command
        cmd_reg = 0

        if (long_rsp):
            cmd_reg |= (1 << COMMAND_BIT_RSP_LONG_FLG)

        cmd_reg |= (1 << COMMAND_BIT_GO)
        cmd_reg |= cmd
        #print "cmd reg: 0x%08X" % cmd_reg

        self.write_register(SD_ARGUMENT, cmd_arg)
        self.write_register(SD_COMMAND, cmd_reg)
        to = time.time() + timeout
        while (time.time() < to) and self.is_sd_busy():
            if self.debug: print ".",
        if self.debug: print ""
        if self.is_sd_busy():
            if self.debug: print "Cancel command"
            cmd_reg &= (1 << COMMAND_BIT_GO)
            self.write_register(SD_COMMAND, cmd_reg)
            raise SDHostException("Timeout when sending command: 0x%02X" % cmd)

        response_index = RESPONSE_DICT[cmd]
        if response_index is None:
            return
        resp = self.read_response_list()
        self.parse_response(response_index, resp)

    def get_status(self):
        return self.read_register(STATUS)

    def is_sd_busy(self):
        return self.is_register_bit_set(STATUS, STATUS_SD_BUSY)

    def is_sd_data_busy(self):
        return self.is_register_bit_set(STATUS, STATUS_SD_DATA_BUSY)

    def select_sd_function(self, function_id):
        self.write_register_bit_range(CONTROL, CONTROL_FUNCTION_ADDRESS_HIGH, CONTROL_FUNCTION_ADDRESS_LOW, function_id)

    def cancel_command(self):
        cmd_reg = self.read_register(SD_COMMAND)
        cmd_reg &= (1 << COMMAND_BIT_GO)
        self.write_register(SD_COMMAND, cmd_reg)
#Responses
    def read_response_list(self):
        resp = [0, 0, 0, 0, 0]
        resp[0] = self.read_register(SD_RESPONSE0)
        resp[1] = self.read_register(SD_RESPONSE1)
        resp[2] = self.read_register(SD_RESPONSE2)
        resp[3] = self.read_register(SD_RESPONSE3)
        return resp

    def read_response(self):
        rsps_list = self.read_response_list()
        #response = long(rsps_list[0])
        #response = (response << 8) | rsps_list[1]
        #response = (response << 8) | rsps_list[2]
        #response = (response << 8) | rsps_list[3]
        response = rsps_list[3]
        return response

    def parse_response(self, response_index, response):
        self.debug = True
        self.error_crc = 0
        self.error_out_of_range = 0
        if response_index == 1:
            self.parse_r1_resp(response)
        elif response_index == 2:
            raise SDHostException("R2 Response is not finished")
        elif response_index == 3:
            raise SDHostException("R3 Response is not finished")
        elif response_index == 4:
            self.parse_r4_resp(response)
        elif response_index == 5:
            self.parse_r5_resp(response)
        elif response_index == 6:
            self.parse_r6_resp(response)
        elif response_index == 7:
            self.parse_r7_resp(response)

    def parse_r1_resp(self, response):
        self.error_crc          =   ((response[3] & 1 << R1_COM_CRC_ERROR) > 0     )
        self.error_out_of_range =   ((response[3] & 1 << R1_OUT_OF_RANGE) > 0      )
        self.error_illegal_cmd  =   ((response[3] & 1 << R1_ILLEGAL_COMMAND) > 0   )
        self.error_unknown      =   ((response[3] & 1 << R1_ERROR) > 0             )
        self.current_state      =   ((response[3] >> R1_CURRENT_STATE) & R1_CURRENT_STATE_BITMASK)
        if self.debug: print "CRC Error: %s" % str(self.error_crc)
        if self.debug: print "Out of range Error: %s" % str(self.error_out_of_range)
        if self.debug: print "Illegal Command: %s" % str(self.error_illegal_cmd)
        if self.debug: print "Unknown Error %s" % str(self.error_unknown)
        if self.debug: print "Current State: %d" % self.current_state

    def parse_r4_resp(self, response):
        self.card_ready         =   ((response[3] & (1 << (R4_READY))) > 0)
        self.num_funcs          =   ((response[3] >>(R4_NUM_FUNCS)) & R4_NUM_FUNCS_BITMASK)
        self.v1p8_mode          =   ((response[3] & (1 << (R4_S18A) )) > 0)
        self.memory_present     =   ((response[3] & (1 << (R4_MEM_PRESENT))) > 0)
        vmin = 20
        vmax = 35
        pos = 8
        for i in range (vmin, vmax, 1):
            self.card_voltage_range[i] = ((response[3] & (1 << R4_IO_OCR + pos)) > 0)
            pos += 1

        #print "card ready: %s" % str(self.card_ready)
        #print "memory present: %s" % str(self.memory_present)
        #print "num funcs: %d" % self.num_funcs
        #print "1.8V Mode: %s" % self.v1p8_mode
        #print "IO Range:"
        #for i in range (vmin, vmax, 1):
        #    print "\t%d: %s" % (i, self.card_voltage_range[i])

    def parse_r5_resp(self, response):
        self.error_crc          =   ((response[3] & 1 << R5_COM_CRC_ERROR) > 0)
        self.error_illegal_cmd  =   ((response[3] & 1 << R5_ILLEGAL_COMMAND) > 0)
        self.current_state      =   ((response[3] >> R5_CURRENT_STATE) & R5_CURRENT_STATE_BITMASK)
        self.error_unknown      =   ((response[3] & 1 << R5_ERROR) > 0)
        self.error_function     =   ((response[3] & 1 << R5_ERROR_FUNC) > 0)
        self.error_out_of_range =   ((response[3] & 1 << R5_ERROR_OUT_OF_RANGE) > 0)
        self.read_data_byte     =   (response[3] & DATA_MASK)

    def parse_r6_resp(self, response):
        self.relative_card_address = ((response[3] >> R6_REL_ADDR) & R6_REL_ADDR_BITMASK)
        self.error_crc = (response[3] & (1 << R6_STS_CRC_COMM_ERR) > 0)
        self.error_illegal_cmd = (response[3] & (1 << R6_STS_ILLEGAL_CMD) > 0)
        self.error_unknown = (response[3] & (1 << R6_STS_ERROR) > 0)
        #print "Relative Address: 0x%04X" % self.relative_card_address
        #print "CRC Error: %s" % str(self.error_crc)
        #print "Illegal Command: %s" % str(self.error_illegal_cmd)
        #print "Unknown Error %s" % str(self.error_unknown)

    def parse_r7_resp(self, response):
        pass

    def set_voltage_range(self, vmin = 2.0, vmax = 3.6):
        #print "Voltage Range: %f - %f" % (vmin, vmax)
        if vmin >= vmax:
            raise SDHostException("Vmin is greater than Vmax")

        for key in self.voltage_range.keys():
            self.voltage_range[key] = False

        vmin = int(vmin * 10)
        vmax = int(vmax * 10)
        #print "Voltage Range: %d - %d" % (vmin, vmax)

        vmin_range = 20
        vmax_range = 35
        fval = vmin_range
        while (fval < vmax_range + 1):
            #print "fval: %d" % fval
            if fval >= vmax:
                #print "\tDone!"
                break
            if fval < vmin:
                #print "vmin < fval: %d < %d" % (vmin, fval)
                fval = fval + 1
                continue

            self.voltage_range[fval] = True
            fval += 1

        #print "dict: %s" % str(self.voltage_range)
        #print "voltage:"
        vmin_range = 20
        vmax_range = 35
        fval = vmin_range
        while (fval < vmax_range + 1):
            #print "\t%d: %s" % (fval, self.voltage_range[fval])
            fval += 1

# Commands
    def cmd_phy_sel(self, spi_mode = False):
        try:
            self.send_command(CMD_PHY_MODE)
        except SDHostException:
            print "No Response"
            return
            pass

    def cmd_io_send_op_cond(self, enable_1p8v):
        command_arg = 0x00
        if enable_1p8v:
            command_arg |=  1 << OP_COND_BIT_EN_1P8V
        pos = OP_COND_BIT_OCR_LOW
        for i in range (20, 36, 1):
            if (self.voltage_range[i]):
                command_arg |= 1 << pos
            pos += 1

        self.send_command(CMD_OP_COND, command_arg)

    def cmd_get_relative_card_address(self):
        command_arg = 0x00

        self.send_command(CMD_SEND_RELATIVE_ADDR)

    def cmd_enable_card(self, select_enable):
        if self.relative_card_address == 0:
            print "Card Select/Deslect is not configured yet!"
            print "Calling card config to get an address"
            self.cmd_get_relative_card_address()
        command_arg = 0x00
        if select_enable:
            command_arg |= self.relative_card_address << R6_REL_ADDR

        try:
            self.send_command(CMD_SEL_DESEL_CARD, command_arg)
        except SDHostException:
            return

    def cmd_go_inactive_state(self):
        try:
            self.send_command(CMD_GO_INACTIVE)
        except SDHostException:
            pass

        self.inactive = True
        print "Inactive State, reset to continue"

    def write_config_byte(self, address, data, read_after_write = False):
        data = [data]
        return self.write_sd_data(function_id = 0,
                              address = address,
                              data = data,
                              read_after_write = read_after_write)

    def read_config_byte(self, address):
        return self.read_sd_data(function_id = 0,
                                address = address)

    def write_sd_data(self, function_id, address, data, fifo_mode = False, read_after_write = False):
        if len(data) == 1:
            #This seems overly complicated but I chose to add this to exercise the SDIO Device Core
            return self.rw_byte(True, function_id, address, data[0], read_after_write)

        self.block_size = self.get_block_size(function_id)

        if  self.block_size == 0 or               \
            ( len(data) <= self.block_size and    \
              len(data) <= 512):

            #Block mode
            #print "Go to write multiple bytes"
            return self.rw_multiple_bytes(True, function_id, address, data, fifo_mode)

        return self.rw_block(True, function_id, address, data, byte_count = 0, fifo_mode = fifo_mode)

    def set_block_size(self, func_num, block_size):
        self.write_register(SD_BLOCK_SIZE_OFFSET + func_num, block_size)

    def get_block_size(self, func_num):
        return self.read_register(SD_BLOCK_SIZE_OFFSET + func_num)

    def read_sd_data(self, function_id, address, byte_count = 1, fifo_mode = False):
        if byte_count == 1:
            return self.rw_byte(False, function_id, address, [0], False)

        self.block_size = self.get_block_size(function_id)


        if (self.block_size == 0) or (byte_count < self.block_size):
            return self.rw_multiple_bytes(write_flag = False,
                                          function_id = function_id,
                                          address = address,
                                          data = [0],
                                          byte_count = byte_count,
                                          fifo_mode = fifo_mode)

        return self.rw_block(write_flag = False,
                             function_id = function_id,
                             address = address,
                             data = [],
                             byte_count = byte_count,
                             fifo_mode = fifo_mode)

    def rw_byte(self, write_flag, function_id, address, data, read_after_write):
        command_arg = 0
        if write_flag:
            command_arg |= (1 << DATA_WRITE_FLAG)
            command_arg |= (data & DATA_MASK)
        command_arg |= ((function_id & DATA_FUNC_BITMASK) << DATA_FUNC_INDEX)
        command_arg |= ((address & DATA_ADDR_BITMASK) << DATA_ADDR)
        self.send_command(CMD_SINGLE_DATA_RW, command_arg)
        return self.read_data_byte

    def rw_multiple_bytes(self, write_flag, function_id, address, data, fifo_mode, byte_count = 1, timeout = 0.2):
        command_arg = 0
        command_arg |= ((function_id & DATA_FUNC_BITMASK) << DATA_FUNC_INDEX)
        command_arg |= ((address & DATA_ADDR_BITMASK) << DATA_ADDR)

        if not fifo_mode:
            #print "Increment Address!"
            command_arg |= (1 << DATA_RW_OP_CODE)

        if write_flag:
            self.dma_writer.set_size(512)
            command_arg |= (1 << DATA_WRITE_FLAG)
            command_arg |= (len(data) & DATA_RW_COUNT_BITMODE)

            self.send_command(CMD_DATA_RW, command_arg)

            #print "Initiate Data Transfer (Outbound)"
            self.write_memory(self.MEM_BASE_0, data)
            self.set_register_bit(CONTROL, CONTROL_DATA_WRITE_FLAG)
            self.set_register_bit(CONTROL, CONTROL_ENABLE_DMA_WR)
            #Initiate transfer from memory to FIFO
            self.write_register(REG_MEM_0_SIZE, len(data) / 4)
            self.write_register(SD_DATA_BYTE_COUNT, len(data))
            #time.sleep(0.1)
            self.set_register_bit(CONTROL, CONTROL_DATA_BIT_ACTIVATE)
            to = time.time() + timeout
            while (time.time() < to) and self.is_sd_busy():
                if self.debug: print ".",
                time.sleep(0.001)
            if self.debug: print ""
            #Disable the DMA Write Flag
            #print "Waiting till data has finished sending..."
            to = time.time() + timeout
            while (time.time() < to) and (self.dma_writer.get_available_memory_blocks() != 3):
                print "This should change to an asynchrounous Wait"
                time.sleep(0.01)

            self.clear_register_bit(CONTROL, CONTROL_ENABLE_DMA_WR)

        else:
            if self.debug: print "Initiate Data Transfer (Inbound)"
            self.dma_reader.set_size(512)
            #print "byte count: %s" % byte_count
            command_arg |= (byte_count & DATA_RW_COUNT_BITMODE)

            self.clear_register_bit(CONTROL, CONTROL_DATA_WRITE_FLAG)
            self.set_register_bit(CONTROL, CONTROL_ENABLE_DMA_RD)
            self.write_register(SD_DATA_BYTE_COUNT, byte_count)
            self.write_register(REG_MEM_0_SIZE, byte_count / 4)

            self.set_register_bit(CONTROL, CONTROL_DATA_BIT_ACTIVATE)

            self.send_command(CMD_DATA_RW, command_arg)
            word_count = byte_count / 4
            if word_count == 0:
                word_count = 1

            #Disable the DMA Write Flag
            self.clear_register_bit(CONTROL, CONTROL_ENABLE_DMA_RD)
            self.set_register_bit(CONTROL, CONTROL_DATA_WRITE_FLAG)
            return self.read_memory(self.MEM_BASE_0, byte_count / 4)

    def set_function_block_size(self, func_num, block_size):
        '''
        Sets the read/write block size for the specified function.
        When user performs a read/write command with the block mode set to true
        Then this value must be set. The value can be anything between 1 - 2048

        Users must not use block mode without setting this value!

        Args:
            func_num (Integer): Function between 0 - 7
            block_size (Integer): Size of block to read/write

        Returns:
            Nothing

        Raises:
            SDHostException:
                Value besides 1 - 2048 was given
        '''
        if func_num < 0:
            raise SDHostException("Only function number between 0 and 7 allowed: %d not valid" % func_num)

        if func_num > 7:
            raise SDHostException("Only function number between 0 and 7 allowed: %d not valid" % func_num)

        if block_size > 2048:
            raise SDHostException("Only values between 1 - 2048 allowed: %d not valid" % block_size)

        if block_size < 1:
            raise SDHostException("Only values between 1 - 2048 allowed: %d not valid" % block_size)

        self.block_size = block_size

        address = 0x100 * func_num + 0x10

        lower_byte = block_size & 0xFF
        upper_byte = ((block_size >> 8) & 0xFF)
        self.write_config_byte(address, lower_byte)
        self.write_config_byte(address + 1, upper_byte)
        print "Function Number: %d" % func_num
        print "address: 0x%04X, Block Size: %d" % (SD_BLOCK_SIZE_OFFSET + func_num, block_size)
        self.write_register(SD_BLOCK_SIZE_OFFSET + func_num, block_size)

    def rw_block(self, write_flag, function_id, address, data, byte_count, fifo_mode, timeout = 0.2):
        if self.debug: print "RW Block: Writing: %s" % str(write_flag)
        self.byte_count = byte_count
        command_arg = 0
        command_arg |= ((function_id & DATA_FUNC_BITMASK) << DATA_FUNC_INDEX)
        command_arg |= ((address & DATA_ADDR_BITMASK) << DATA_ADDR)

        #Set Block Transfer Mode
        command_arg |= (1 << DATA_RW_BLOCK_MODE)

        if not fifo_mode:
            if self.debug: print "Increment Address!"
            command_arg |= (1 << DATA_RW_OP_CODE)

        self.block_size = self.get_block_size(function_id)

        if write_flag:
            #Setup the DMA Read or Write Block Size
            command_arg |= ((len(data) / self.block_size) & DATA_RW_COUNT_BITMODE)
            self.dma_writer.set_size(self.block_size)
            command_arg |= (1 << DATA_WRITE_FLAG)
            self.set_register_bit(CONTROL, CONTROL_DATA_WRITE_FLAG)
            self.send_command(CMD_DATA_RW, command_arg)
            if self.debug: print "Initiate Data Transfer (Outbound)"
            #XXX: All these transactions with the control register can be consolodated to one function call
            self.set_register_bit(CONTROL, CONTROL_ENABLE_DMA_WR)
            self.write_register(SD_DATA_BYTE_COUNT, (len(data) / self.block_size))
            self.set_register_bit(CONTROL, CONTROL_DATA_BLOCK_MODE)
            self.set_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT)
            self.select_sd_function(function_id)
            self.set_register_bit(CONTROL, CONTROL_DATA_BIT_ACTIVATE)

            self.dma_writer.write(data)

            to = time.time() + timeout
            #while (time.time() < to) and (self.dma_writer.get_available_memory_blocks() != 3):
            while (time.time() < to) and (self.is_sd_data_busy()):
                print "This should change to an asynchrounous Wait"
                time.sleep(0.01)

            self.clear_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT)
            self.clear_register_bit(CONTROL, CONTROL_DATA_BIT_ACTIVATE)
            self.clear_register_bit(CONTROL, CONTROL_DATA_BLOCK_MODE)
            self.clear_register_bit(CONTROL, CONTROL_ENABLE_DMA_WR)

        else:
            command_arg |= (byte_count / self.block_size) & DATA_RW_COUNT_BITMODE
            self.clear_register_bit(CONTROL, CONTROL_DATA_WRITE_FLAG)
            self.dma_reader.set_size(self.block_size / 4)
            self.set_register_bit(CONTROL, CONTROL_ENABLE_DMA_RD)
            self.write_register(SD_DATA_BYTE_COUNT, byte_count / self.block_size)
            self.set_register_bit(CONTROL, CONTROL_DATA_BLOCK_MODE)
            self.set_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT)
            self.select_sd_function(function_id)
            self.set_register_bit(CONTROL, CONTROL_DATA_BIT_ACTIVATE)

            if self.debug: print "Sending Command..."
            try:
                self.send_command(CMD_DATA_RW, command_arg)
            except SDHostException as e:
                print "Exception: %s" % str(e)
                return
            if self.debug: print "Command Sent"
            self.block_timeout = time.time() + timeout

            self.dma_reader.debug = True
            if self.is_asynchronous_read_mode():
                if self.debug: print "ASYNCHRONOUS MODE!"
                self.read_data = Array('B')
                #Go to asynchronous Read mode
                self.dma_reader.enable_asynchronous_read(self._read_async_data)
                return

            else:
                #Synchronous Read Mode
                self.read_data = Array('B')
                self.dma_reader.debug = True
                if self.debug: print "Byte Count: %d" % byte_count
                while len(self.read_data) < byte_count:
                    if self.debug: print "Length Read Data: %d" % len(self.read_data)
                    self.read_data += self.dma_reader.read()
                if self.debug: print "Length Read Data: %d" % len(self.read_data)
                self.dma_reader.debug = False

                self.clear_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT)
                self.clear_register_bit(CONTROL, CONTROL_DATA_BIT_ACTIVATE)
                self.clear_register_bit(CONTROL, CONTROL_DATA_BLOCK_MODE)
                self.clear_register_bit(CONTROL, CONTROL_ENABLE_DMA_RD)
                return self.read_data

    def send_single_byte(self, function_id, address, data, read_after_write):
        command_arg = 0
        write_flag = DATA_WRITE_FLAG
        cmd = CMD_SINGLE_DATA_RW

    def set_data_bus_dir_output(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_DATA_WRITE_FLAG, enable)

    def is_read_wait_supported(self):
        return ((self.read_config_byte(CONFIGURE_READ_WAIT_SPRT_ADDR) & CONFIGURE_READ_WAIT_SPRT_BIT) > 0)

    def is_asynchronous_read_mode(self):
        return self.async_read_mode

    def enable_async_dma_reader(self, enable):
        self.async_read_mode = enable

    def set_async_dma_reader_callback(self, callback):
        self.async_read_callback = callback

    def _callback(self):
        if self.is_asynchronous_read_mode():
            #No Interrupt during block read
            return
        if self.interrupt_callback is not None:
            self.interrupt_callback()

    def _read_async_data(self):
        #self.read_data += self.dma_reader.async_read()
        self.read_data += self.dma_reader._dangerous_async_read()
        #print "Async Callback...: Read Data: %s" % self.read_data
        if len(self.read_data) >= self.byte_count:
            #print "DONE!"
            self.dma_reader.disable_asynchronous_read()
            self.async_read_callback(self.read_data)
            self.clear_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT)
            self.clear_register_bit(CONTROL, CONTROL_DATA_BIT_ACTIVATE)
            self.clear_register_bit(CONTROL, CONTROL_DATA_BLOCK_MODE)
            self.clear_register_bit(CONTROL, CONTROL_ENABLE_DMA_RD)
            self.read_register(STATUS)

    def read_async_data(self):
        return self.read_data

    def enable_function(self, function_id):
        data = 0
        data = self.read_config_byte(IO_FUNC_ENABLE_ADDR)
        if function_id:
            data |= 1 << function_id
        else:
            data &= ~(1 << function_id)

        self.write_config_byte(IO_FUNC_ENABLE_ADDR, data)

    def set_interrupt_callback(self, callback):
        self.interrupt_callback = callback

    def clear_interrupt_callback(self):
        if self.debug: print "Interrupt callback!"
        self.interrupt_callback = None

    def enable_function_interrupt(self, function_id):
        data = 0
        data = self.read_config_byte(INT_ENABLE_ADDR)
        if function_id:
            data |= 1 << function_id
        else:
            data &= ~(1 << function_id)
        self.write_config_byte(INT_ENABLE_ADDR, data)

    def is_interrupt_pending(self, function_id):
        return ((self.read_config_byte(INT_PENDING_ADDR) & (1 << function_id)) > 0)

    def get_interrupt_pending(self):
        return self.read_config_byte(INT_PENDING_ADDR)

    def enable_interrupt(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT, enable)

    def is_interrupt_enabled(self):
        return self.is_register_bit_set(CONTROL, CONTROL_ENABLE_ITNERRUPT)

    def set_input_delay(self, delay):
        delay = delay % 256
        self.write_register(SD_DELAY_VALUE, delay)

    def get_input_delay(self):
        return self.read_register(SD_DELAY_VALUE)

    def get_gen_crc(self):
        return self.read_register(SD_DBG_CRC_GEN)
        
    def get_rmt_crc(self):
        return self.read_register(SD_DBG_CRC_RMT)
 
    def display_crcs(self):
        gen_crc = self.get_gen_crc()
        rmt_crc = self.get_rmt_crc()
        if gen_crc != rmt_crc:
            print "%sCRC Gen:0x%02X != Rmt:0x%02X %s" % (red, gen_crc, rmt_crc, white)
        else:
            print "%sCRC Gen:0x%02X == Rmt:0x%02X %s" % (green, gen_crc, rmt_crc, white)

    def display_control(self):
        control = self.get_control()
        print green,
        print "SD Host Control:"
        if (control & (1 << CONTROL_ENABLE_SD) > 0):
            print "\tSD Host Enabled"
        if (control & (1 << CONTROL_ENABLE_INTERRUPT) > 0):
            print "\tSD Host Enable Interrupts"
        if (control & (1 << CONTROL_ENABLE_DMA_WR) > 0):
            print "\tSD Host Enable DMA Write"
        if (control & (1 << CONTROL_ENABLE_DMA_RD) > 0):
            print "\tSD Host Enable DMA Read"
        if (control & (1 << CONTROL_ENABLE_SD_FIN_INT) > 0):
            print "\tSD Host Enable Interrupt on Finish"
        if (control & (1 << CONTROL_DATA_WRITE_FLAG) > 0):
            print "\tSD Host Data Write Flag"
        if (control & (1 << CONTROL_DATA_BLOCK_MODE) > 0):
            print "\tSD Host Data Block Mode"

        faddr = control >> CONTROL_FUNCTION_ADDRESS_LOW
        faddr &= (CONTROL_FUNCTION_ADDRESS_HIGH - CONTROL_FUNCTION_ADDRESS_LOW) + 1

        print "\tSD Host Function Address: 0x%02X %s" % (faddr, white)

    def display_status(self):
        status = self.get_status()
        print blue,
        print "SD Host Status:"
        if (status & (1 << STATUS_ENABLE) > 0):
            print "\tSD Host Enabled"
        if (status & (1 << STATUS_SD_READY) > 0):
            print "\tSD Host SD Ready"
        if (status & (1 << STATUS_SD_DATA_BUSY) > 0):
            print "\tSD Host Data Transaction In Progress"
        if (status & (1 << STATUS_MEMORY_0_FINISHED) > 0):
            print "\tSD Host Memory 0 Finished"
        if (status & (1 << STATUS_MEMORY_1_FINISHED) > 0):
            print "\tSD Host Memory 1 Finished"
        if (status & (1 << STATUS_MEMORY_0_EMPTY) > 0):
            print "\tSD Host Memory 0 Empty"
        if (status & (1 << STATUS_MEMORY_1_EMPTY) > 0):
            print "\tSD Host Memory 1 Empty"

        sts_error = status >> STATUS_ERROR_BIT_BOT
        sts_error &= (STATUS_ERROR_BIT_TOP - STATUS_ERROR_BIT_BOT) + 1
        print "\tSD Host Error Code: 0x%02X %s" % (sts_error, white)



