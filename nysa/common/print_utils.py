
def print_32bit_hex_array(hex_array):
    for i in range (0, len(hex_array), 4):
        print ("[8][{0:>4}] [32][{1:>4}]: {2:02X} {3:02X} {4:02X} {5:02X}".format(i, (i / 4), hex_array[i], hex_array[i + 1], hex_array[i + 2], hex_array[i + 3]))


