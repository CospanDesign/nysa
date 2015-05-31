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

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from array import array as Array
from common.status import Status

from cbuilder.sdb import SDBError

from cbuilder.sdb_component  import SDB_ROM_RECORD_LENGTH

from cbuilder.sdb_object_model import SOMRoot
from cbuilder.sdb_object_model import SOMBus

from cbuilder import sdb_object_model as som
from cbuilder import sdb_component as sdbc
from cbuilder import som_rom_parser as srp
from cbuilder import device_manager
from host.driver.driver import Driver

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
            c = self.get_component_from_urn(c_urn)
            if isinstance(c, SOMBus):
                continue
            d_urns.append(c_urn)

        return d_urns

    def _get_component_index(self, component):
        parent = component.get_parent()
        index = 0
        for c in parent:
            if component == c:
                return index
            index += 1
        return index

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

    def get_component_from_urn(self, urn):
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

    def find_device_from_driver(self, driver):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            device (Driver Object): Type of device to find, a subclass of the
                driver object

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        l = []
        urns = self.get_all_components_as_urns()
        driver_abi_class = driver.get_abi_class()
        driver_abi_major = driver.get_abi_major()
        driver_abi_minor = driver.get_abi_minor()
        driver_vendor_id = driver.get_vendor_id()
        driver_device_id = driver.get_device_id()
        driver_version = driver.get_version()
        driver_date = driver.get_date()

        if isinstance(driver_abi_major, str):
            driver_abi_major= device_manager.get_device_id_from_name(driver_abi_major)
        for urn in urns:
            if self.is_bus(urn):
                continue

            device_abi_class = self.get_device_abi_class(urn)
            device_abi_major = self.get_device_abi_major(urn)
            device_abi_minor = self.get_device_abi_minor(urn)
            device_vendor_id = self.get_device_vendor_id(urn)
            device_device_id = self.get_device_product_id(urn)
            device_version = self.get_device_version(urn)
            device_date = self.get_device_date(urn)

            if driver_abi_class is not None:
                if driver_abi_class != device_abi_class:
                    continue
            if driver_abi_major is not None:
                if driver_abi_major != device_abi_major:
                    continue
            if driver_abi_minor is not None:
                if driver_abi_minor != device_abi_minor:
                    continue
            if driver_vendor_id is not None:
                if driver_vendor_id != device_vendor_id:
                    continue
            if driver_device_id is not None:
                if driver_device_id != device_device_id:
                    continue
            if driver_version is not None:
                if driver_version != device_version:
                    continue
            if driver_date is not None:
                if driver_date != device_date:
                    continue

            l.append(urn)
        return l

    def get_device_index_in_bus(self, urn):
        """
        Return the index of the device in the parent bus

        Args:
            urn (string): Unique Reference Name identifying the device

        Returns: (Integer)
            index of the device in the peripheral in the bus

        Raises:
            Nothing
        """
        component = self.get_component_from_urn(urn)
        return self._get_component_index(component)

    def read_sdb(self, n):
        """
        Reads the SDB of the device, this is used to initialize the SDB Object
        Model with the content of the SDB on the host

        Args:
            n (Nysa Instance): A reference to nysa that the controller will
                use to extrapolate the SDB from the device

        Returns:
            Array of bytes consisting of SDB

        Raises:
            NysaCommError: Errors associated with communication
        """
        sdb_data = Array('B')
        self.s.Important("Parsing Top Interconnect Buffer")
        #Because Nysa works with many different platforms we need to get the
        #platform specific location of where the SDB actually is
        sdb_base_address = n.get_sdb_base_address()
        self.som = som.SOM()
        self.som.initialize_root()
        bus = self.som.get_root()
        sdb_data.extend(_parse_bus(n, self.som, bus, sdb_base_address, sdb_base_address, self.s))
        sdb_data = n.read(sdb_base_address, len(sdb_data) / 4)
        return sdb_data

    def is_wishbone_bus(self, urn = None):
        """
        Returns true if the SDB bus is a wishbone bus

        Args:
            urn (None/String): Absolute reference to the component
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
            component = self.get_component_from_urn(urn)
            if not isinstance(component, SOMBus):
                component = component.get_parent()
            c = component.get_component()

        return c.get_bus_type_as_int() == 0

    def is_axi_bus(self, urn = None):
        """
        Returns true if the SDB bus is an axi bus

        Args:
            urn (None/String): Absolute reference to the component
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
            urn (None/String): Absolute reference to the component
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
            component = self.get_component_from_urn(urn)
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

    def get_device_name(self, urn):
        """
        Returns the name of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (String)
            Name of the device

        Raises:
            SDBError: User attempted to get the name of a synthesis record
            SDBError: User attempted to get the name of a URL record
            SDBError: User attempted to get the name of an integration record
        """
        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Name")
        return component.get_name()

    def get_device_address(self, urn):
        """
        Return the address of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Long)
            Base address of the device or interconnect

        Raises:
            SDBError: User attempted to get the address of a synthesis record
            SDBError: User attempted to get the address of a URL record
            SDBError: User attempted to get the address of an integration record
        """
        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Address")
        return component.get_start_address_as_int()

    def get_device_size(self, urn):
        """
        Return the size of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Integer)
            Size of the device or interconnect

        Raises:
            SDBError: User attempted to get the size of a synthesis record
            SDBError: User attempted to get the size of a URL record
            SDBError: User attempted to get the size of an integration record
        """
        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Size")
        return component.get_size_as_int()

    def get_device_vendor_id(self, urn):
        """
        Return the vendor id of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Long)
            Vendor ID of the device or interconnect

        Raises:
            SDBError: User attempted to get the vendor id of a synthesis record
            SDBError: User attempted to get the vendor id of a URL record
            SDBError: User attempted to get the vendor id of an integration record
        """

        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Vendor ID")
        return component.get_vendor_id_as_int()

    def get_device_product_id(self, urn):
        """
        Return the product id of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Integer)
            Product ID of the device or interconnect

        Raises:
            SDBError: User attempted to get the product id of a synthesis record
            SDBError: User attempted to get the product id of a URL record
            SDBError: User attempted to get the product id of an integration record
        """

        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "Product ID")
        return component.get_device_id_as_int()

    def get_device_abi_class(self, urn):
        """
        Return the ABI class of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Integer)
            ABI Class of the device or interconnect

        Raises:
            SDBError: User attempted to get the ABI class of a synthesis record
            SDBError: User attempted to get the ABI class of a URL record
            SDBError: User attempted to get the ABI class of an integration record
            SDBError: User attempted to get the ABI class of an interconnect
        """
        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "ABI Class")
        if  component.is_interconnect():
            raise SDBError("Interconnects do not have an ABI Class: %s" % component)
        return component.get_abi_class_as_int()

    def get_device_abi_major(self, urn):
        """
        Return the ABI major number of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Integer)
            ABI Major of the device or interconnect

        Raises:
            SDBError: User attempted to get the ABI major number of a synthesis record
            SDBError: User attempted to get the ABI major number of a URL record
            SDBError: User attempted to get the ABI major number of an integration record
            SDBError: User attempted to get the ABI major number of an interconnect
        """

        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "ABI Major")
        if  component.is_interconnect():
            raise SDBError("Interconnects do not have an ABI Major: %s" % component)
        return component.get_abi_version_major_as_int()

    def get_device_abi_minor(self, urn):
        """
        Return the ABI minor number of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Integer)
            ABI Minor ID of the device or interconnect

        Raises:
            SDBError: User attempted to get the ABI minor number of a synthesis record
            SDBError: User attempted to get the ABI minor number of a URL record
            SDBError: User attempted to get the ABI minor number of an integration record
            SDBError: User attempted to get the ABI minor number of an interconnect
        """

        component = self.get_component_from_urn(urn).get_component()
        self._verify_functional_device(component, "ABI Minor")
        if  component.is_interconnect():
            raise SDBError("Interconnects do not have an ABI Minor: %s" % component)
        return component.get_abi_version_minor_as_int()

    def get_device_version(self, urn):
        """
        Return the version of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Integer)
            Version of the device or interconnect

        Raises:
            SDBError: User attempted to get the version of a synthesis record
            SDBError: User attempted to get the version of a URL record
        """
        component = self.get_component_from_urn(urn).get_component()
        if  component.is_synthesis_record():
            raise SDBError("Synthesis Record does not have an %s: %s" % ("Version", component))

        if component.is_url_record():
            raise SDBError("URL Record does not have an %s: %s" % ("Version", component))

        return component.get_version_as_int()

    def get_device_date(self, urn):
        """
        Return the Date number of the device

        Args:
            urn (String): Absolute reference to the component

        Returns (Integer)
            Date of the device or interconnect

        Raises:
            SDBError: User attempted to get the Date number of a synthesis record
            SDBError: User attempted to get the Date number of a URL record
            SDBError: User attempted to get the Date number of an integration record
            SDBError: User attempted to get the Date number of an interconnect
        """
        component = self.get_component_from_urn(urn).get_component()
        if  component.is_synthesis_record():
            raise SDBError("Synthesis Record does not have an %s: %s" % ("Version", component))

        if component.is_url_record():
            raise SDBError("URL Record does not have an %s: %s" % ("Version", component))

        return component.get_abi_version_minor_as_int()

    def is_bus(self, urn):
        """
        Returns True if the urn is referencing a component that is a bus

        Args:
            urn (String): Absolute reference to the component

        Raises:
            SDBError: urn is not valid
        """
        return self.get_component_from_urn(urn).get_component().is_interconnect()

    def find_urn_from_device_type(self, device_name, sub_type = None, abi_class = 0):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            device_type (String): Type of device to find, 'gpio' or 'uart'
                can be searched for
            device_sub_type (None, Integer): a number to identify one version
                of the device and another
            abi_class (None, Integer): A number identifying the class

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        abi_major = 0
        self.s.Verbose("ABI Class == %d" % abi_class)

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
            #l.append(self.get_component_from_urn(urn).get_component())
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
            #l.append(self.get_component_from_urn(urn).get_component())
            l.append(urn)
        return l

    def get_integration_references(self, urn):
        """
        Given a URN return a list of URNs that the integration record is
        pointing to

        Args:
            urn (String): Universal Reference Name pointing to a particular
            device

        Return (List of URNs):
            An empty list if there is no reference to the URN

        Raises:
            Nothing
        """
        self.s.Debug("From URN: %s" % urn)
        urn_references = []
        component = self.get_component_from_urn(urn)
        parent = component.get_parent()
        from_urn = None
        to_urns = []

        for c in parent:
            if c.get_component().is_integration_record():
                from_urn, to_urns = self.parse_integration_data(c)
                #print "urn: %s" % urn
                #print "From URN: %s" % from_urn
                if from_urn == urn:
                    #print "Found: %s" % from_urn
                    return to_urns
        return []

    #Helpful Fuctions
    def is_memory_device(self, urn):
        memory_major = device_manager.get_device_id_from_name("memory")
        return self.get_device_abi_major(urn) == memory_major

    def get_address_of_memory_bus(self):
        return self.get_device_address("/top/memory")

    def get_total_memory_size(self):
        urns = self.find_urn_from_device_type("memory")
        size = 0
        for urn in urns:
            size += self.get_device_size(urn)
        return size

    def parse_integration_data(self, integration):
        """
        Parses an integration record into a tuple with two parts:
            1: A URN referencing the from component
            2: A list of URNs referencing the destination component

        Args:
            A reference to a SOM Component

        Returns (Tuple):
            (From URN, List of To URNs)

        Raises:
            Nothing
        """
        component = integration.get_component()
        #Get the actual data from the integration record
        data = component.get_name().strip()
        bus = integration.get_parent()

        #got a numeric referece to the from index component
        #print "Data: %s" % data
        #print "Data: %s" % str(data.partition(":")[0])
        from_index = int(data.partition(":")[0])
        #from_component = self.som.get_component(bus, from_index)
        from_component = bus.get_child_from_index(from_index)

        #Got a URN reference of the from index component
        from_urn = self._get_urn_from_component(from_component)

        #Get a list of strings for the to indexes
        to_sindexes = data.partition(":")[2]
        to_sindexes_list = to_sindexes.split(",")
        #change all reference to the to component indexes to a list of strings
        to_indexes = []
        for sindex in to_sindexes_list:
            to_indexes.append(int(sindex))

        #Get a list of to indexes in the form of URNs
        to_urns = []
        for index in to_indexes:
            to_component = bus.get_child_from_index(index)
            #print "to urn: %d" % index
            to_urns.append(self._get_urn_from_component(to_component))

        return (from_urn, to_urns)

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
        for t in range(depth):
            self.s.Print("\t")
        self.s.PrintLine("Number of components: %d" % bus.get_child_count(), "purple")

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
    sdb_data = Array('B')
    entity_rom = n.read(addr, SDB_ROM_RECORD_LENGTH / 4)
    sdb_data.extend(entity_rom)
    status.Verbose("Bus @ 0x%08X: Name: %s" % (addr, bus.get_name()))
    #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
    try:
        bus_entity = srp.parse_rom_element(entity_rom)
    except SDBError as e:
        error =  "Error when parsing bus entry at base address: 0x%08X, addr: 0x%08X\n" % (base_addr, addr)
        error += str(e)
        raise SDBError(error)
    if not bus_entity.is_interconnect():
        raise SDBError("Rom data does not point to an interconnect")
    num_devices = bus_entity.get_number_of_records_as_int()
    status.Verbose("\tFound %d Devices" % num_devices)
    som.set_bus_component(bus, bus_entity)
    #print "Found bus: %s" % bus_entity.get_name()

    entity_size = []
    entity_addr_start = []

    for i in range(1, (num_devices + 2)):
        I = (i * (SDB_ROM_RECORD_LENGTH / 4)) + addr
        entity_rom = n.read(I, SDB_ROM_RECORD_LENGTH / 4)
        sdb_data.extend(entity_rom)
        entity = srp.parse_rom_element(entity_rom)
        #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
        end = long(entity.get_end_address_as_int())
        start = long(entity.get_start_address_as_int())
        entity_addr_start.append(start)
        entity_size.append(end - start)

        if entity.is_bridge():
            #print "Found bridge"
            status.Verbose("Found Bridge:")
            sub_bus = som.insert_bus(root = bus,
                                     name = entity.get_name())
            sub_bus_addr = entity.get_bridge_address_as_int() * 2 + base_addr
            sdb_data.extend(_parse_bus(n, som, sub_bus, sub_bus_addr, base_addr, status))
        else:
            if entity.is_empty_record():
                continue
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
    return sdb_data

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

