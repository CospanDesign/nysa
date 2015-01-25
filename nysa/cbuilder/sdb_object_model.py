#! /usr/bin/python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa.
# (http://wiki.cospandesign.com/index.php?title=Nysa.org)
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

import sdb_component
from sdb_component import SDBComponent as sdbc
from sdb_component import is_valid_bus_type

from sdb import SDBInfo
from sdb import SDBWarning
from sdb import SDBError



class SOMComponent(object):

    def __init__(self, parent, c):
        self.parent = parent
        self.c = c

    def get_component(self):
        return self.c

    def get_parent(self):
        return self.parent

    def get_name(self):
        return self.c.get_name()

    def set_name(self, name):
        self.c.set_name(name)

class SOMBus(SOMComponent):

    def __init__(self, parent):
        self.spacing = 0
        self.children = []
        super(SOMBus, self).__init__(parent, sdbc())
        self.c = sdb_component.create_interconnect_record( name = "bus",
                                                  vendor_id = 0x800000000000C594,
                                                  device_id = 0x00000001,
                                                  start_address = 0x00,
                                                  size = 0x00)
        self.curr_pos = 0

    def insert_child(self, child, pos = -1):
        if pos == -1:
            self.children.append(child)
        else:
            self.children.insert(pos, child)
        size = 0
        for child in self.children:
            size += child.c.get_size_as_int()

        self.c.set_size(size)

    def get_child_from_index(self, i):
        return self.children[i]

    def remove_child_at_index(self, i):
        child = self.children[i]
        self.remove_child(child)

    def remove_child(self, child):
        self.children.remove(child)
        size = 0
        for child in self.children:
            size += child.c.get_size_as_int()

        self.c.set_size(size)

    def get_child_count(self):
        return len(self.children)

    def is_root(self):
        return False

    def get_component(self):
        return self.c

    def set_child_spacing(self, spacing = 0):
        """
        sets the spacing of the children within a bus, by default this is zero
        which means the children will be put right after each other, however
        if this value is set to a larger number such as 0x01000000 then every
        child start address will start on a 0x01000000 boundary as an example:

        child 0 @ 0x00000000
        child 1 @ 0x01000000
        child 2 & 0x02000000

        Args:
            spacing (integer): start spacing of a child in the bus

        Return:
            Nothing

        Raises:
            Nothing
        """
        #import pdb
        #pdb.set_trace()
        self.spacing = spacing

    def get_child_spacing(self):
        """
        Returns the minimum spacing between children start address

        Args:
            Nothing

        Returns (integer):
            spacing between start address of children

        Raises:
            Nothing
        """
        return self.spacing

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        self.curr_pos = 0
        return self

    def next(self):
        if self.curr_pos == len(self.children):
            raise StopIteration
        pos = self.curr_pos
        self.curr_pos += 1
        return self.children[pos]

class SDBRoot(SOMBus):

    def __init__(self):
        super(SDBRoot, self).__init__(None)
        self.c.d["SDB_NAME"] = "Root"

    def is_root(self):
        return True


#User Facing Object
class SOM(object):

    def __init__(self, status):
        self.s = status
        self.root = None
        self.reset_som()
        self.current_rot = self.root
        self.current_pos = 0

    #Bus Functions
    def initialize_root(self,
                                name = "top",
                                version = sdbc.SDB_VERSION,
                                vendor_id = 0x8000000000000000,
                                entity_id = 0x00000000,
                                bus_type = "wishbone"):

        c = self.root.get_component()
        c.d["SDB_NAME"] = name
        if version > sdbc.SDB_VERSION:
            raise SDBError("Version %d is greater than known version! (%d)" %
                            (version,
                            sdbc.SDB_VERSION))
        c.d["SDB_VERSION"] = version

        if not is_valid_bus_type(bus_type):
            raise SDBError("%s is not a valid bus type" % bus_type)
        c.d["SDB_BUS_TYPE"] = "wishbone"

    def get_root(self):
        """
        Returns the root of the bus

        Args:
            Nothing

        Returns:
            (SOMBus): the base bus of the SOM

        Raises:
            Nothing
        """
        return self.root

    def get_buses(self, root = None):
        """
        Returns a list of buses that are underneath the provided root

        Args:
            (SOMBus): The root bus to retrieve the sub buses from

        Returns: (Tuple of SOMBus)

        Raises:
            Nothing
        """
        if root is None:
            root = self.root

        bus_list = []
        for i in range(root.get_child_count()):
            child = root.get_child_from_index(i)
            if isinstance(child, SOMBus):
                bus_list.append(child)


        return tuple(bus_list)

    def is_entity_a_bus(self, root = None, index = None):
        """
        Returns true if the entity at the specified index is a bus

        Args:
            root(SOMBus): The bus where the devcies are
                leave blank for the top of the tree
            index(Integer): The index of the entity within the root bus

        Return (Boolean):
            True: entity is a bus
            False: entity is not a bus

        Raises:
            SDBError:
                index is not supplied
        """
        if index is None:
            raise SDBError("index is None, this should be an integer")

        if root is None:
            root = self.root

        n = root.get_child_from_index(index)
        if isinstance(n, SOMBus):
            return True

        return False

    def insert_bus(self,
                    root = None,
                    name = None,
                    bus = None,
                    pos = -1):
        """
        Add a new bus into the SDB Network, if the user supplies the root
        then the new item will be inserted into the root bus otherwise
        insert it into the bus provided.

        The name of the bus can be set initially or later

        Args:
            root(SOMBus): the bus where this new bus will be added

            name(String): Name of the bus to add, could be left blank
            start_address(integer): where to add this bus relative to the
                above bus
            bus(SOMBus): a SOM Bus this can be used to add a pre-existing bus
            pos(integer): position of where to put bus, leave blank to put it
            at the end

        Return:
            (SOMBus): The branch element returned to the user for
                use in adding more element
        """
        if root is None:
            root = self.root

        if bus is None:
            bus = SOMBus(root)

        c = bus.get_component()

        if name is not None:
            c.d["SDB_NAME"] = name

        #if start_address is not None:
        #    self.c.set_start_address(start_address)

        root.insert_child(bus, pos)
        self._update()
        return bus

    def remove_bus(self, bus):
        """
        Remove a bus from the SOM

        Args:
            bus (SOMBus): bus to remove

        Return (SOMBus):
            An orphaned SOMBus

        Raises:
            SOMError:   User attempted to remove root
                        User attempted to remove non-existent bus
        """
        parent = bus.get_parent()
        if parent is None:
            raise SDBError("Cannot remove root, use reset_som to reset SOM")
        try:
            parent.remove_child(bus)
        except ValueError as ex:
            raise SDBError("Attempted to remove a non-existent bus from a "\
                            "parent bus: Parent Bus: %s, Child Bus: %s" %
                            parent.c.d["SDB_NAME"],
                            bus.c.d["SDB_NAME"])

    def set_bus_name(self, bus, name):
        """
        Names the bus

        Args:
            bus (SOMBus): bus to rename
            name (String): name

        Return:
            Nothing

        Raises:
            SDBError: bus does not exist
        """
        if bus is None:
            raise SDBError("Bus doesn't exist")

        elif not isinstance(bus, SOMBus):
            raise SDBError("Bus is not an SOMBus")

        c = bus.get_component()
        c.set_name(name)

    def get_bus_name(self, bus):
        """
        Returns the name of the bus

        Args:
            bus (SOMBus): bus

        Return:
            Nothing

        Raises:
            SOBError: bus does not exist
        """
        if bus is None:
            raise SDBError("Bus doesn't exist")

        elif not isinstance(bus, SOMBus):
            raise SDBError("Bus is not an SOMBus")

        return bus.get_component().get_name()

    #Bus Private Functions

    #Component Entity Functions
    def insert_component(self, root = None, component = None, pos = -1):
        """
        insert a new component into a bus, if root is left empty then
        insert this component into the root

        Args:
            root(SOMBus): The bus where this component should
                be located
            component(SDBComponent): the element in which to add this
                component into
                This component can only be a entity, or informative item
            pos(integer): the location where to put the component, leave blank
                for the end

        Return
            (SOMComponent): the generated SOMComponent is already inserted into
            the tree

        Raises:
            Nothing
        """
        if root is None:
            #print "root is None, Using base root!"
            root = self.root
        else:
            #print "Using custom root..."
            #print ""
            #print ""
            pass

        #Extrapolate the size of the component
        if component.is_interconnect() or component.is_bridge():
            raise SDBError("Only component can be inserted, not %s", component)

        leaf = SOMComponent(root, component)
        root.insert_child(leaf, pos)
        self._update()

    def get_component(self, root = None, index = None):
        """
        Returns a component that represents an SDB Component

        This does not return interconnects or bridges

        Args:
            root (SOMBus): bus for the entitys
                leave blank for the top of the tree

        Return (SDBComponent): Returns the comopnent
            at the index specified on the specified bus

        Raises:
            None
        """
        if root is None:
            root = self.root

        child = root.get_child_from_index(index)
        component = child.get_component()
        return component

    def remove_component_by_index(self, root = None, index = -1):
        """
        Removes a component given it's root and index

        Args:
            root (SOMBus): bus for the entity, leave blan for root
            index (integer): index of item on bus

        Returns:
            Nothing

        Raises:
            ValueError: Component not found
        """
        if root is None:
            root = self.root

        child = root.get_child_from_index(index)
        return self._remove_component(child)

    def move_component(self, from_root, from_index, to_root, to_index):
        """
        Move a component to another location in the SDB

        Args:
            from_root (SOMBus): bus where the component is located
            from_index (integer): index of where to get the item
            to_root (SOMBus): bus where to put the component
            to_index (integer): index of where to put the item

        Returns:
            Nothing

        Raises:
            Value Error: Component not found
        """
        som_component = self.remove_component_by_index(from_root, from_index)
        component = som_component.get_component()
        self.insert_component(to_root, component, to_index)

    #Component Private Functions
    def _remove_component(self, som_component):
        """
        Remove a component from the SOM

        Args:
            component (SDBComponent)

        Returns:
            Nothing

        Raises:
            ValueError: Not found in bus
        """
        parent = som_component.get_parent()
        parent.remove_child(som_component)
        self._update()
        return som_component

    #Utility Functions
    def reset_som(self):
        self.root = SDBRoot()

    def get_child_count(self, root = None):
        """
        Return a count of the children of a specified node

        Args:
            root(SOMBus): the bus where the entitys are
                leave blank for the top of the tree

        Return (integer): number of entitys in a bus

        Raises:
            Nothing
        """
        if root is None:
            root = self.root

        return root.get_child_count()

    #Private Functions
    def _update(self, root = None):
        """
        Go through the entire tree updating all buses with the appropriate sizes
        from all the elements

        Args:
            Nothing

        Return:
            Nothing

        Raises:
            Nothing
        """
        if root is None:
            root = self.root
        else:
            #print "Updating root that is not base!"
            #print ""
            #print ""
            pass


        bus_size = 0
        rc = root.get_component()
        start_address = rc.get_start_address_as_int()
        spacing = root.get_child_spacing()

        '''
        #Bubble sort everything
        for i in range(root.get_child_count()):
            prev_child = None
            for j in range(root.get_child_count()):
                child = root.get_child_from_index(j)
                if prev_child is None:
                    prev_child = child
                    continue
                if child.c.get_start_address_as_int() < prev_child.c.get_start_address_as_int():
                    #print "Reordering children"
                    root.remove_child_at_index(j)
                    root.insert_child(child, j - 1)

                prev_child = child

        print "Sorted Children:"
        for i in range(root.get_child_count()):
            child = root.get_child_from_index(i)
            print "\tchild %s: 0x%02X" % (child.c.d["SDB_NAME"], child.c.get_start_address_as_int())
        '''

        #Move all informative elements to the end of the bus
        #Bubble sort all non informative elements to the front of informative
        #   elements
        for i in range(root.get_child_count()):
            prev_child = None
            for j in range(root.get_child_count() - 1, -1, -1):
                child = root.get_child_from_index(j)
                if prev_child is None:
                    prev_child = child
                #print "Comparing..."
                #print "child is an integration record: %s" % str(child.c.is_integration_record())
                if  child.c.is_integration_record() or child.c.is_synthesis_record() or child.c.is_url_record():
                    root.remove_child_at_index(j)
                    root.insert_child(child, j + 1)

                prev_child = child



        #Adjust all the sizes for the busses
        prev_child = None
        for i in range(root.get_child_count()):
            child = root.get_child_from_index(i)
            c = child.get_component()
            if prev_child is None:
                #First child should always be 0 relative to this bus
                c.set_start_address(0x00)
                prev_child = child
                if isinstance(child, SOMBus):
                    #print "Found bus, initate recursive update"
                    self._update(child)

                #Bus Size
                bus_size = c.get_start_address_as_int() + c.get_size_as_int()
                #print "bus size: 0x%08X" % bus_size
                if spacing > 0:
                    if (bus_size % spacing) > 0:
                        bus_size += (bus_size * spacing)
                continue

            pc = prev_child.get_component()
            spacing_size = 0
            if isinstance(child, SOMBus):
                #print "Found bus, initate recursive update"
                self._update(child)

            prev_start_address = pc.get_start_address_as_int()
            prev_child_size = pc.get_size_as_int()

            #current_start_address = c.get_start_address_as_int()

            #Add an extra spacing size so that all divided values will at least
            #be one
            spacing_size = prev_child_size + spacing
            if spacing > 0:
                increment = (prev_child_size + spacing) / spacing
                spacing_size = increment * spacing

            new_child_start_address = prev_start_address + spacing_size
            #if current_start_address < new_child_start_address:
            c.set_start_address(new_child_start_address)
            prev_child = child

            bus_size = c.get_start_address_as_int() + c.get_size_as_int()
            if spacing_size > 0:
                if (bus_size % spacing_size) > 0:
                    bus_size = (bus_size * spacing_size)

        c = root.get_component()
        c.set_size(bus_size)
        #print "bus size: %d" % bus_size
        c.set_number_of_records(root.get_child_count())


        #Debug
        '''
        print "Final Children Order:"
        for i in range(root.get_child_count()):
            child = root.get_child_from_index(i)
            print "\tchild %s: 0x%02X" % (child.c.d["SDB_NAME"], child.c.get_start_address_as_int())
        '''


