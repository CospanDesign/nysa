from array import array as Array

def is_bit_set(value, bit):
    if (value & (1 << bit)) > 0:
        return True
    return False

def get_value_in_range(value, high_bit, low_bit):
    bitmask = (((1 << (high_bit + 1))) - (1 << low_bit))
    value &= bitmask
    value = value >> low_bit
    return value

def list_to_hex_string(a):
    s = None
    for i in a:
        if s is None:
            s = "["
        else:
            s += ", "

        s += "0x%02X" % i

    s += "]"
    return s


def dword_to_array(value):
    out = Array('B')
    out.append((value >> 24) & 0xFF)
    out.append((value >> 16) & 0xFF)
    out.append((value >>  8) & 0xFF)
    out.append((value >>  0) & 0xFF)
    return out

def array_to_dword(a):
    return (a[0] << 24) | (a[1] << 16) | (a[2] << 8) | a[3]
