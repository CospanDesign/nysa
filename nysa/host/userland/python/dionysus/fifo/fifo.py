"""
Nysa FIFO Control
"""

from pyftdi.pyftdi.ftdi import Ftdi
from array import array as Array

class FifoController(object):
    SYNC_FIFO_INTERFACE = 1
    SYNC_FIFO_INDEX = 0

    def __init__(self, vendor, product):
        self.vendor = vendor
        self.product = product
        self.f = Ftdi()


    def set_sync_fifo(self, frequency = 30.0E6, latency = 2):
        """Configure the interface for synchronous FIFO mode"""
        self.f.add_type(self.vendor, self.product, 0x700, "ft2232h")
        self.f.open(self.vendor, self.product, 0)
        #Drain the input buffer
        self.f.purge_buffers()
        #Enable MPSSE Mode
        self.f.set_bitmode(0x00, Ftdi.BITMODE_SYNCFF)
        #Configure the clock
        frequency = self.f._set_frequency(frequency)
        #Set latency timer
        self.f.set_latency_timer(latency)

        #Set Chunk size
        self.f.write_data_set_chunksize(0x10000)
        self.f.read_data_set_chunksize(0x10000)

        self.f.set_flowctrl('hw')
        self.f.purge_buffers()
        return frequency

    def set_async_fifo(self, frequency=6.0E6, latency = 2):
        """Configure the interface for asynchronous FIFO mode"""
        #Open FTDI Interface
        self.f.add_type(self.vendor, self.product, 0x700, "ft2232h")
        self.f.open(self.vendor,
                    self.product, 
                    self.SYNC_FIFO_INTERFACE, 
                    self.SYNC_FIFO_INDEX, 
                    None, 
                    None)
        self.f.set_latency_timer(latency) 
        self.f.write_data_set_chunksize(512)
        self.f.read_data_set_chunksize(512)
        self.f.purge_buffers()
        self.f.set_bitmode(0x00, Ftdi.BITMODE_BITBANG)
        frequency = self.f._set_frequency(frequency)
        self.f.purge_buffers()
        return frequency
        
