#! /usr/bin/python
import sys
import os
import json
import string
from array import array as Array

#sys.path.append(os.path.join(os.path.dirname(__file__)))

class DRTError(Exception):
  """DRTError

  Errors associated with Devcie ROM Table:
    invalid JSON file.
    DRT is not defined
  """
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class DRTManager():

  def __init__(self):
    self.drt_lines = []
    self.drt_string = ""
    self.drt = Array('B')
    self.num_of_devices = 0

  def set_drt(self, drt):
    self.drt = drt
    self.drt_string = ""
    self.num_of_devices = get_number_of_devices(drt)
    display_len = 8 + self.num_of_devices * 8
    for i in range (0, display_len):
      self.drt_string += "%02X%02X%02X%02X\n"% (self.drt[i * 4], self.drt[(i * 4) + 1], self.drt[i * 4 + 2], self.drt[i * 4 + 3])

    self.drt_lines = self.drt_string.splitlines()
    self.num_of_devices = get_number_of_devices(self.drt)


  def is_memory_device(self, device_index):
    """is_memory_device
    
    Queries the DRT to see if the device is on the memory bus or the 
    peripheral bus

    Args:
      device_index: Index of the device to test

    Returns:
      True: Device is on the memory bus
      False: Device is on the peripheral bus

    Raises:
      Nothing
    """
    flags = int(self.drt_lines[((device_index + 1) * 8) + 1], 16)

    if ((flags & 0x00010000) > 0):
      return True

    return False
    

  def get_number_of_devices(self):
    """get_number_of_devices

    Can be used to get the number of devices from the pre-existing DRT stored
    in this class

    Args:
      Nothing

    Returns:
      Number of devices on the DRT

    Raises:
      DRTError: Device not found 
    """
    return self.num_of_devices

  def is_device_attached(self, device_id):
    """is_device_attached

    Determine if the device with the specified ID exists

    Check if something like a UART is attached to the bus

    Args:
      device_id: device identification number

    Returns:
      True: the device is attached to the bus
      False: the device is not attached to the bus
    
    Raises:
      Nothing
    """
    for dev_index in range (0, self.num_of_devices):
      dev_id = string.atoi(self.drt_lines[((dev_index + 1) * 8)], 16)
      if (self.dbg):
        print "dev_id: " + str(dev_id)
      if (dev_id == device_id):
        return True
    return False
  
  def get_address_from_index(self, device_index):
    """get_address_from_index

    From the index within the DRT return the address of where to find this 
    device

    Args:
      device_index: index of the device

    Returns:
      32bit address of the device

    Raises:
      Nothing
    """
    return (string.atoi(self.drt_lines[((device_index + 1) * 8) + 2], 16)) >> 24


  def get_id_from_index(self, device_index):
    """get_id_from_index

    From the index within the DRT return the ID of this device

    Args:
      device_index: index of the device

    Returns:
      Standard device ID

    Raises:
      Nothing
    """
    return string.atoi(self.drt_lines[((device_index + 1) * 8)], 16)


  def get_size_from_index(self, device_index):
    """get_size_from_index

    Depending on if this is a memory device or a peripheral device
    return either the number of registers associated with the peripheral or
    the size of the memory device

    Args:
      device_index: index of the device

    Returns:
      Either the number of registers or the size of the memory device

    Raises:
      Nothing
    """
    return string.atoi(self.drt_lines[((device_index + 1) * 8) + 3], 16)

  def get_device_flags(self, device_index):
    """get_device_flags

    Identifies the name of the flags with the device at the given
    device_index
    """
    flag_strings = []
    flags = int(self.drt_lines[((device_index + 1) * 8) + 1], 16)
    if ((flags & 0x00000001) > 0):
      flag_strings.append("0x00000001: Standard Device")
    if ((flags & 0x00010000) > 0):
      flag_strings.append("0x00010000: Memory Device")
    return flag_strings

  def pretty_print_drt(self):
    """pretty_print_drt

    Prints out the DRT in a pretty way

    Args:
      Nothing

    Returns:
      Nothing

    Raises:
      Nothing
    """
    num = int(self.drt_lines[1], 16)
 
    #the first line is the version of the DRT and the ID
    white = '\033[0m'
    gray = '\033[90m'
    red   = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    purple = '\033[95m'
    cyan = '\033[96m'
 
    test = '\033[97m'
 
    print red,
    print "DRT:"
    print ""
    print "%s%s:%sVersion: %s ID Word: %s" % (blue, self.drt_lines[0], green, self.drt_lines[0][0:4], self.drt_lines[0][4:8])
    print "%s%s:%sNumber of Devices: %d" % (blue, self.drt_lines[1], green, int(self.drt_lines[1], 16))
    print "%s%s:%sString Table Offset (0x0000 == No Table)" % (blue, self.drt_lines[2], green)
    print "%s%s:%sReserverd for future use" % (blue, self.drt_lines[3], green)
    print "%s%s:%sReserverd for future use" % (blue, self.drt_lines[4], green)
    print "%s%s:%sReserverd for future use" % (blue, self.drt_lines[5], green)
    print "%s%s:%sReserverd for future use" % (blue, self.drt_lines[6], green)
    print "%s%s:%sReserverd for future use" % (blue, self.drt_lines[7], green)
 
    print red,
    print "Devices:"
    for i in range (0, self.num_of_devices):
      memory_device = False 
      f = int (self.drt_lines[((i + 1) * 8 + 1)], 16) 
      if ((f & 0x00010000) > 0):
        memory_device = True
      print ""
      print red,
      print "Device %d" % i
      type_value = int(self.drt_lines[(i + 1) * 8], 16)
      type_name = get_device_type(type_value)
      print "%s%s:%sDevice Type: %s" % (blue, self.drt_lines[(i + 1) * 8], green, type_name) 
      print "%s%s:%sDevice Flags:" % (blue, self.drt_lines[((i + 1) * 8) + 1], green)
      flags = self.get_device_flags(i)
      for j in flags:
        print "\t%s%s" % (purple, j)
 
      if memory_device:
        print "%s%s:%sOffset of Memory Device:      0x%08X" % (blue, self.drt_lines[((i + 1) * 8) + 2], green, int(self.drt_lines[((i + 1) * 8) + 2], 16))
        print "%s%s:%sSize of Memory device:        0x%08X" % (blue, self.drt_lines[((i + 1) * 8) + 3], green, int (self.drt_lines[((i + 1) * 8) + 3], 16))
 
 
      else:
        print "%s%s:%sOffset of Peripheral Device:  0x%08X" % (blue, self.drt_lines[((i + 1) * 8) + 2], green, int(self.drt_lines[((i + 1) * 8) + 2], 16))
        print "%s%s:%sNumber of Registers :         0x%08X" % (blue, self.drt_lines[((i + 1) * 8) + 3], green, int(self.drt_lines[((i + 1) * 8) + 3], 16))
 
      print "%s%s:%sReserved for future use" % (blue, self.drt_lines[((i + 1) * 8) + 4], green)
      print "%s%s:%sReserved for future use" % (blue, self.drt_lines[((i + 1) * 8) + 5], green)
      print "%s%s:%sReserved for future use" % (blue, self.drt_lines[((i + 1) * 8) + 6], green)
      print "%s%s:%sReserved for future use" % (blue, self.drt_lines[((i + 1) * 8) + 7], green)
 
 
    print white,


  def get_total_memory_size(self):
  
    """get_total_memory_size

    adds all the contiguous memory peripherals together and returns the
    total size
  
    Note: this memory must start at address 0

    Args:
      Nothing

    Returns:
      Size of the total memory

    Raises:
      DRTError: DRT Not defined
    """

    offset = 0
    if self.drt is None:
      raise DRTError("DRT Not Defined")


    offset = 0x00
    num_devices = self.get_number_of_devices()
    while (1):
      prev_offset = offset
      for dev_index in range (0, num_devices):
        memory_device = self.is_memory_device(dev_index)
        dev_offset = self.get_address_from_index(dev_index)
        dev_size = self.get_size_from_index(dev_index)
        device_id = self.get_id_from_index(dev_index)
        if (device_id == 5):
          if dev_offset == offset:
            offset = offset + dev_size + 1

      if prev_offset == offset:
        break
            
    if offset > 0:
      return offset - 1

    return 0x00
              





""" Utility Functions

Functions that can be called outside of the class
"""
def get_number_of_devices(initial_block):
  """get_number_of_devices

  Determine the number of devices that are available from
  the initial read (specify the first 8 32 bit words of a DRT in 
  'initial_block')

  Args:
    initial_block: Initial block of the drt (if not specified the stored DRT
      is used

  Returns:
    Number of devices on the DRT
  """
  num_of_devices = (initial_block[4] << 24 | initial_block[5] << 16 | initial_block[6] << 8 | initial_block[7])
  return num_of_devices



def get_device_list():
  """get a list of devices"""
  drt_tags = {}
  dev_tags = {}
  dev_list = []
  index = 0
  length = 0
  try: 
    f = open(os.path.join(os.path.dirname(__file__), "drt.json"), "r")
    drt_tags = json.load(f)
  except TypeError as err:
    print "JSON Error: %s" % str(err)
    raise DRTError("DRT Error: %s", str(err)) 

  dev_tags = drt_tags["devices"]

  length = len(dev_tags) 

  for i in range(0, length):
    for key in dev_tags.keys():
      #change the hex number into a integer
      in_str = dev_tags[key]["ID"]
      index = int(dev_tags[key]["ID"][2:], 16)
      if index == i:
        dev_tags[key]["name"] = key
        dev_list.insert(index, dev_tags[key])
  return dev_list


def get_device_index(name):
  """get the index of the device speicified by name"""
  dev_list = get_device_list()
    
  for i in range(0, len(dev_list)):
    if name == dev_list[i]["name"]:
      return i 

  raise DRTError("Name: %s is not a known type of devices" % name) 

def get_device_type(index):
  """Given a index return the name of the Device"""
  dev_list = get_device_list()
  return dev_list[index]["name"]

def get_flag_tags():
  """Returns a listing of the Flags"""
  drt_tags = {}
  flag_tags = {}

  try: 
    f = open(os.path.join(os.path.dirname(__file__), "drt.json"), "r")
    drt_tags = json.load(f)
  except TypeError as err:
    print "JSON Error: %s" % str(err)
    raise DRTError("DRT Error: %s", str(err)) 

  flag_tags = drt_tags["flags"]
  return flag_tags

def get_device_flag_names(flags_string):
  """Reads in a flag string and returns the flags that are set
  in a human readible view"""

  flag_tags = get_flag_tags()
  flags = int(flags_string, 16)
  flag_names = []

  for key in flag_tags.keys():
    test_value = 2 ** flag_tags[key]["bit"]
    if (test_value & flags) > 0:
      flag_names.append("0x%8X: %s" % (test_value, key))
  return flag_names
  

def pretty_print_drt(drt):
  """takes in a DRT string and prints it in a pretty way"""
  drt_lines = drt.splitlines()
  num = int(drt_lines[1], 16)

  #the first line is the version of the DRT and the ID
  white = '\033[0m'
  gray = '\033[90m'
  red   = '\033[91m'
  green = '\033[92m'
  yellow = '\033[93m'
  blue = '\033[94m'
  purple = '\033[95m'
  cyan = '\033[96m'

  test = '\033[97m'

  print red,
  print "DRT:"
  print ""
  print "%s%s:%sVersion: %s ID Word: %s" % (blue, drt_lines[0], green, drt_lines[0][0:4], drt_lines[0][4:8])
  print "%s%s:%sNumber of Devices: %d" % (blue, drt_lines[1], green, int(drt_lines[1], 16))
  print "%s%s:%sString Table Offset (0x0000 == No Table)" % (blue, drt_lines[2], green)
  print "%s%s:%sReserverd for future use" % (blue, drt_lines[3], green)
  print "%s%s:%sReserverd for future use" % (blue, drt_lines[4], green)
  print "%s%s:%sReserverd for future use" % (blue, drt_lines[5], green)
  print "%s%s:%sReserverd for future use" % (blue, drt_lines[6], green)
  print "%s%s:%sReserverd for future use" % (blue, drt_lines[7], green)

  print red,
  print "Devices:"
  for i in range (0, num_of_devices):
    memory_device = False 
    f = int (drt_lines[((i + 1) * 8 + 1)], 16) 
    if ((f & 0x00010000) > 0):
      memory_device = True
    print ""
    print red,
    print "Device %d" % i
    type_value = int(drt_lines[(i + 1) * 8], 16)
    type_name = get_device_type(type_value)
    print "%s%s:%sDevice Type: %s" % (blue, drt_lines[(i + 1) * 8], green, type_name) 
    print "%s%s:%sDevice Flags:" % (blue, drt_lines[((i + 1) * 8) + 1], green)
    flags = self.get_device_flags(i)
    for j in flags:
      print "\t%s%s" % (purple, j)

    if memory_device:
      print "%s%s:%sOffset of Memory Device:      0x%08X" % (blue, drt_lines[((i + 1) * 8) + 2], green, int(drt_lines[((i + 1) * 8) + 2], 16))
      print "%s%s:%sSize of Memory device:        0x%08X" % (blue, drt_lines[((i + 1) * 8) + 3], green, int (drt_lines[((i + 1) * 8) + 3], 16))


    else:
      print "%s%s:%sOffset of Peripheral Device:  0x%08X" % (blue, drt_lines[((i + 1) * 8) + 2], green, int(drt_lines[((i + 1) * 8) + 2], 16))
      print "%s%s:%sNumber of Registers :         0x%08X" % (blue, drt_lines[((i + 1) * 8) + 3], green, int(drt_lines[((i + 1) * 8) + 3], 16))

    print "%s%s:%sReserved for future use" % (blue, drt_lines[((i + 1) * 8) + 4], green)
    print "%s%s:%sReserved for future use" % (blue, drt_lines[((i + 1) * 8) + 5], green)
    print "%s%s:%sReserved for future use" % (blue, drt_lines[((i + 1) * 8) + 6], green)
    print "%s%s:%sReserved for future use" % (blue, drt_lines[((i + 1) * 8) + 7], green)


  print white,

 

if __name__ == "__main__":
  """test all functions"""
  dev_list = get_device_list()
  print "Devices:"
  for i in range(0, len(dev_list)):
    print "\t%s" % dev_list[i]["name"]
    print "\t\tID: 0x%04X" % i 
    print "\t\tDescription: %s" % dev_list[i]["description"]

  print "\n\n"
  print "GPIO index: %d" % get_device_index("GPIO")
  #get_device_index ("bob")


