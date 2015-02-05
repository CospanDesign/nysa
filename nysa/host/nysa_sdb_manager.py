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


# -*- coding: utf-8 -*-


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

from common.status import Status

from cbuilder.sdb import SDBError

from cbuilder.sdb_component  import SDB_ROM_RECORD_LENGTH

from cbuilder.sdb_object_model import SOMRoot
from cbuilder.sdb_object_model import SOMBus

from cbuilder import sdb_object_model as som
from cbuilder import sdb_component as sdbc
from cbuilder import som_rom_parser as srp
from cbuilder import device_manager

class NysaSDBManager(object):

    def __init__(self, status = None):
        self.s = status

        if self.s is None:
            self.s = Status()
            self.s.Important("Generating a new Status")

    #SOM Functions
    def get_all_components_as_urns(self):
        component_list = []
        root = self.som.get_root()
        component_list.extend(self._get_bus_list(root))

        return list(set(component_list))

    def get_all_devices_as_urns(self):
        c_urns = self.get_all_components_as_urns()
        d_urns = []
        for c_urn in c_urns:
            c = self._get_component_from_urn(c_urn)
            if isinstance(c, SOMBus):
                continue
            d_urns.append(c_urn)

        return d_urns

    def _get_urn_from_component(self, component):
        urn = "/" + component.get_name()
        p = component.get_parent()
        #while not isinstance(p, SOMRoot) and p is not None:
        while p is not None:
            #print "Parent: %s" % p.get_name()
            urn = "/" + p.get_name() + urn
            p = p.get_parent()
        return urn

    def _get_bus_list(self, bus):
        #print "bus: %s" % bus.get_name()
        bus_list = []
        bus_list.append(self._get_urn_from_component(bus))
        for i in range(bus.get_child_count()):
            component = bus.get_child_from_index(i)
            #print "component: %s" % component.get_name()
            if isinstance(component, SOMBus):
                #print "Found bus!"
                bus_list.extend(self._get_bus_list(component))
            if component.get_component().is_synthesis_record():
                continue
            if component.get_component().is_integration_record():
                continue
            if component.get_component().is_url_record():
                continue
            bus_list.append(self._get_urn_from_component(component))
        return bus_list

    def _get_component_from_urn(self, urn):
        ls = urn.split("/")
        name_list = []

        for l in ls:
            if len(l) > 0:
                name_list.append(l)

        root = self.som.get_root()
        #print "ls: %s" % str(ls)

        # If user set URN to "/"
        if len(name_list) == 0:
            return root

        if (len(name_list) == 1) and (name_list[0] != root.get_name()):
            raise SDBError("Could not find Component from URN: %s" % urn)

        return self._get_component_from_bus_urn(root, name_list[1:])

    def _get_component_from_bus_urn(self, bus, name_list):
        #User has asked for a bus
        if len(name_list) == 0:
            return bus

        #Go through all the sub components.
        for child in bus:
            if child.get_name() == name_list[0]:
                #If the name is bus then go deeper
                if isinstance(child, SOMBus):
                    return self._get_component_from_bus_urn(child, name_list[1:])
                #else the device is a component
                return child

    def get_number_of_devices(self):
        """
        Return the number of devices in the SDB Bus

        Args:
            Nothing

        Returns:
            (Integer) Number of devices on the SDB Bus

        Raises:
            Nothing
        """
        urns = self.get_all_devices_as_urns()
        return len(urns)

    def get_number_of_components(self):
        """
        Return the number of devices in the SDB Bus

        Args:
            Nothing

        Returns:
            (Integer) Number of devices on the SDB Bus

        Raises:
            Nothing
        """
        urns = self.get_all_components_as_urns()
        return len(urns)

    def _find_component_from_func(self, bus, func, args):
        #Check Bus First

        if func(bus.get_component(), args):
            return self._get_urn_from_component(bus)

        #Check Each of the children
        for child in bus:
            if isinstance(child, SOMBus):
                #This child is a bus, go to the next recursive level
                return self._find_component_from_func(child, func, args)
            #this is a child
            elif func(child.get_component(), args):
                return self._get_urn_from_component(child)

    def _find_device_from_ids(self, c, args):
        """Private function called with all devices"""
        vendor_id = args[0]
        product_id = args[1]
        if vendor_id is not None:
            #print "\tChecking: 0x%016X and 0x%016X" % (c.get_vendor_id_as_int(), vendor_id)
            if c.get_vendor_id_as_int() != vendor_id:
                return False
        if product_id is not None:
            #print "\tChecking: 0x%08X and 0x%08X" % (c.get_device_id_as_int(), product_id)
            if c.get_device_id_as_int() != product_id:
                return False
        return True

    def find_device_from_ids(self, vendor_id = None, product_id = None):
        """
        Returns the URN of the device with the given vendor and or product ID

        Args:
            vendor_id (None or Integer): the vendor id number of the device
            product_id (None or Integer): the product id number of the device

        Returns:
            (String): URN of the device of the form:
            /top/peripherals/gpio1

        Raises:
            SDBError: device isn't found
        """
        return self._find_component_from_func(self.som.get_root(), self._find_device_from_ids, (vendor_id, product_id))

    def _find_device_from_address(self, c, args):
        """Private function called with all devices"""
        address = args[0]
        #print "Address: 0x%016X:0x%016X" % (address, c.get_start_address_as_int())
        if address == c.get_start_address_as_int():
            return True
        return False

    def find_device_from_address(self, address):
        """
        Returns the URN of the device with the given address

        Args:
            address (Integer): the absolute base address of the device

        Returns:
            (String): URN of the device of the form:
            /peripherals/gpio1

        Raises:
            SDBError: device isn't found
        """
        return self._find_component_from_func(self.som.get_root(), self._find_device_from_address, (address,))

    def _find_device_from_abi(self, c, args):
        clazz = args[0]
        major = args[1]
        minor = args[2]

        if clazz is not None:
            if clazz != c.get_abi_class_as_int():
                return False

        if major is not None:
            if major != c.get_abi_version_major_as_int():
                return False

        if minor is not None:
            if minor != c.get_abi_version_minor_as_int():
                return False

        return True

    def find_device_from_abi(self, abi_class = 0, abi_major = None, abi_minor = None):
        """
        Returns the URN of the device with the given address

        Args:
            abi_class (Nothing/Integer): class of the device, note abi_class has
                not been formally defined and this function may change for the
                future
            abi_major: (Nothing/Integer): major number of the device, refer to
                to the device list to find the associated number of a device
            abi_minor: (Nothing/Integer): minor nuber of the device, refer to
                the device list to find the associated number of a device

        Returns:
            (String): URN of the device of the form:
            /peripherals/gpio1

        Raises:
            SDBError: device isn't found
        """
        return self._find_component_from_func(self.som.get_root(), self._find_device_from_abi, (abi_class, abi_major, abi_minor,))

    def read_sdb(self, n):
        """
        Reads the SDB of the device, this is used to initialize the SDB Object
        Model with the content of the SDB on the host

        Args:
            n (Nysa Instance): A reference to nysa that the controller will
                use to extrapolate the SDB from the device

        Returns:
            Nothing

        Raises:
            NysaCommError: Errors associated with communication
        """
        self.s.Important("Parsing Top Interconnect Buffer")
        #Because Nysa works with many different platforms we need to get the
        #platform specific location of where the SDB actually is
        #XXX: Create this function in nysa
        sdb_base_address = n.get_sdb_base_address()
        self.som = som.SOM()
        self.som.initialize_root()
        bus = self.som.get_root()
        _parse_bus(n, self.som, bus, sdb_base_address, sdb_base_address, self.s)

    def is_wishbone_bus(self, urn = None):
        """
        Returns true if the SDB bus is a wishbone bus

        Args:
            urn (None/String): Absolute reference to the bus
                leave blank for root

        Returns (Boolean):
           True: Is a wishbone bus
           False: Not a wishbone bus

        Raises:
            Nothing
        """
        c = None
        if urn is None:
            c = self.som.get_root().get_component()
        else:
            component = self._get_component_from_urn(urn)
            if not isinstance(component, SOMBus):
                component = component.get_parent()
            c = component.get_component()

        return c.get_bus_type_as_int() == 0

    def is_axi_bus(self, urn = None):
        """
        Returns true if the SDB bus is an axi bus

        Args:
            urn (None/String): Absolute reference to the bus
                leave blank for root

        Returns (Boolean):
           True: Is an axi bus
           False: Not an axi bus

        Raises:
            Nothing
        """

        raise AssertionError("AXI bus not implemented yet")

    def is_storage_bus(self, urn = None):
        """
        Returns true if the SDB bus is a storage bus

        Args:
            urn (None/String): Absolute reference to the bus
                leave blank for root

        Returns (Boolean):
           True: Is a storage bus
           False: Not a storage bus

        Raises:
            Nothing
        """
        c = None
        if urn is None:
            c = self.som.get_root().get_component()
        else:
            component = self._get_component_from_urn(urn)
            if not isinstance(component, SOMBus):
                component = component.get_parent()
            c = component.get_component()

        return c.get_bus_type_as_int() == 1

    #Device Functions
    def _verify_functional_device(self, component, error_name):
        if  component.is_synthesis_record():
            raise SDBError("Synthesis Record does not have an %s: %s" % (error_name, component))

        if component.is_integration_record():
            raise SDBError("Integration Record does not have an %s: %s" % (error_name, component))

        if component.is_url_record():
            raise SDBError("URL Record does not have an %s: %s" % (error_name, component))

    def get_device_address(self, urn):
        """
        Return the address of the device

        Args:
            urn (String): Absolute reference to the bus

        Returns (Long)
            Base address of the device or interconnect

        Raises:
            SDBError: User attempted to get the address of a synthesis record
            SDBError: User attempted to get the address of a URL record
            SDBError: User attempted to get the address of an integration record
        """
        component = self._get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Address")
        return component.get_start_address_as_int()

    def get_device_size(self, urn):
        """
        Return the size of the device

        Args:
            urn (String): Absolute reference to the bus

        Returns (Integer)
            Size of the device or interconnect

        Raises:
            SDBError: User attempted to get the size of a synthesis record
            SDBError: User attempted to get the size of a URL record
            SDBError: User attempted to get the size of an integration record
        """
        component = self._get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Size")
        return component.get_size_as_int()

    def get_device_vendor_id(self, urn):
        """
        Return the vendor id of the device

        Args:
            urn (String): Absolute reference to the bus

        Returns (Integer)
            Size of the device or interconnect

        Raises:
            SDBError: User attempted to get the vendor id of a synthesis record
            SDBError: User attempted to get the vendor id of a URL record
            SDBError: User attempted to get the vendor id of an integration record
        """

        component = self._get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Vendor ID")
        return component.get_vendor_id_as_int()

    def get_device_product_id(self, urn):
        """
        Return the product id of the device

        Args:
            urn (String): Absolute reference to the bus

        Returns (Integer)
            Size of the device or interconnect

        Raises:
            SDBError: User attempted to get the product id of a synthesis record
            SDBError: User attempted to get the product id of a URL record
            SDBError: User attempted to get the product id of an integration record
        """

        component = self._get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Product ID")
        return component.get_device_id_as_int()

    def get_device_abi_class(self, urn):
        """
        Return the ABI class of the device

        Args:
            urn (String): Absolute reference to the bus

        Returns (Integer)
            Size of the device or interconnect

        Raises:
            SDBError: User attempted to get the ABI class of a synthesis record
            SDBError: User attempted to get the ABI class of a URL record
            SDBError: User attempted to get the ABI class of an integration record
            SDBError: User attempted to get the ABI class of an interconnect
        """
        component = self._get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "ABI Class")
        if  component.is_interconnect():
            raise SDBError("Interconnects do not have an ABI Class: %s" % component)
        return component.get_abi_class_as_int()

    def get_device_abi_major(self, urn):
        """
        Return the ABI major number of the device

        Args:
            urn (String): Absolute reference to the bus

        Returns (Integer)
            Size of the device or interconnect

        Raises:
            SDBError: User attempted to get the ABI major number of a synthesis record
            SDBError: User attempted to get the ABI major number of a URL record
            SDBError: User attempted to get the ABI major number of an integration record
            SDBError: User attempted to get the ABI major number of an interconnect
        """

        component = self._get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "ABI Major")
        if  component.is_interconnect():
            raise SDBError("Interconnects do not have an ABI Major: %s" % component)
        return component.get_abi_version_major_as_int()

    def get_device_abi_minor(self, urn):
        """
        Return the ABI minor number of the device

        Args:
            urn (String): Absolute reference to the bus

        Returns (Integer)
            Size of the device or interconnect

        Raises:
            SDBError: User attempted to get the ABI minor number of a synthesis record
            SDBError: User attempted to get the ABI minor number of a URL record
            SDBError: User attempted to get the ABI minor number of an integration record
            SDBError: User attempted to get the ABI minor number of an interconnect
        """

        component = self._get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "ABI Minor")
        if  component.is_interconnect():
            raise SDBError("Interconnects do not have an ABI Minor: %s" % component)
        return component.get_abi_version_minor_as_int()

    def is_bus(self, urn):
        """
        Returns True if the urn is referencing a component that is a bus

        Args:
            urn (String): Absolute reference to the bus

        Raises:
            SDBError: urn is not valid
        """
        return self._get_component_from_urn(urn).get_component().is_interconnect()

    def find_urn_from_device_type(self, device_name, sub_type = None):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            device_type (String): Type of device to find, 'gpio' or 'uart'
                can be searched for
            device_sub_type (None, Integer): a number to identify one version
                of the device and another

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        abi_class = 0
        abi_major = 0
        self.s.Verbose("ABI Class == 0")

        try:
            abi_major = device_manager.get_device_id_from_name(device_name)
        except SDBError as ex:
            return []
        #print "abi major: %d" % abi_major
        return self.find_urn_from_abi(abi_class, abi_major = abi_major, abi_minor = sub_type)

    def find_urn_from_abi(self, abi_class = 0, abi_major = None, abi_minor = None):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            abi_class (None, Integer): Application Binary Interface Class,
                currently most components use '0' as the class is not defined
            abi_major (None, Integer): Application Binary Interface Major Number
                the current list of abi_major numbers can be found using the
                nysa command line tool ('nysa devices')
            abi_minor (None, Integer): Applicatoin Binary Interface Minor Number
                this is an identification within the major number, used to
                distinguish one version of a device from another

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        l = []
        urns = self.get_all_components_as_urns()
        if isinstance(abi_major, str):
            abi_major = device_manager.get_device_id_from_name(abi_major)
        for urn in urns:
            if self.is_bus(urn):
                continue
            abi_class_test = self.get_device_abi_class(urn)
            abi_major_test = self.get_device_abi_major(urn)
            abi_minor_test = self.get_device_abi_minor(urn)
            if abi_class is not None:
                if abi_class_test != abi_class:
                    continue
            if abi_major is not None:
                if abi_major_test != abi_major:
                    continue
            if abi_minor is not None:
                if abi_minor_test != abi_minor:
                    continue
            #l.append(self._get_component_from_urn(urn).get_component())
            l.append(urn)
        return l

    def find_urn_from_ids(self, vendor_id = None, product_id = None):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            vendor_id (None, Integer): Vendor Identification number
            product_id(None, Integer): Product Identification number

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        l = []
        urns = self.get_all_components_as_urns()
        for urn in urns:
            if self.is_bus(urn):
                continue
            vendor_id_test = self.get_device_vendor_id(urn)
            product_id_test = self.get_device_product_id(urn)
            if vendor_id is not None:
                if vendor_id_test != vendor_id:
                    continue
            if product_id is not None:
                if product_id_test != product_id:
                    continue
            #l.append(self._get_component_from_urn(urn).get_component())
            l.append(urn)
        return l

    #Helpful Fuctions
    def is_memory_device(self, urn):
        memory_major = device_manager.get_device_id_from_name("memory")
        return self.get_device_abi_major(urn) == memory_major

    def get_total_memory_size(self):
        urns = self.find_urn_from_device_type("memory")
        size = 0
        for urn in urns:
            size += self.get_device_size(urn)
        return size

    def pretty_print_sdb(self):
        self.s.Verbose("pretty print SDB")
        self.s.PrintLine("SDB ", color = "blue")
        #self.som
        root = self.som.get_root()
        self._print_bus(root, depth = 0)

    def _print_bus(self, bus, depth = 0):
        c = bus.get_component()
        for t in range(depth):
            self.s.Print("\t")
        s = "Bus: {0:<10} @ 0x{1:0=16X} : Size: 0x{2:0=8X}".format(bus.get_name(), c.get_start_address_as_int(), c.get_size_as_int())
        self.s.PrintLine(s, "purple")

        for i in range(bus.get_child_count()):
            c = bus.get_child_from_index(i)
            if self.som.is_entity_a_bus(bus, i):
                self._print_bus(c, depth = depth + 1)
            else:
                c = bus.get_child_from_index(i)
                c = c.get_component()
                major = c.get_abi_version_major_as_int()
                minor = c.get_abi_version_minor_as_int()
                dev_name = device_manager.get_device_name_from_id(major)
                for t in range(depth + 1):
                    self.s.Print("\t")
                s = "{0:20} Type (Major:Minor) ({1:0=2X}:{2:0=2X}): {3:10}".format(c.get_name(),
                                                   major,
                                                   minor,
                                                   dev_name)

                self.s.PrintLine(s, "green")
                for t in range(depth + 1):
                    self.s.Print("\t")
                s = "Address:        0x{0:0=16X}-0x{1:0=16X} : Size: 0x{2:0=8X}".format(c.get_start_address_as_int(),
                                                                    c.get_end_address_as_int(),
                                                                    c.get_size_as_int())
                self.s.PrintLine(s, "green")
                for t in range(depth + 1):
                    self.s.Print("\t")
                s = "Vendor:Product: {0:0=16X}:{1:0=8X}".format(c.get_vendor_id_as_int(),
                                                                c.get_device_id_as_int())

                self.s.PrintLine(s, "green")
                self.s.PrintLine("")


def _parse_bus(n, som, bus, addr, base_addr, status):
    #The first element at this address is the interconnect
    status.Verbose("Bus @ 0x%08X" % addr)
    entity_rom = n.read(addr, SDB_ROM_RECORD_LENGTH / 4)
    #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
    bus_entity = srp.parse_rom_element(entity_rom)
    if not bus_entity.is_interconnect():
        raise SDBError("Rom data does not point to an interconnect")
    num_devices = bus_entity.get_number_of_records_as_int()
    status.Verbose("\tFound %d Devices" % num_devices)
    som.set_bus_component(bus, bus_entity)
    #print "Found bus: %s" % bus_entity.get_name()

    entity_size = []
    entity_addr_start = []

    for i in range(1, (num_devices + 1)):
        I = (i * (SDB_ROM_RECORD_LENGTH / 4)) + addr
        entity_rom = n.read(I, SDB_ROM_RECORD_LENGTH / 4)
        #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
        entity = srp.parse_rom_element(entity_rom)
        end = long(entity.get_end_address_as_int())
        start = long(entity.get_start_address_as_int())
        entity_addr_start.append(start)
        entity_size.append(end - start)

        if entity.is_bridge():
            #print "Found bridge"
            sub_bus = som.insert_bus(root = bus,
                                     name = entity.get_name())
            sub_bus_addr = entity.get_bridge_address_as_int() * 2 + base_addr
            _parse_bus(n, som, sub_bus, sub_bus_addr, base_addr, status)
        else:
            som.insert_component(root = bus, component = entity)
            status.Verbose("Found device %s Type (0x%02X): %s" % (
                                            entity.get_name(),
                                            entity.get_abi_version_major_as_int(),
                                            device_manager.get_device_name_from_id(entity.get_abi_version_major_as_int())))
            #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))

    #Calculate Spacing
    spacing = 0
    prev_start = None
    prev_size = None
    for i in range (num_devices):
        size = entity_size[i]
        start_addr = entity_addr_start[i]
        if prev_start is None:
            prev_size = size
            prev_start = start_addr
            continue

        potential_spacing = (start_addr - prev_start)
        if potential_spacing > prev_size:
            if potential_spacing > 0 and spacing == 0:
                spacing = potential_spacing
            if spacing > potential_spacing:
                spacing = potential_spacing

        prev_size = size
        prev_start = start_addr

    som.set_child_spacing(bus, spacing)

def print_sdb_rom(rom):
    #rom = sdbc.convert_rom_to_32bit_buffer(rom)
    rom = rom.splitlines()
    print "ROM"
    for i in range (0, len(rom), 4):
        if (i % 16 == 0):
            magic = "0x%s" % (rom[i].lower())
            last_val = int(rom[i + 15], 16) & 0xFF
            print ""
            if (magic == hex(sdbc.SDB_INTERCONNECT_MAGIC) and last_val == 0):
                print "Interconnect"
            elif last_val == 0x01:
                print "Device"
            elif last_val == 0x02:
                print "Bridge"
            elif last_val == 0x80:
                print "Integration"
            elif last_val == 0x81:
                print "URL"
            elif last_val == 0x82:
                print "Synthesis"
            elif last_val == 0xFF:
                print "Empty"
            else:
                print "???"

        print "%s %s : %s %s" % (rom[i], rom[i + 1], rom[i + 2], rom[i + 3])

