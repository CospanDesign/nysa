import sys
import os
import time
from array import array as Array
from nysa.host.driver.utils import *
from collections import OrderedDict

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from nysa.host.driver import driver

DEVICE_TYPE                     = "Logic Analyzer"
SDB_ABI_VERSION_MINOR           = 1
SDB_VENDOR_ID                   = 0x800000000000C594

CONTROL_RESET                   = 0
CONTROL_ENABLE_INTERRUPT        = 1
CONTROL_ENABLE_LA               = 2
CONTROL_RESTART_LA              = 3
CONTROL_FORCE_STB               = 4
CONTROL_ENABLE_UART             = 5

STATUS_FINISHED                 = 0



#Addresses
CONTROL         = 0x00
STATUS          = 0x01
TRIGGER         = 0x02
TRIGGER_MASK    = 0x03
TRIGGER_AFTER   = 0x04
TRIGGER_EDGE    = 0x05
BOTH_EDGES      = 0x06
REPEAT_COUNT    = 0x07
DATA_COUNT      = 0x08
START_POS       = 0x09
CLOCK_RATE      = 0x0A
READ_DATA       = 0x0B



class LogicAnalyzerException(Exception):
    pass

class LogicAnalyzer(driver.Driver):
    """ wb_logic_analyser

        Communication with a logic analyzer
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
        super(LogicAnalyzer, self).__init__(nysa, urn, debug)
        #Perform this strange read write so that we can disable the UART
        # Controller
        control = self.read_register(CONTROL)
        #print "control: 0x%08X" % control
        self.data_count = self.get_data_count()
        #print "Count: 0x%08X" % self.data_count
        self.enable_uart_control(False)

    def reset(self):
        self.set_register_bit(CONTROL, CONTROL_RESET)

    def enable_interrupts(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT, enable)

    def enable_uart_control(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_ENABLE_UART, enable)

    def is_uart_enabled(self):
        return self.is_register_bit_set(CONTROL, CONTROL_ENABLE_UART)

    def is_interrupts_enabled(self):
        return self.is_register_bit_set(CONTROL, CONTROL_ENABLE_INTERRUPT)

    def enable(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_ENABLE_LA, enable)

    def is_enabled(self):
        return self.is_register_bit_set(CONTROL, CONTROL_ENABLE_LA)

    def restart(self):
        self.set_register_bit(CONTROL, CONTROL_RESTART_LA)

    def is_finished(self):
        return self.is_register_bit_set(STATUS, STATUS_FINISHED)

    def force_trigger(self):
        self.enable_register_bit(CONTROL, CONTROL_FORCE_STB, True)

    def set_trigger(self, trigger):
        self.write_register(TRIGGER, trigger)

    def get_trigger(self):
        return self.read_register(TRIGGER)

    def set_trigger_mask(self, trigger_mask):
        self.write_register(TRIGGER_MASK, trigger_mask)

    def get_trigger_mask(self):
        return self.read_register(TRIGGER_MASK)

    def set_trigger_after(self, trigger_after):
        self.write_register(TRIGGER_AFTER, trigger_after)

    def get_trigger_after(self):
        return self.read_register(TRIGGER_AFTER)

    def set_trigger_edge(self, trigger_edge):
        self.write_register(TRIGGER_EDGE, trigger_edge)

    def get_trigger_edge(self):
        return self.read_register(TRIGGER_EDGE)

    def set_both_edge(self, both_edges):
        self.write_register(BOTH_EDGES, both_edges)

    def get_both_edge(self):
        return self.read_register(BOTH_EDGES)

    def set_repeat_count(self, repeat_count):
        self.write_register(REPEAT_COUNT, repeat_count)

    def get_repeat_count(self):
        return self.read_register(REPEAT_COUNT)

    def get_data_count(self):
        return self.read_register(DATA_COUNT)

    def get_start_pos(self):
        return self.read_register(START_POS)

    def read_raw_data(self):
        return self.read(READ_DATA, self.data_count, disable_auto_inc = True)

    def read_data(self):
        start_pos = self.read_register(START_POS)
        raw_data = self.read(READ_DATA, self.data_count, disable_auto_inc = True)
        #Need to reorder the data so it makes sense for the user
        temp = Array('L')
        for i in range (0, len(raw_data), 4):
            temp.append(array_to_dword(raw_data[i: i + 4]))

        '''
        for i in range (0, len(temp), 1):
            print "\t[%04X] 0x%08X" % (i, temp[i])
        '''

        print "Start Pos: 0x%04X" % start_pos

        #Change data to 32-bit array
        data = Array('L')
        if start_pos  == 0:
            data = temp

        data.extend(temp[start_pos:])
        data.extend(temp[0:start_pos])
        return data

    def get_clock_rate(self):
        return self.read_register(CLOCK_RATE)

def set_vcd_header():
    #set date
    buf = ""
    buf += "$date\n"
    buf += time.strftime("%b %d, %Y %H:%M:%S") + "\n"
    buf += "$end\n"
    buf += "\n"

    #set version
    buf += "$version\n"
    buf += "\tNysa Logic Analyzer V0.1\n"
    buf += "$end\n"
    buf += "\n"

    #set the timescale
    buf += "$timescale\n"
    buf += "\t1 ns\n"
    buf += "$end\n"
    buf += "\n"

    return buf

def set_signal_names(signal_dict, add_clock):
    buf = ""

    #set the scope
    buf += "$scope\n"
    buf += "$module logic_analyzer\n"
    buf += "$end\n"
    buf += "\n"

    offset = 0
    char_offset = 33
    if add_clock:
        character_alias = char_offset
        buf += "$var wire 1 %c clk $end\n" % (character_alias)
        char_offset = 34

    offset = 0
    for name in signal_dict:
        character_alias = char_offset + offset
        buf += "$var wire %d %c %s $end\n" % (signal_dict[name], character_alias, name)
        offset += 1

    #Pop of the scope stack
    buf += "\n"
    buf += "$upscope\n"
    buf += "$end\n"
    buf += "\n"

    #End the signal name defnitions
    buf += "$enddefinitions\n"
    buf += "$end\n"
    return buf

def set_waveforms(data, signal_dict, add_clock, cycles_per_clock, debug = False):
    buf = ""
    buf += "#0\n"
    buf += "$dumpvars\n"
    timeval = 0

    if debug: print "Cycles per clock: %d" % cycles_per_clock

    index_offset = 33
    clock_character = 33
    if add_clock:
        index_offset = 34

    #Time 0
    #Add in the initial Clock Edge
    if add_clock:
        buf += "%d%c\n" % (0, clock_character)

    for i in range(len(signal_dict)):
        buf += "x%c\n" % (index_offset + i)

    #Time 1/2 clock cycle
    if add_clock:
        buf += "#%d\n" % (cycles_per_clock / 2)
        buf += "%d%c\n" % (0, clock_character)

    if add_clock:
        buf += "#%d\n" % ((i + 1) * cycles_per_clock)
        buf += "%d%c\n" % (1, clock_character)


    for j in range (len(signal_dict)):
        buf += "%d%c\n" % (((data[0] >> j) & 0x01), (index_offset + j))

    #Time 1/2 clock cycle
    if add_clock:
        buf += "#%d\n" % (cycles_per_clock / 2)
        buf += "%d%c\n" % (0, clock_character)



    #Go through all the values for every time instance and look for changes
    if debug: print "Data Length: %d" % len(data)
    for i in range(1, len(data)):

        if add_clock:
            buf += "#%d\n" % ((i + 1) * cycles_per_clock)
            buf += "%d%c\n" % (1, clock_character)

        #Read up to the second to the last peice of data
        if data[i - 1] != data[i]:
            if not add_clock:
                buf += "#%d\n" % ((i + 1) * cycles_per_clock)
            for j in range (len(signal_dict)):
                if ((data[i - 1] >> j) & 0x01) != ((data[i] >> j) & 0x01):
                    buf += "%d%c\n" % (((data[i] >> j) & 0x01), (index_offset + j))

        if add_clock:
            buf += "#%d\n" % (((i + 1) * cycles_per_clock) + (cycles_per_clock / 2))
            buf += "%d%c\n" % (0, clock_character)


    buf += "#%d\n" % (len(data) * cycles_per_clock)
    for i in range(len(signal_dict)):
        buf += "%d%c\n" % (((data[-1] >> i) & 0x01), (33 + i))
    return buf

def create_vcd_buffer(data, signal_dict = OrderedDict(), count = 32, clock_count = 100, add_clock = True, debug = False):
    if debug: print "Create a VCD file"
    print "clock count: %d" % clock_count
    ghertz_freq = 1000000000
    if clock_count == 0:
        clock_count = 100000000
    cycles_per_clock = int(ghertz_freq / clock_count)
    if debug: print "Clocks per cycle: %d" % cycles_per_clock

    if len(signal_dict) < count:
        for i in range(count):
            signal_dict["signal%d" % i] = 1

    buf = ""
    buf += set_vcd_header()
    buf += set_signal_names(signal_dict, add_clock)
    buf += set_waveforms(data, signal_dict, add_clock, cycles_per_clock, debug)
    return buf


