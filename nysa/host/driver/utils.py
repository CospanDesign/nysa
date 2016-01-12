

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

