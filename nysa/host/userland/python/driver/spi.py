#Distributed under the MIT licesnse.
#Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

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

""" SPI

Facilitates communication with the SPI core independent of communication
medium

For more details see:

http://wiki.cospandesign.com/index.php?title=Wb_spi

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time

from array import array as Array


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

import nysa
from nysa import Nysa
from nysa import NysaCommError


from driver import Driver

COSPAN_DESIGN_SPI_MODULE = 0x01

#Register Constants
CONTROL             = 0
CLOCK_RATE          = 1
CLOCK_DIVIDER       = 2
SLAVE_SELECT        = 3
READ_DATA0          = 4
READ_DATA1          = 5
READ_DATA2          = 6
READ_DATA3          = 7
WRITE_DATA0         = 8
WRITE_DATA1         = 9
WRITE_DATA2         = 10
WRITE_DATA3         = 11

#Control/Status bit values
CONTROL_CHARACTER_LENGTH  = 0
CONTROL_GO_BUSY           = 8
CONTROL_RX_NEGATIVE       = 9
CONTROL_TX_NEGATIVE       = 10
CONTROL_LSB_ENABLE        = 11
CONTROL_INTERRUPT_ENABLE  = 12
CONTROL_AUTO_SLAVE_SEL    = 13



class SPIError (Exception):
    """SPI Error:

    Errors associated with SPI
        SPI Bus Busy
        Incorrect Settings
    """
    pass

class SPI(Driver):
    """
    SPI
        Communication with SPI Core
    """

    @staticmethod
    def get_core_id():
        """
        Returns the identification number of the device this module controls

        Args:
            Nothing

        Returns (Integer):
            Number corresponding to the device in the drt.json file

        Raises:
            DRTError: Device ID Not found in drt.json
        """
        return Nysa.get_id_from_name("SPI")

    @staticmethod
    def get_core_sub_id():
        """Returns the identification of the specific implementation of this
        controller

        Example: Cospan Design wrote the HDL GPIO core with sub_id = 0x01
            this module was designed to interface and exploit features that
            are specific to the Cospan Design version of the GPIO controller.

            Some controllers may add extra functionalities that others do not
            sub_ids are used to differentiate them and select the right python
            controller for those HDL modules

        Args:
            Nothing

        Returns (Integer):
            Number ID for the HDL Module that this controls
            (Note: 0 = generic control or baseline funtionality of the module)

        Raises:
            Nothing
        """
        return COSPAN_DESIGN_SPI_MODULE

    def __init__(self, nysa, dev_id, debug = False):
        super(SPI, self).__init__(nysa, dev_id, debug)

    def __del__(self):
        pass

    def get_control(self):
        """get_control
        
        reads the control register
        
        Args:
            Nothing
        
        Return:
            32-bit control register value
        
        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CONTROL)

    def set_control(self, control):
        """set_control
  
        write the control register
  
        Args:
            control: 32-bit control value
  
        Return:
            Nothing
  
        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(CONTROL, control)

    def get_character_length(self):
        """get_character_length
       
       
        gets the length of a character transaction
       
        Args:
          Nothing
       
        Returns:
          32-bit value of the length of the character:
            0x001 = 1
            0x002 = 2
            ...
            0x07F = 127
            0x080 = 128
       
        Raises:
          NysaCommError: Error in communication
        """
        control = self.get_control()
        char_len = control & 0x07F
        if char_len == 0x00:
            char_len == 0x080
        return char_len

    def set_character_length(self, character_length):
        """set_character_length
       
        sets the length of a character transaction
       
        Args:
            Length of a charater transaction
                0x001 = 1
                0x002 = 2
                ...
                0x07F = 127
                0x080 = 128
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        if character_length >= 0x080:
            character_length = 0x00
        control = self.get_control()
        #Clear the previous
        control &= ~0x007F
        control |= character_length
        self.set_control(control)

    def set_tx_polarity(self, positive):
        """set_tx_polarity
       
        sets what clock edge the TX will shift data out
       
        Args:
            positive:
              True = positive edge
              False = negative edge
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        self.enable_register_bit(CONTROL, CONTROL_TX_NEGATIVE, not positive)
 
    def is_tx_polarity_positive(self):
        """is_tx_polarity_positive
       
        returns True if the TX polarity is positive
       
        Args:
            Nothing
       
        Return:
            True: Positive Tx Polarity
            False: Negative TX polarity
       
        Raises:
            NysaCommError: Error in communication
        """
        return not self.is_register_bit_set(CONTROL, CONTROL_TX_NEGATIVE)
 
    def set_rx_polarity(self, positive):
        """set_rx_polarity
       
        sets what clock edge the RX will shift data in
       
        Args:
            positive:
                True = positive edge
                False = negative edge
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        self.enable_register_bit(CONTROL, CONTROL_RX_NEGATIVE, not positive)
 
    def is_rx_polarity_positive(self):
        """is_rx_polarity_positive
       
        returns True if the RX polarity is positive
       
        Args:
            Nothing
       
        Return:
            True: Positive Tx Polarity
            False: Negative RX polarity
       
        Raises:
            NysaCommError: Error in communication
        """
        return not self.is_register_bit_set(CONTROL, CONTROL_RX_NEGATIVE)
 
    def start_transaction(self):
        """start_transaction
       
        starts a spi read/write transaction
       
        Args:
            Nothing
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
            SPIError: SPI core is not ready
        """
        control = self.get_control()
        if (control & CONTROL_GO_BUSY) > 0:
            raise SPIError("SPI Not Ready")

        self.set_register_bit(CONTROL, CONTROL_GO_BUSY)
 
    def is_busy(self):
        """is_busy
       
        returns true if the core is busy with a transaction
       
        Args:
            Nothing
       
        Returns:
            True: Busy
            False: Ready
       
        Raises:
            NysaCommError: Error in communication
        """
        return self.is_register_bit_set(CONTROL, CONTROL_GO_BUSY)
 
    def enable_interrupt(self, enable):
        """enable_interrupt
       
        enables/disables the core to raise interrupts when a transaction is
        complete
       
        Args:
            enable (Boolean):
                True: Enable
                False: Disable
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        self.enable_register_bit(CONTROL, CONTROL_INTERRUPT_ENABLE, enable)
 
    def is_interrupt_enabled(self):
        """is_interrupt_enbled
       
        returns True if the interrupt is enabled
       
        Args:
            Nothing
       
        Returns:
            True: if interrupt is enabled
            False: interrupt is not enabled
       
        Raises:
            NysaCommError: Error in communication
        """
        self.is_register_bit_set(CONTROL, CONTROL_INTERRUPT_ENABLE)
 
    def is_lsb_enabled(self):
        """is_lsb
       
        is the bit order reveresed
            (least significant bit first)
       
        Args:
            Nothing
       
        Return:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        return self.is_register_bit_set(CONTROL, CONTROL_LSB_ENABLE)
 
    def set_lsb_enable(self, enable):
        """set_lsb_enable
       
        set the lsb bit
            (eanble least significant bit first
       
        Args:
            Nothing
       
        Return:
            Nothing
       
        Raises:
            NysaCommError
        """
        self.enable_register_bit(CONTROL, CONTROL_LSB_ENABLE, enable)
 
    def get_clock_rate(self):
        """get_clock_rate
       
        gets the clock rate of the design (this is used in setting the clock divider
       
        Args:
            Nothing
       
        Returns:
            32-bit value indicating the clock_rate of the system
                Example: 100000000 = 100MHz clock
       
        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CLOCK_RATE)
 
    def get_clock_divider(self):
        """get_clock_divider
       
        gets the clock rate of the divider
       
        Args:
            Nothing
       
        Returns:
            32-bit clock divider value
       
        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CLOCK_DIVIDER)
 
    def set_clock_divider(self, clock_divider):
        """set_clock_divider
       
        set the clock divider
       
        Args:
            clock_divider: 32-bit value to write into the register
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(CLOCK_DIVIDER, clock_divider)
 
    def set_spi_clock_rate(self, spi_clock_rate):
        """set_spi_clock_rate
       
        attempts to set the clock rate to the clock value
       
        Args:
            clock_rate: 32-bit value to write into the register
                Ex: 1000000: 1MHz
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        clock_rate = self.get_clock_rate()
        spi_clock_rate = spi_clock_rate * 2
        divider = clock_rate/spi_clock_rate

        if divider == 0:
            divider = 1

        self.set_clock_divider(divider)
 
    def get_spi_clock_rate(self):
        """get_spi_clock_rate
       
        get the clock rate from the system
       
        Args:
            Nothing
       
        Returns:
            Clock Rate
       
        Raises:
            NysaCommError: Error in communication
        """
        clock_rate = self.get_clock_rate()
        divider = self.get_clock_divider()
        if self.debug: print "Divider: %d" % divider
        value = (clock_rate / (divider + 1)) * 2
        return value
 
    def set_auto_ss_control(self, enable):
        """set_auto_ss_select_mode
       
        allow the core to control slave select
       
        Args:
            enable:
                True: enable auto select mode
                False: Manual select mode
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        self.enable_register_bit(CONTROL, CONTROL_AUTO_SLAVE_SEL, enable)
 
    def is_auto_ss(self):
        """is_auto_ss
       
        check if auto ss is set
       
        Args:
            Nothing
       
        Return:
            True: Auto SS is set
            False: Auto SS is not set
       
        Raises:
            NysaCommError
        """
        return self.is_register_bit_set(CONTROL, CONTROL_AUTO_SLAVE_SEL)
 
    def get_slave_select_raw(self):
        """get_slave_select_raw
       
        get the raw slave select value from the register
       
        Args:
            Nothing
       
        Returns:
            32-bit slave select register
       
        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(SLAVE_SELECT)
 
    def set_slave_select_raw(self, slave_select):
        """set_slave_select_raw
       
        sets the slave select register
       
        Args:
            slave_select: 32-bit value to be written to the slave select register
                Ex: 0x00000001: select slave 0
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(SLAVE_SELECT, slave_select)
 
    def set_spi_slave_select(self, slave_bit, enable):
        """set_spi_slave
       
        enable an individual SPI slave
       
        Args:
            slave_bit: a bit value of the slave to enable
                Ex: 0x02 : Enable slave 1
            enable: True or False value that enables/disables the selected slave
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        self.enable_register_bit(SLAVE_SELECT, slave_bit, enable)
 
    def is_spi_slave_selected(self, slave_bit):
        """is_spi_slave_selected
       
        reads the slave select of the specified slave bit
       
        Args:
            slave_bit: a bit value of the slave to check if enabled
       
        Returns:
            True: Selected
            False: Not Selected
       
        Raises:
            NysaCommError: Error in communication
        """
        return self.is_register_bit_set(SLAVE_SELECT, slave_bit)
 
    def get_read_data(self, read_length):
        """get_read_data
       
        get the read data from the SPI core, due to the behavior of SPI the
        user should specify the amount of data to return. generally a SPI
        transaction will consist of writing to a register and then sending out
        bytes until the read value is read in
       
        Args:
            read_length: length of the data in bytes to return
       
        Returns:
            An array of bytes of data
       
        Raises:
            NysaCommError: Error in communication
        """
        char_len = self.get_character_length() / 8
        read_data = self.read(READ_DATA0, 4)
        if self.debug:
            print "Read Data: %s" % str(read_data)
        return read_data
 
    def set_write_data(self, write_data):
        """set_write_data
       
        Sets the write data
       
        Args:
            write_data: Array of bytes
       
        Returns:
            Nothing
       
        Raises:
            NysaCommError: Error in communication
        """
        char_len = self.get_character_length() / 8
        if char_len == 0:
            char_len = 1

        if self.is_lsb_enabled():
            if self.debug:
                print "LSB First"
            while char_len > write_data:
                write_data.insert(0, 0xFF)

            while (len(write_data) % 4) != 0:
                write_data.insert(0, 0x00)

        else:
            #MSB First
            if self.debug:
                print "MSB First"
                print "Write Length: %d, Char Length / 8: %d" % (len(write_data), char_len)
            while char_len > len(write_data):
                write_data.append(0xFF)

            while (len(write_data) % 4) != 0:
                write_data.insert(0, 0x00)

            if len(write_data) > 16:
                raise SPIError("Length of write data is too long: %d (Max == 16)" % len(write_data))

            if self.debug:
                print "Write Data: %s" % str(write_data)

            self.write(WRITE_DATA0, write_data)

def unit_test(nysa, dev_id):

    spi = SPI(nysa, dev_id)
    clock_rate = spi.get_clock_rate()
    print "Clock rate: %d" % clock_rate

    char_len = spi.get_character_length()
    print "Character Length: %d" % char_len
    print "Setting Charcter Length to 16"
    spi.set_character_length(16)
    char_len = spi.get_character_length()
    print "Character Length: %d" % char_len

    print "Is busy?"
    is_busy = spi.is_busy()
    if is_busy:
        print "\tBusy!"
    else:
        print "\tNot Busy!"

    print "Enable Interrupts"
    spi.enable_interrupt(True)
    print "Is Interrupts enabled?"
    if spi.is_interrupt_enabled():
        print "\tInterrupt is enabled"
    else:
        print "\tInterrupt is not enabled"

    print "Disable Interrupts"
    spi.enable_interrupt(False)
    print "Is Interrupts enabled?"
    if spi.is_interrupt_enabled():
        print "\tInterrupt is enabled"
    else:
        print "\tInterrupt is not enabled"

    print "Test LSB Enabled"
    print "Setting LSB Enabled"
    spi.set_lsb_enable(True)
    print "Is LSB Enabled?"
    if spi.is_lsb_enabled():
        print "\tEnabled"
    else:
        print "\tNot Enabled"

    print "Disable LSB Enabled"
    spi.set_lsb_enable(False)
    print "Is LSB Enabled?"
    if spi.is_lsb_enabled():
        print "\tEnabled"
    else:
        print "\tNot Enabled"

    #clock rate
    print "Setting clock rate to 1MHz"
    spi.set_spi_clock_rate(1000000)

    #get/set TX/RX polarity
    print "Setting TX Polarity to positive"
    spi.set_tx_polarity(True)
 
    if spi.is_tx_polarity_positive():
        print "TX Polarity is positive"
    else:
        print "TX Polarity is negative"
 
    print "Setting TX Polarity to negative"
    spi.set_tx_polarity(False)
 
    if spi.is_tx_polarity_positive():
        print "TX Polarity is positive"
    else:
        print "TX Polarity is negative"
 
    spi.set_tx_polarity(True)
 
    print "Setting RX Polarity to positive"
    spi.set_rx_polarity(True)
 
    if spi.is_rx_polarity_positive():
        print "RX Polarity is positive"
    else:
        print "RX Polarity is negative"
 
    print "Setting RX Polarity to negative"
    spi.set_rx_polarity(False)
 
    if spi.is_rx_polarity_positive():
        print "RX Polarity is positive"
    else:
        print "RX Polarity is negative"
 
    spi.set_rx_polarity(True)

    #slave select
    print "Getting slave select raw"
    slave_select = spi.get_slave_select_raw()
    print "Slave select: %d" % slave_select
 
    print "Setting slave select raw"
    spi.set_slave_select_raw(0x01)
 
    print "Getting slave select raw"
    slave_select = spi.get_slave_select_raw()
    print "Slave select: %d" % slave_select
 
    spi.set_slave_select_raw(0x00)
 
 
    #set slave select bit
    print "Checking setting/clearing slave bit"
 
    print "Checking if bit 2 is set"
    if spi.is_spi_slave_selected(2):
        print "bit 2 is set"
    else:
        print "bit 2 is not set"
 
    print "Setting bit 2"
    spi.set_spi_slave_select(2, True)
 
    #set auto select mode
    spi.set_auto_ss_control(True)
    if spi.is_auto_ss():
        print "Auto ss successfully set"
    else:
        print "Auto ss not successfully set"
 
 
    print "Checking if bit 2 is set"
    if spi.is_spi_slave_selected(2):
        print "bit 2 is set"
    else:
        print "bit 2 is not set"

    #Setup to interface 

    print "Setting Write Data"
    write_data = Array('B', [0, 1, 2, 3])
    spi.set_write_data(write_data)
 
    print "Getting read data:"
    read_data = spi.get_read_data(16)
    print "Read data: %s" % str(read_data)
 
 
    print "start a transaction"
    spi.start_transaction()
 
    while spi.is_busy():
        print "busy!"
 
 
    #print "Getting read data:"
    #read_data = spi.get_read_data(16)
    #print "Read data: %s" % str(read_data)


