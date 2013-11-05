

"""Flash Object to be inherited"""
class SerialFlash(object):
    """Interface of a generic SPI flash device"""
    FEAT_NONE = 0x000         # No special feature
    FEAT_LOCK = 0x001         # Basic, revertable locking
    FEAT_INVLOCK = 0x002      # Inverted (bottom/top) locking
    FEAT_SECTLOCK = 0x004     # Arbitrary sector locking
    FEAT_OTPLOCK = 0x008      # OTP locking available
    FEAT_UNIQUEID = 0x010     # Unique ID
    FEAT_SECTERASE = 0x100    # Can erase whole sectors
    FEAT_HSECTERASE = 0x200   # Can erase half sectors
    FEAT_SUBSECTERASE = 0x400 # Can erase sub sectors

    def read(self, address, length):
        """Read a sequence of bytes from the specified address."""
        raise NotImplementedError()

    def write(self, address, data):
        """Write a sequence of bytes, starting at the specified address."""
        raise NotImplementedError()

    def erase(self, address, length):
        """Erase a block of bytes. Address and length depends upon device-
           specific constraints."""
        raise NotImplementedError()

    def can_erase(self, address, length):
        """Tells whether a defined area can be erased on the Spansion flash
           device. It does not take into account any locking scheme."""
        raise NotImplementedError()

    def is_busy(self):
        """Reports whether the flash may receive commands or is actually
           being performing internal work"""
        raise NotImplementedError()

    def get_capacity(self):
        """Get the flash device capacity in bytes"""
        raise NotImplementedError()

    def get_capabilities(self):
        """Flash device capabilities."""
        return SerialFlash.FEAT_NONE

    def get_locks(self):
        """Report the currently write-protected areas of the device."""
        raise NotImplementedError()

    def set_lock(self, address, length, otp=False):
        """Create a write-protected area. Device should have been unlocked
           first."""
        raise NotImplementedError()

    def unlock(self):
        """Make the whole device read/write"""
        pass

    def get_unique_id(self):
        """Return the unique ID of the flash, if it exists"""
        raise NotImplementedError()


