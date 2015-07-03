#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import spi
from nysa.common.status import Status

class Test (unittest.TestCase):

    def setUp(self):
        s = Status()
        s.set_level("fatal")

        print "Unit test!"
        pass
        '''
        for name in get_platforms():
            try:
                self.n = find_board(name, status = s)
            except PlatformScannerException as ex:
                pass
        self.n.read_sdb()
        urns = self.n.find_device(SPI)
        self.simple_dev = MockGPIODriver(self.n, urns[0], False)
        s.set_level("error")
        '''

    def notest_spi(self):
        '''
        spi = SPI(nysa, urn)
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

        print "Checking if bit 0 is set"
        if spi.is_spi_slave_selected(0):
            print "bit 0 is set"
        else:
            print "bit 0 is not set"

        print "Setting bit 0"
        spi.set_spi_slave_select(0, True)

        #set auto select mode
        spi.auto_ss_control_enable(True)
        if spi.is_auto_ss():
            print "Auto ss successfully set"
        else:
            print "Auto ss not successfully set"


        print "Checking if bit 0 is set"
        if spi.is_spi_slave_selected(0):
            print "bit 0 is set"
        else:
            print "bit 0 is not set"

        #Setup to interface

        print "Setting TX Polarity to positive"
        spi.set_tx_polarity(True)

        print "Setting RX Polarity to positive"
        spi.set_rx_polarity(True)

        print "Setting Write Data"
        write_data = Array('B', [0xAA, 0xAA, 0xAA, 0xAA])
        spi.set_character_length(0)
        spi.set_write_data(write_data)

        print "start a transaction"
        spi.start_transaction()


        while spi.is_busy():
            print "busy!"

        print "Getting read data:"
        read_data = spi.get_read_data(0)
        print "Read data: %s" % str(read_data)


        #print "Getting read data:"
        #read_data = spi.get_read_data(16)
        #print "Read data: %s" % str(read_data)
        '''
        pass

if __name__ == "__main__":
    unittest.main()

