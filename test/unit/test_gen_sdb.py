#!/usr/bin/python

import unittest
import json
import sys
import os
import collections

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from nysa.cbuilder import sdb_component as sdbc
from nysa.ibuilder.gen_scripts import gen_sdb
from nysa.ibuilder import utils

class Test (unittest.TestCase):
    """Unit test SDB Tree"""

    def setUp(self):
        self.gs = gen_sdb.GenSDB()
        self.user_paths = utils.get_user_verilog_dir()

    def test_simple_rom(self):
        project_tags = json.loads(SIMPLE_CONFIG, object_pairs_hook = collections.OrderedDict)
        som = self.gs.gen_som(tags = project_tags, buf = "", user_paths = self.user_paths, debug = False)
        rom = self.gs.gen_rom(tags = project_tags, buf = "", user_paths = self.user_paths, debug = False)
        #print_sdb(rom)

    def test_integration_rom(self):
        project_tags = json.loads(INTEGRATION_CONFIG, object_pairs_hook = collections.OrderedDict)
        som = self.gs.gen_som(tags = project_tags, buf = "", user_paths = self.user_paths, debug = False)
        #rom = self.gs.gen_rom(tags = project_tags, buf = "", user_paths = self.user_paths, debug = False)
        #print_sdb(rom)

    def test_complex_integration_rom(self):
        project_tags = json.loads(COMPLEX_INTEGRATION_CONFIG, object_pairs_hook = collections.OrderedDict)
        som = self.gs.gen_som(tags = project_tags, buf = "", user_paths = self.user_paths, debug = False)
        rom = self.gs.gen_rom(tags = project_tags, buf = "", user_paths = self.user_paths, debug = False)
        print_sdb(rom)

def write_to_file(rom, filename):
    rom = sdbc.convert_rom_to_32bit_buffer(rom)
    f = open(filename, 'w')
    f.write(rom)
    f.close()

def print_sdb(rom):
    rom = sdbc.convert_rom_to_32bit_buffer(rom)
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



SIMPLE_CONFIG = "{                                  \
    \"BASE_DIR\":\"~/projects/ibuilder_project\",   \
    \"TEMPLATE\":\"wishbone_template.json\",        \
    \"board\":\"dionysus\",                         \
    \"SLAVES\":{                                    \
        \"gpio1\":{                                 \
            \"filename\":\"wb_gpio.v\",             \
            \"unique_id\":1                         \
        }                                           \
    },                                              \
    \"MEMORY\":{                                    \
        \"mem1\":{                                  \
            \"filename\":\"wb_sdram.v\"             \
        }                                           \
    }                                               \
}"



INTEGRATION_CONFIG = "{                             \
    \"BASE_DIR\":\"~/projects/ibuilder_project\",   \
    \"board\":\"dionysus\",                         \
    \"TEMPLATE\":\"wishbone_template.json\",        \
    \"SLAVES\":{                                    \
        \"gpio1\":{                                 \
            \"filename\":\"wb_gpio.v\",             \
            \"integration\":[                       \
                \"gpio2\"                           \
            ]                                       \
        },                                          \
        \"gpio2\":{                                 \
            \"filename\":\"wb_gpio.v\"              \
        }                                           \
    },                                              \
    \"MEMORY\":{                                    \
        \"mem1\":{                                  \
            \"filename\":\"wb_sdram.v\"             \
        }                                           \
    }                                               \
}"

COMPLEX_INTEGRATION_CONFIG = "{                     \
    \"BASE_DIR\":\"~/projects/ibuilder_project\",   \
    \"board\":\"dionysus\",                         \
    \"TEMPLATE\":\"wishbone_template.json\",        \
    \"SLAVES\":{                                    \
        \"gpio1\":{                                 \
            \"filename\":\"wb_gpio.v\",             \
            \"integration\":[                       \
                \"gpio2\",                          \
                \"gpio3\"                           \
            ]                                       \
        },                                          \
        \"gpio2\":{                                 \
            \"filename\":\"wb_gpio.v\"              \
        },                                          \
        \"gpio3\":{                                 \
            \"filename\":\"wb_gpio.v\"              \
        }                                           \
    },                                              \
    \"MEMORY\":{                                    \
        \"mem1\":{                                  \
            \"filename\":\"wb_sdram.v\"             \
        }                                           \
    }                                               \
}"

