#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import stepper
from nysa.common.status import Status

class Test (unittest.TestCase):

    def setUp(self):
        s = Status()
        s.set_level("fatal")

        print "Unit test!"
        pass
        '''
        for name in get_platforms():
            try:
                self.n = find_board(name, status = s)
            except PlatformScannerException as ex:
                pass
        self.n.read_sdb()
        urns = self.n.find_device(I2C)
        self.simple_dev = MockGPIODriver(self.n, urns[0], False)
        s.set_level("error")
        '''

    def notest_stepper(self):
        '''
        print "Stepper Motor Unit Test: ID: %d" % dev_id
        stepper = Stepper(nysa, dev_id, debug = debug)
        #Set the motor to bipolar
        if debug:
            print "Clock Rate: 0x%08X" % stepper.get_clock_rate()
        stepper.configure_bipolar_stepper()
        if debug:
            print "configuration: 0x%08X" % stepper.get_configuration()
        if debug:
            stepper.print_status(stepper.get_status())
        #Setup the walk period
        stepper.set_walk_period         (0x00100000)
        stepper.set_run_period          (0x00008000)
        #stepper.set_step_accelleration(1000)
        stepper.set_step_accelleration  (      1000)
        stepper.set_micro_step_hold     (         0)
        stepper.set_max_position        (       200)
        print "Max position: %d" % stepper.get_max_position()
        #Enable Interrupt

        #Set the direction to forward
        stepper.set_direction(1)    # Forward
        #stepper.set_direction(0)    # Reverse

        #Set to full steps
        #stepper.set_full_step()
        #stepper.set_half_step()
        stepper.set_micro_step()
        if debug:
            stepper.print_status(stepper.get_status())

        #Set to not continuous
        #stepper.enable_continuous(True)
        #stepper.go()
        #time.sleep(2)
        #stepper.stop()
        #time.sleep(1)
        stepper.enable_continuous(False)

        stepper.set_steps(stepper.construct_step_count( full_steps  = 100,
                                                        half_steps  = 0,
                                                        micro_steps = 0))
        #stepper.set_float_steps(10.00)

        if debug:
            stepper.print_control(stepper.get_control())
        #Set the go command
        stepper.go()
        if debug:
            stepper.print_status(stepper.get_status())

        start = time.time()
        step_time = time.time()
        syms = ['\\', '|', '/', '-']
        syms_pos = 0
        bs = '\b'
        while (stepper.is_busy()):
            sys.stdout.write("\b%s" % syms[syms_pos])
            syms_pos += 1
            if syms_pos >= len(syms):
                syms_pos = 0
            sys.stdout.flush()
            time.sleep(.1)


        sys.stdout.write("\b")

        print "Current Position: 0x%08X" % (stepper.get_current_position())
        print "Final Delta T (Seconds): %f" % (time.time() - start)
        print "Final Status: 0x%08X" % (stepper.get_status())
        print "Final Command: 0x%08X" % (stepper.get_command())
        #while (stepper.wait_for_interrupts()):
        #    print "Waiting for interrupts..."
        #    time.sleep(10)
        print "Finished"
        '''
        pass


