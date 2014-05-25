# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

""" dionysus

Concrete interface for Nysa on the Dionysus platform
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

""" Changelog:
10/18/2013
    -Pep8ing the module and some cleanup
09/21/2012
    -added core dump function to retrieve the state of the master when a crash
    occurs
08/30/2012
    -Initial Commit
"""
import sys
import os
import threading
import time
from array import array as Array


p = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from nysa import Nysa
from nysa import NysaCommError

from pyftdi.pyftdi.ftdi import Ftdi
from array import array as Array

from bitbang.bitbang import BitBangController



INTERRUPT_COUNT = 32

#50 mS sleep between interrupt checks
INTERRUPT_SLEEP = 0.050
#INTERRUPT_SLEEP = 1

class ReaderThread(threading.Thread):

    def __init__(self, dev, interrupt_update_callback, lock, debug):
        super(ReaderThread, self).__init__()
        self.dev = dev

        self.interrupt_update_callback = interrupt_update_callback
        self.lock = lock
        self.term_flag = False
        self.debug = debug
        self.interrupts_cb = []
        for i in range(INTERRUPT_COUNT):
            self.interrupts_cb.append([])

    def stop(self):
        if self.debug: print "Finish!"
        self.term_flag = True

    def update_interrupts(self, interrupts):
        print "Updating interrupt..."

    def register_interrupt_cb(self, index, callback):
        if self.debug: print "Registering Callback for device: %d" % index
        if index > INTERRUPT_COUNT - 1:
            raise NysaCommError("Index of interrupt device is out of range (> %d)" % (INTERRUPT_COUNT - 1))
        self.interrupts_cb[index].append(callback)

    def unregister_interrupt_cb(self, index, callback = None):
        if self.debug: print "Unregister Callback for device: %d" % index
        if index > INTERRUPT_COUNT -1:
            raise NysaCommError("Index of interrupt device is out of range (> %d)" % (INTERRUPT_COUNT - 1))
        interrupt_list = self.interrupts_cb[index]
        if callback is None:
            interrupt_list = []

        elif callback in interrupt_list:
            interrupt_list.remove(callback)

    def run(self):
        if self.debug: print "Reader thread started"
        while not self.term_flag:
            data = ""
            try:
                if self.lock.acquire(False):
                    try:
                        #print "+",
                        #if self.debug: print "got lock"
                        
                        data = self.dev.read_data_bytes(13)
                        #if self.debug: print "release lock"
                        
                        if len(data) > 0 and 220 in data:
                            offset = data.index(220)
                            if offset > 0:
                                data = data[offset:]
                                data += self.dev.read_data_bytes(offset)
                
                            #print ".",
                            #data = Array('B', data)
                            if len(data) > 2:
                                if self.debug: print "Data: %s" % str(data)
                            #print "Data: %s" % str(data)
                            if data[0] == 50 and data[1] == 96:
                                data = self.dev.read_data_bytes(2)
                
                            if data[0] != 0xDC:
                                continue
                            if len(data) >= 13:
                                interrupts = (data[9]  << 24 |
                                              data[10] << 16 |
                                              data[11] << 8  |
                                              data[12])
                        
                                if self.debug: print "Got Interrupts: 0x%08X" % interrupts
                                self.process_interrupts(interrupts)
                                self.interrupt_update_callback(interrupts)
                            #print "Purge buffers"
                            #self.dev.purge_buffers()
                    except:
                        if self.debug: print "Exception when reading interrupts!"
                        pass
                
                    finally:
                        self.lock.release()
                        #print "- "
                else:
                    if self.debug: print "Lock not aquired"
            except:
                pass

            time.sleep(INTERRUPT_SLEEP)

    def process_interrupts(self, interrupts):
        for i in range(INTERRUPT_COUNT):
            if (interrupts & 1 << i) == 0:
                continue
            if len(self.interrupts_cb[i]) == 0:
                continue
            #Call all callbacks
            if self.debug: print "Calling callback for: %d" % i
            for cb in self.interrupts_cb[i]:
                try:
                    cb()
                except TypeError:
                    #If an error occured when calling a callback removed if from
                    #our list
                    self.interrupts_cb.remove(cb)
                    print "Error need to remove callback"


class Dionysus (Nysa):
    """
    Dionysus

    Concrete Class that implemented Dionysus specific communication functions
    """

    def __init__(self, idVendor = 0x0403, idProduct = 0x8530, sernum = None, debug = False):
        Nysa.__init__(self, debug)
        self.vendor = idVendor
        self.product = idProduct
        self.sernum = sernum

        self.debug = debug
        self.dev = None
        self.lock = threading.Lock()
        

        self.dev = Ftdi()
        self._open_dev()
        self.name = "Dionysus"
        self.debug = debug
        try:
            #XXX: Hack to fix a strange bug where FTDI
            #XXX: won't recognize Dionysus until a read and reset occurs
            btimeout = self.timeout
            self.timeout = 0.1
            self.ping()
            self.timeout = btimeout
        except NysaCommError:
            self.timeout = btimeout
            self.reset()

        #debug = True
        self.reader_thread = ReaderThread(self.dev, self.interrupt_update_callback, self.lock, debug = debug)
        self.reader_thread.setName("Reader Thread")
        self.reader_thread.setDaemon(True)
        self.reader_thread.start()

    def __del__(self):
        print "Close reader thread"
        #self.lock.aquire()
        #if (self.reader_thread is not None) and self.reader_thread.isAlive():
        #    self.reader_thread.stop()
        #    print "Waiting to join"
        #    self.reader_thread.join()
        #self.lock.release()
        #self.debug = True
        if self.debug: print "Reader thread joined"
        self.dev.close()

    def _open_dev(self):
        """_open_dev

        Open an FTDI Communication Channel

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Exception
        """
        #This frequency should go up to 60MHz
        frequency = 30.0E6
        #Latency can go down to 2 but there is a small chance there will be a
        #crash
        latency  = 2
        Ftdi.add_type(self.vendor, self.product, 0x700, "ft2232h")
        self.dev.open(self.vendor, self.product, 0, serial = self.sernum)

        #Drain the input buffer
        self.dev.purge_buffers()

        #Reset
        #Configure Clock
        frequency = self.dev._set_frequency(frequency)

        #Set Latency Timer
        self.dev.set_latency_timer(latency)

        #Set Chunk Size (Maximum Chunk size)
        self.dev.write_data_set_chunksize(0x10000)
        self.dev.read_data_set_chunksize(0x10000)

        #Set the hardware flow control
        self.dev.set_flowctrl('hw')
        self.dev.purge_buffers()
        #Enable MPSSE Mode
        self.dev.set_bitmode(0x00, Ftdi.BITMODE_SYNCFF)




    def read(self, device_id, address, length = 1, memory_device = False):
        """read

        read data from Dionysus

        Command Format

        ID 02 NN NN NN OO AA AA AA
           ID: ID Byte (0xCD)
           02: Read Command (12 for memory read)
           NN: Size of Read (3 Bytes)
           OO: Offset (for peripheral, part of address for mem)
           AA: Address (3 bytes for peripheral,
               (4 bytes including offset for mem)

        Args:
            device_id (int): Device Identification number, found in the DRT
                (DRT Address = 0)
            address (int): Address of the register/memory to read
            memory_device (boolean): True if the device is on the memory bus
            length (int): Number of 32-bit words to read

        Returns:
            (Byte Array): A byte array containing the raw data returned from
            Dionysus

        Raises:
            NysaCommError
        """
        #self.debug = True
        with self.lock:
            if self.debug: print "Reading..."
            read_data = Array('B')
            #Set up the ID and the 'Read command (0x02)'
            write_data = Array('B', [0xCD, 0x02])
            if memory_device:
                if self.debug:
                    print "Read from Memory Device"
                #'OR' the 0x10 flag to indicate that we are using the memory bus
                write_data = Array('B', [0xCD, 0x12])
            
            #Add the length value to the array
            fmt_string = "%06X" % length
            write_data.fromstring(fmt_string.decode('hex'))
            
            #Add the device Number
            
            #XXX: Memory devices don't have an offset (should they?)
            offset_string = "00"
            if not memory_device:
                offset_string = "%02X" % device_id
            
            write_data.fromstring(offset_string.decode('hex'))
            
            #Add the address
            addr_string = "%06X" % address
            write_data.fromstring(addr_string.decode('hex'))
            if self.debug:
                print "DEBUG: Data read string: %s" % str(write_data)

            self.dev.purge_buffers()
            self.dev.write_data(write_data)
            
            timeout = time.time() + self.timeout
            rsp = Array ('B')
            while time.time() < timeout:
                rsp = self.dev.read_data_bytes(1)
                if len(rsp) > 0 and rsp[0] == 0xDC:
                    if self.debug: print "Got a Response"
                    break
            
            if len(rsp) > 0:
                if rsp[0] != 0xDC:
                    if self.debug:
                        print "Response Not Found"
                    raise NysaCommError("Did not find identification byte (0xDC): %s" % str(rsp))
            
            else:
                if self.debug:
                    print "Timed out while waiting for response"
                raise NysaCommError("Timeout while waiting for a response")
            
            #Watch out for the modem status bytes
            read_count = 0
            response = Array ('B')
            rsp = Array('B')
            timeout = time.time() + self.timeout
            
            total_length = length * 4 + 8
            
            while (time.time() < timeout) and (read_count < total_length):
                rsp += self.dev.read_data_bytes(total_length - read_count)
                read_count = len(rsp)
            
            #self.debug = True
            if self.debug:
                print "DEBUG READ:"
                print "\tRead Length: %d, Total Length: %d" % (len(rsp), total_length)
                #print "Time left on timeout: %d" % (timeout - time.time())

                print "\tResponse Length: %d" % len(rsp)
                print "\tResponse Status: %s" % str(rsp[:8])
                print "\tResponse Dev ID: %d Addr: 0x%06X" % (rsp[4], (rsp[5] << 16 | rsp[6] << 8 | rsp[7]))
                print "\tResponse Data:\n\t%s" % str(rsp[8:])
            #self.debug = False
            #self.debug = False
            return rsp[8:]


    def write(self, device_id, address, data, memory_device=False):
        """write

        Write data to a Nysa image

        Command Format

        ID 01 NN NN NN OO AA AA AA DD DD DD DD
           ID: ID Byte (0xCD)
           01: Write Command (11 for Memory Write)
           NN: Size of Write (3 Bytes)
           OO: Offset (for peripheral, part of address for mem)
           AA: Address (3 bytes for peripheral,
             #(4 bytes including offset for mem)
           DD: Data (4 bytes)

        Args:
            device_id (int): Device identification number, found in the DRT
            address (int): Address of the register/memory to write to
            memory_device (boolean):
                True: Memory device
                False: Peripheral device
            data (array of bytes): Array of raw bytes to send to the devcie

        Returns: Nothing

        Raises:
            NysaCommError
        """

        with self.lock:
            length = len(data) / 4
            #Create an Array with the identification byte and code for writing
            data_out = Array ('B', [0xCD, 0x01])
            if memory_device:
                if self.debug:
                    print "Memory Device"
                data_out = Array('B', [0xCD, 0x11])
            
            #Append the length into the first 24 bits
            fmt_string = "%06X" % length
            data_out.fromstring(fmt_string.decode('hex'))
            offset_string = "00"
            if not memory_device:
                offset_string = "%02X" % device_id
            data_out.fromstring(offset_string.decode('hex'))
            addr_string = "%06X" % address
            data_out.fromstring(addr_string.decode('hex'))
            data_out.extend(data)
            if self.debug:
                print "Length: %d" % len(data)
                print "Reported Length: %d" % length
                print "Writing: %s" % str(data_out[0:9])
                print "\tData: %s" % str(data_out[9:13])
        
            #Avoid the akward stale bug
            '''
            d = self.dev.read_data_bytes(13)
            if d > 0:
                print "D: %s" % str(d)
            '''


            self.dev.purge_buffers()
            self.dev.write_data(data_out)
            rsp = Array ('B')
            #self.debug = True
            if self.debug and (len(data_out) < 100):
                print "Data Out: %s" % str(data_out)
            
            timeout = time.time() + self.timeout
            
            while time.time() < timeout:
                #response = self.dev.read_data_bytes(1)
                rsp = self.dev.read_data_bytes(1)
                if len(rsp) > 0 and rsp[0] == 0xDC:
                    if self.debug: print "Got a response"
                    break
            #self.debug = False
            
            
            if len(rsp) > 0:
                if rsp[0] != 0xDC:
                    if self.debug:
                        print "Reponse ID Not found"
                    raise NysaCommError("Did not find ID byte (0xDC) in response: %s" % str(rsp))
            
            else:
                if self.debug:
                    print "No Response"
                raise NysaCommError ("Timeout while waiting for response")
            
            
            rsp = self.dev.read_data_bytes(12)
            if self.debug:
                print "DEBUG: Write Response: %s" % str(rsp[0:8])
                #print "Response: %s" % str(rsp)


    def ping (self):
        """ping

        Command Format

        ID 00 00 00 00 00 00 00 00
            ID: ID Byte (0xCD)
            00: Ping Command
            00 00 00 00 00 00 00: Zeros

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        data = Array('B')
        data.extend([0xCD, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        if self.debug:
            print "Sending ping...",
        with self.lock:
            self.dev.write_data(data)
            
            #Set up a response
            rsp = Array('B')
            temp = Array('B')
            
            timeout = time.time() + self.timeout
            
            while time.time() < timeout:
                rsp = self.dev.read_data_bytes(5)
                temp.extend(rsp)
                if 0xDC in rsp:
                    if self.debug:
                        print "Response to Ping"
                        print "Resposne: %s" % str(temp)
                    break
            
            if not 0xDC in rsp:
                if self.debug:
                    print "ID byte not found in response"
                raise NysaCommError("Ping response did not contain ID: %s" % str(temp))
            
            index = rsp.index (0xDC) + 1
            read_data = Array('B')
            read_data.extend(rsp[index:])
            
            num = 3 - index
            read_data.extend(self.dev.read_data_bytes(num))
            
            if self.debug:
                print "Success"
            
            return


    def reset (self):
        """ reset

        Software reset the Nysa FPGA Master, this may not actually reset the entire
        FPGA image

        ID 03 00 00 00
            ID: ID Byte (0xCD)
            00: Reset Command
            00 00 00: Zeros

        Args:
            Nothing

        Return:
            Nothing

        Raises:
            NysaCommError: Failue in communication
        """
        #data = Array('B')
        #data.extend([0xCD, 0x03, 0x00, 0x00, 0x00]);
        #if self.debug:
        #    print "Sending Reset..."

        #self.dev.purge_buffers()
        #self.dev.write_data(data)

        bbc = BitBangController(self.vendor, self.product, 2)
        bbc.set_soft_reset_to_output()
        bbc.soft_reset_high()
        time.sleep(.2)
        bbc.soft_reset_low()
        time.sleep(.2)
        bbc.soft_reset_high()
        bbc.pins_on()
        bbc.set_pins_to_input()



    def dump_core(self):
        """ dump_core

        Returns the state of the wishbone master priorto a reset, this is usefu for
        debugging a crash

        Command Format

        ID 0F 00 00 00 00 00 00 00
            ID: ID Byte (0xCD)
            0F: Dump Core Command
            00 00 00 00 00 00 00 00 00 00 00: Zeros

        Args:
            Nothing

        Returns:
            (Array of 32-bit Values) to be parsed by the core_analyzer utility

        Raises:
            NysaCommError: A failure in communication is detected
        """
        with self.lock:
            data = Array ('B')
            data.extend([0xCD, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            if self.debug:
                print "Sending core dump request..."
            self.dev.purge_buffers()
            self.dev.write_data(data)
            
            core_dump = Array('L')
            wait_time = 5
            timeout = time.time() + wait_time
            
            temp = Array ('B')
            while time.time() < timeout:
                rsp = self.dev.read_data_bytes(1)
                temp.extend(rsp)
                if 0xDC in rsp:
                    print "Read a response from the core dump"
                    break
            
            if not 0xDC in rsp:
                if self.debug:
                    print "Response not found!"
                raise NysaCommError("Response Not Found")
            
            rsp = Array ('B')
            read_total = 4
            read_count = len(rsp)
            
            #Get the number of items from the incomming data, This size is set by the
            #Wishbone Master
            timeout = time.time() + wait_time
            while (time.time() < timeout) and (read_count < read_total):
                rsp += self.dev.read_data_bytes(read_total - read_count)
                read_count = len(rsp)
            
            
            count = (rsp[1] << 16 | rsp[2] << 8 | rsp[3]) * 4
            if self.debug:
                print "Length of read:%d" % len(rsp)
                print "Data: %s" % str(rsp)
                print "Number of core registers: %d" % (count / 4)
            
            timeout = time.time() + wait_time
            read_total = count
            read_count = 0
            temp = Array ('B')
            rsp = Array('B')
            while (time.time() < timeout) and (read_count < read_total):
                rsp += self.dev.read_data_bytes(read_total - read_count)
                read_count = len(rsp)
            
            if self.debug:
                print "Length read: %d" % (len(rsp) / 4)
                print "Data: %s" % str(rsp)
            
            core_data = Array('L')
            for i in rage(0, count, 4):
                if self.debug:
                    print "Count: %d" % i
                    core_data.append(rsp[i] << 24 | rsp[i + 1] << 16 | rsp[i + 2] << 8 | rsp[i + 3])
            
            
            if self.debug:
                print "Core Data: %s" % str(core_data)
            
            return core_data

    def register_interrupt_callback(self, index, callback):
        """ register_interrupt

        Setup the thread to call the callback when an interrupt is detected

        Args:
            index (Integer): bit position of the device
                if the device is 1, then set index = 1
            callback: a function to call when an interrupt is detected

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.reader_thread.register_interrupt_cb(index, callback)

    def unregister_interrupt_callback(self, index, callback = None):
        """ unregister_interrupt_callback

        Removes an interrupt callback from the reader thread list

        Args:
            index (Integer): bit position of the associated device
                EX: if the device that will receive callbacks is 1, index = 1
            callback: a function to remove from the callback list

        Returns:
            Nothing

        Raises:
            Nothing (This function fails quietly if ther callback is not found)
        """
        self.reader_thread.unregister_interrupt_cb(index, callback)

    def wait_for_interrupts(self, wait_time = 1):
        """ wait_for_interrupts

        listen for interrupts for the user specified amount of time

        The Nysa image will send a small packet of info to the host when a slave
        needs to send information to the host

        Response Format
        DC 01 00 00 00 II II II II
            DC: Inverted CD is the start of a response
            01: Interrupt ID
            00 00 00 00 00 00 00 00: Zeros, reserved for future use
            II II II II: 32-bit interrupts


        Args:
            wait_time (Integer): the amount of time in seconds to wait for an
                interrupt

        Returns (boolean):
            True: Interrupts were detected
            Falses: Interrupts were not detected

        Raises:
            NysaCommError: A failure in communication is detected
        """
        #self.debug = True
        timeout = time.time() + wait_time

        #temp = Array('B')
        rsp = Array('B')

        with self.lock:
            while time.time() < timeout:
                rsp = self.dev.read_data_bytes(1)
                if 0xDC in rsp:
                    if self.debug: print "Received an interrupt response!"
                    break
            
            if not 0xDC in rsp:
                if self.debug:
                    print "Dionysus (Wait for Interrupts): Response not found"
                #self.debug = False
                return False
            
            read_total = 13
            read_count = len(rsp)

            while (time.time() < timeout) and (read_count < read_total):
                rsp += self.dev.read_data_bytes(read_total - read_count)
                read_count = len(rsp)
            
        index = rsp.index(0xDC) + 1
        read_data = Array('B')
        read_data.extend(rsp[index:])

        self.interrupts = read_data[-4] << 24 | read_data[-3] << 16 | read_data[-2] << 8 | read_data[-1]

        if self.debug:
            print "Interrupts: 0x%08X" % self.interrupts
        #self.debug = False
        return True


    def interrupt_update_callback(self, interrupts):
        self.interrupts = interrupts

