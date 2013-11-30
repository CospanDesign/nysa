import time
from array import array as Array
from serial_flash import SerialFlash
from pyftdi.pyftdi.spi import SpiController

class NumonyxFlashDevice(SerialFlash):
    """ Numonyx Flash Device Implementation
    
        Numonyx ID number is 0x20
    """

    #ID variables
    ID                  =   0x20
    
    #commands
    CMD_WRITE_ENABLE    =   0x06 # Write enable
    CMD_WRITE_DISABLE   =   0x04 # Write disable
    CMD_READ_JEDEC      =   0x9F # Read JEDED ID # (20H)
    CMD_READ_STATUS     =   0x05 # Read status register
    CMD_WRITE_STATUS    =   0x01 # Write status register
    CMD_READ_LO_SPEED   =   0x03 # Read @ low speed
    CMD_READ_HI_SPEED   =   0x0B # Read @ high speed
    CMD_PROGRAM_PAGE    =   0x02 # Write page
    CMD_ERASE_BLOCK     =   0xD8 # Erase full block
    CMD_PROGRAM_PAGE    =   0x02
    CMD_ERASE_SECTOR    =   0xD8
    CMD_ERASE_CHIP      =   0xC7
    CMD_SLEEP           =   0xB9
    CMD_WAKE            =   0xAB

    CMD_EWSR            =   0x50 # Enable write status register


    PAGE_DIV            =   8                   #??
    SECTOR_DIV          =   0x10                #place holder   

    PAGE_SIZE           =   1 << PAGE_DIV       #256 bytes  
    SECTOR_SIZE         =   1 << SECTOR_DIV     #65,536 bytes   
    NUM_SECTORS         =   (1 << 0x16) / SECTOR_SIZE   

    SPI_FREQUENCY_MAX   =   75                  # MHz
    ADDRESS_WIDTH       =   1


    SR_WIP              =   0b00000001  # Write in progress 
    SR_WEL              =   0b00000010  # Write Enable Latch bit    
    SR_BP0              =   0b00000100  # Block Protect bit 0   
    SR_BP1              =   0b00001000  # Block Protect bit 1
    SR_BP2              =   0b00010000  # Block Protect bit 2
    SR_WP               =   0b10000000  # Write Protect


    PROGRAM_PAGE_TIMES  =   (0.0010, 0.010)
    ERASE_SECTOR_TIMES  =   (0.7, 3)
    ERASE_BULK_TIMES    =   (6.8, 160)
    SPI_FREQ_MAX        =   30  #MHz

    def __init__(self, spiport, capacity):
        self._spi = spiport;
        self.capacity = capacity
        self._size = 1 << capacity
        self.NUM_SECTORS = (self._size) / self.SECTOR_SIZE

    def __len__(self):
        return self._size

    def __str__(self):
        return 'Numonyx %d KB, %d sectors each %d bytes' % (len(self) >> 10, self.NUM_SECTORS, self.SECTOR_SIZE)

    def get_capacity(self):
        return len(self)

    def is_busy(self):
        status = self._read_status()
        return (status & self.SR_WIP)

    def is_wren(self):
        status = self._read_status()
        return (status & self.SR_WEL)

    def wake(self):
        wake_cmd = Array('B', [self.CMD_WAKE, 0x00, 0x00, 0x00])
        self._spi.exchange(wake_cmd)

    def unlock(self):
        ewsr_cmd = Array('B', [self.CMD_WRITE_ENABLE])
        self._spi.exchange(ewsr_cmd)
        wrsr_cmd = Array('B', [ self.CMD_WITE_STATUS, (~(self.SR_WP | self.SR_BP0 | self.SR_BP1 | self.SR_BP2) & 0xFF)])
        self._spi.exchange(wrsr_cmd)

    def write (self, address, data):
        length = len(data)

        print "addr: %08X, len data: %08X, len self: %08X" % (address, len(data), len(self))
        if address + len(data) > len(self):
            raise SerialFlashValueError("Cannot fit in flash area")
        if not isinstance (data, Array):
            data = Array('B', data)

    #   data.byteswap()
        pos = 0
        percentage = 0.0
        while pos < length:
            percentage = (100.0 * pos / length)
            #print "percentage: %d @ 0x%08X" % (percentage, pos)

            size = min (length - pos, self.PAGE_SIZE)
            self._write(address, data[pos:pos + size])
            address += size
            pos += size

    def erase (self, address, length):
        #sanity check
        self.can_erase(address, length)

        start = address

        end = start + length

        self._enable_write()
        self._read_status()
        print "Erase 0x%08X - 0x%08X Length: %d" % (start, end, length)
        
        self._erase_blocks( self.CMD_ERASE_SECTOR,
                            self.ERASE_SECTOR_TIMES,
                            start, end,
                            self.SECTOR_SIZE)
#       self._disable_write()

    def bulk_erase(self):
        self._enable_write()
        ba_cmd = Array( 'B',
                        [self.CMD_ERASE_CHIP])
        self._spi.exchange(ba_cmd)
        self._wait_for_completion(self.ERASE_BULK_TIMES)

    
    def can_erase (self, address, length):
        if address & (self.SECTOR_SIZE - 1):
            raise serialflash.SerialFlashValueError("Start address should be aligned on a sector boundary")
        if length & (self.SECTOR_SIZE - 1):
#           print "Length: " + hex(length)
#           print "Sector_size: " + hex(self.SECTOR_SIZE)
            raise serialflash.SerialFlashValueError("End address should be aligned on a sector boundary")
        if (address + length) > len(self):
            raise SerialFlashValueError("Would erase over the flash capacity")

    def read (self, address, length):
        if address + length > len(self):
            raise SerialFlashValueError("Out of Range")
        buf = Array('B')
        while length > 0:
            size = min(length, SpiController.PAYLOAD_MAX_LENGTH)
#           print "reading %d bytes from address 0x%06X" % (size, address)
            data = self._read_hi_speed(address, size)
            length -= len(data)
            address += len(data)
            buf.extend(data)
        return buf

    def _read_lo_speed(self, address, length):
        read_cmd = Array('B', [ self.CMD_READ_LO_SPEED,
                                (address >> 16) & 0xFF, (address >> 8) & 0xFF, address & 0xFF])
        return self._spi.exchange(read_cmd, length)

    def _read_hi_speed(self, address, length):
#       print "reading %d bytes from addres: " % (length)
#       print "\t" + hex((address >> 16) & 0xFF) + ":" + hex((address>> 8) & 0xFF) + ":" + hex((address) & 0xFF)
        read_cmd = Array('B', [ self.CMD_READ_HI_SPEED,
                                ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF), 0xFF])
        return self._spi.exchange(read_cmd, length)
    
    def _write(self, address, data):
        """write only up to the size of a page"""
        sequences = []
        if address & (self.PAGE_SIZE - 1):
            #read spans two pages
            up = (address + (self.PAGE_SIZE - 1)) & ~(self.PAGE_SIZE - 1)
            count = min(len(data), up - address)
            sequences = [(address, data[:count]), (up, data[count:])]
        else:
            #read fits into one page
            sequences = [(address, data)]

        for addr, buf in sequences:
            self._enable_write()
            wcmd = Array('B', [self.CMD_PROGRAM_PAGE,
                                (addr >> 16) & 0xFF,
                                (addr >> 8) & 0xFF,
                                addr & 0xFF])
            wcmd.extend(data)
            self._spi.exchange(wcmd)
            self._wait_for_completion(self.PROGRAM_PAGE_TIMES)


    def _read_status(self):
        read_cmd = Array('B', [self.CMD_READ_STATUS])
        data = self._spi.exchange(read_cmd, 1)
#       print "status: " + str(data)
        if len(data) != 1:
            raise SerialFlashTimeout("Unable to retrieve flash status")
        return data[0]

    def _enable_write(self):
        wren_cmd = Array('B', [self.CMD_WRITE_ENABLE])
        self._spi.exchange(wren_cmd)

    def _disable_write(self):
        wrdi_cmd = Array('B', [self.CMD_WRITE_DISABLE])
        self._spi.exchange(wrdi_cmd)

    def _erase_blocks(self, command, times, start, end, size):
        while start < end:
#           print "ERASE BLOCK 0x%06x..0x%06x" % (start, start + size - 1)
            cmd = Array('B', [command,  
                                (start >> 16) & 0xFF,
                                (start >> 8) & 0xFF,
                                start & 0xFF])
            self._spi.exchange(cmd)
            self._wait_for_completion(times)
            start += size

    def _wait_for_completion(self, times):
        typical_time, max_time = times
        timeout = time.time()
        timeout += typical_time + max_time
        cycle = 0
        while self.is_busy():
#           print "."
            # need to wait at least once
            if cycle and time.time() > timeout:
                raise SerialFlashTimeout ("Command timeout (%d cycles)" % cycle)
            time.sleep(typical_time)
            cycle += 1

    def _unprotect(self):
        """Disable default protection for all sectors"""
        unprotect = Array ( 'B',
                            [self.CMD_WRITE_STATUS, 0x00])
        self._enable_write()
        self._spi.exchange(unprotect)
        while self.is_busy():
            time.sleep(0.01) # 10 ms

