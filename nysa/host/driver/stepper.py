#Distributed under the MIT licesnse.
#Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

""" Stepper

Facilitates communication with the Stepper core independent of communication
medium

For more details see:

http://wiki.cospandesign.com/index.php?title=Wb_spi

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time

from array import array as Array


from nysa.host.nysa import Nysa
from nysa.host.nysa import NysaCommError

import driver

COSPAN_DESIGN_STEPPER_MODULE = 0x01

#Register Constants
CONFIGURATION               = 0
CONTROL                     = 1
COMMAND                     = 2
STATUS                      = 3
CLOCK_RATE                  = 4
STEPS                       = 5
WALK_PERIOD                 = 6
RUN_PERIOD                  = 7
STEP_ACCELLERATION          = 8
MICRO_STEP_HOLD             = 9
SHOOT_THROUGH_DELAY         = 10
CURRENT_POSITION            = 11
MAX_POSITION                = 12


#Configuration
CONFIG_UNIPOLAR             = 0
CONFIG_BIPOLAR              = 1
CONFIG_ENABLE_INT           = 2

#Control/Status bit values
CONTROL_DIRECTION           = 0
CONTROL_CONTINUOUS          = 1

CONTROL_STEP_POS            = 4
CONTROL_FULL_STEP           = 1
CONTROL_HALF_STEP           = 2
CONTROL_MICRO_STEP          = 3

#Commands
COMMAND_GO                  = 1
COMMAND_STOP                = 2

#Status
STATUS_BUSY                 = 0
STATUS_ERR_BAD_CMD          = 8
STATUS_ERR_BAD_STEP         = 9
STATUS_ERR_BAD_CONFIG       = 10


class StepperError(Exception):
    """Stepper Motor Controller

    Errors associated with Stepper Controller

    Bad Command
    Bad Step Value
    Bad Configuration
    """
    pass

class Stepper(driver.Driver):
    """
    Stepper Motor Controller
    """
    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return driver.get_device_id_from_name("stepper")

    @staticmethod
    def get_abi_minor():
        return COSPAN_DESIGN_STEPPER_MODULE

    @staticmethod
    def construct_step_count(full_steps, half_steps, micro_steps):
        steps = (full_steps << 9) + (half_steps << 8) + (micro_steps << 4)
        print "steps: 0x%08X" % steps
        return steps

    def __init__(self, nysa, urn, debug = False):
        super(Stepper, self).__init__(nysa, urn, debug)
        status = 0x00

    def __del__(self):
        pass

    def get_configuration(self):
        """get_configuration

        reads the configuration register

        Args:
            Nothing

        Return:
            32-bit configuration register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CONFIGURATION)

    def set_configuration(self, configuration):
        """set_configuration

        write the configuration register

        Args:
            configuration: 32-bit configuration value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(CONFIGURATION, configuration)

    def get_control(self):
        """get_control

        reads the control register

        Args:
            Nothing

        Return:
            32-bit control register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CONTROL)

    def set_control(self, control):
        """set_control

        write the control register

        Args:
            control: 32-bit control value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(CONTROL, control)

    def print_control(self, control):
        print "Command: 0x%08X" % control
        if (control & (1 << CONTROL_DIRECTION)):
            print "\tForward"
        else:
            print "\tReverse"
        if (control & (1 << CONTROL_CONTINUOUS)):
            print "\tContinuous"
        if ((control >> 4) & 0xF) == 1:
            print "\tFull Step"
        if ((control >> 4) & 0xF) == 2:
            print "\tHalf Step"
        if ((control >> 4) & 0xF) == 3:
            print "\tMicro Step"

    def get_command(self):
        """get_command

        reads the command register

        Args:
            Nothing

        Return:
            32-bit command register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(COMMAND)

    def set_command(self, command):
        """set_command

        write the command register

        Args:
            command: 32-bit command value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(COMMAND, command)

    def get_clock_rate(self):
        """get_clock_rate

        reads the clock_rate register

        Args:
            Nothing

        Return:
            32-bit clock_rate register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CLOCK_RATE)

    def get_status(self):
        """get_status

        reads the status register

        Args:
            Nothing

        Return:
            32-bit status register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(STATUS)

    def print_status(self, status):
        print "Status: 0x%08X" % status
        if (status & (1 << STATUS_BUSY)) > 0:
            print "\tBusy"
        if (status & (1 << STATUS_ERR_BAD_CMD)):
            print "\tBad Command"
        if (status & (1 << STATUS_ERR_BAD_STEP)):
            print "\tBad Step Declaration"
        if (status & (1 << STATUS_ERR_BAD_CONFIG)):
            print "\tBad Configuration"

    def get_steps(self):
        """get_steps

        reads the steps register

        Args:
            Nothing

        Return:
            32-bit steps register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(STEPS)

    def set_steps(self, steps):
        """set_steps

        write the steps register

        Args:
            32-bit register steps
                Format:
                    31 - 9  : Full Step Values
                    8       : Half Step Values
                    7  - 4  : Micro Steps
                    3  - 0  : Not Used

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(STEPS, steps)

    def set_float_steps(self, steps):
        """set_steps

        write the steps register

        Args:
            steps: A Floating point number of steps

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        if type(steps) is not float:
            raise StepperError("steps is supposed to be a float, not: %s" % str(type(steps)))

        #Get all the half steps
        print "Original Steps: %f" % steps
        int_steps = (int(steps) << 9)
        print "full int steps: 0x%08X" % (int_steps >> 9)
        print "Half int steps: 0x%08X" % (int_steps >> 8)

        if steps >= 1:
            steps -= int(steps)

        #int_steps += (steps * 10000)
        print "Float Steps: %f" % steps

        print "int steps: 0x%08X" % int_steps
        self.write_register(STEPS, int_steps)

    def get_walk_period(self):
        """get_walk_period

        reads the walk_period register

        Args:
            Nothing

        Return:
            32-bit walk_period register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(WALK_PERIOD)

    def set_walk_period(self, walk_period):
        """set_walk_period

        write the walk_period register

        Args:
            walk_period: 32-bit walk_period value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(WALK_PERIOD, walk_period)

    def get_run_period(self):
        """get_run_period

        reads the run_period register

        Args:
            Nothing

        Return:
            32-bit run_period register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(RUN_PERIOD)

    def set_run_period(self, run_period):
        """set_run_period

        write the run_period register

        Args:
            run_period: 32-bit run_period value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(RUN_PERIOD, run_period)

    def get_step_accelleration(self):
        """get_step_accelleration

        reads the step_accelleration register

        Args:
            Nothing

        Return:
            32-bit step_accelleration register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(STEP_ACCELLERATION)

    def set_step_accelleration(self, step_accelleration):
        """set_step_accelleration

        write the step_accelleration register

        Args:
            step_accelleration: 32-bit step_accelleration value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(STEP_ACCELLERATION, step_accelleration)

    def get_micro_step_hold(self):
        """get_micro_step_hold

        reads the micro_step_hold register

        Args:
            Nothing

        Return:
            32-bit micro_step_hold register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(MICRO_STEP_HOLD)

    def set_micro_step_hold(self, micro_step_hold):
        """set_micro_step_hold

        write the micro_step_hold register

        Args:
            micro_step_hold: 32-bit micro_step_hold value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(MICRO_STEP_HOLD, micro_step_hold)

    def get_shoot_through_delay(self):
        """get_shoot_through_delay

        reads the shoot_through_delay register

        Args:
            Nothing

        Return:
            32-bit shoot_through_delay register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(SHOOT_THROUGH_DELAY)

    def set_shoot_through_delay(self, shoot_through_delay):
        """set_shoot_through_delay

        write the shoot_through_delay register

        Args:
            shoot_through_delay: 32-bit shoot_through_delay value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(SHOOT_THROUGH_DELAY, shoot_through_delay)

    def get_current_position(self):
        """get_current_position

        reads the current_position register

        Args:
            Nothing

        Return:
            32-bit current_position register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CURRENT_POSITION)

    def get_current_position_float(self):
        """get_current_position

        reads the current_position register

        Args:
            Nothing

        Return:
            32-bit current_position register value

        Raises:
            NysaCommError: Error in communication
        """
        curr_pos = self.read_register(CURRENT_POSITION)
        f_curr_pos = curr_pos >> 9
        f_curr_pos += (curr_pos & 0xFF) * 0.0001
        return f_curr_pos

    def set_current_position(self, position):
        """set_current_position

        write the current_position register

        Args:
            (32-bit) position

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        return self.write_register(CURRENT_POSITION, position)

    def get_max_position(self):
        """get_max_position

        reads the max_position register

        Args:
            Nothing

        Return:
            32-bit max_position register value

        Raises:
            NysaCommError: Error in communication
        """
        return (self.read_register(MAX_POSITION) >> 9)

    def set_max_position(self, max_position):
        """set_max_position

        write the max_position register

        Args:
            max_position: 32-bit max_position value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        if self.debug: print "Max Position: %d" % (max_position << 9)
        self.write_register(MAX_POSITION, (max_position << 9))

    def configure_unipolar_stepper(self):
        configuration = self.get_configuration()
        configuration &= ~((1 << CONFIG_UNIPOLAR) | (1 << CONFIG_BIPOLAR))
        configuration |= (1 << CONFIG_UNIPOLAR)
        self.set_configuration(configuration)

    def is_unipolar(self):
        return self.is_register_bit_set(CONFIGURATION, CONFIG_UNIPOLAR)

    def configure_bipolar_stepper(self):
        configuration = self.get_configuration()
        configuration &= ~((1 << CONFIG_UNIPOLAR) | (1 << CONFIG_BIPOLAR))
        configuration |= (1 << CONFIG_BIPOLAR)
        self.set_configuration(configuration)

    def is_bipolar(self):
        return self.is_register_bit_set(CONFIGURATION, CONFIG_BIPOLAR)

    def enable_interrupt(self, enable):
        self.enable_register_bit(CONFIGURATION, CONFIG_ENABLE_INT, enable)

    def is_interrupt_enabled(self):
        return self.is_register_bit_set(CONFIGURATION, CONFIG_ENABLE_INT)

    def enable_continuous(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_CONTINUOUS, enable)

    def set_direction(self, forward):
        self.enable_register_bit(CONTROL, CONTROL_DIRECTION, forward)

    def set_full_step(self):
        control = self.get_control()
        control &= ~((1 << CONTROL_STEP_POS) | (1 << (CONTROL_STEP_POS + 1)) | (1 << (CONTROL_STEP_POS + 2)))
        control |= (CONTROL_FULL_STEP << 4)
        self.set_control(control)

    def set_half_step(self):
        control = self.get_control()
        control &= ~((1 << CONTROL_STEP_POS) | (1 << (CONTROL_STEP_POS + 1)) | (1 << (CONTROL_STEP_POS + 2)))
        control |= (CONTROL_HALF_STEP << 4)
        self.set_control(control)

    def set_micro_step(self):
        control = self.get_control()
        control &= ~((1 << CONTROL_STEP_POS) | (1 << (CONTROL_STEP_POS + 1)) | (1 << (CONTROL_STEP_POS + 2)))
        control |= (CONTROL_MICRO_STEP << 4)
        self.set_control(control)

    def go (self):
        if self.debug: print "Go!"
        self.write_register(COMMAND, COMMAND_GO)

    def stop(self):
        self.write_register(COMMAND, COMMAND_STOP)

    def is_busy(self):
        status = self.get_status()
        while (status & (1 << STATUS_BUSY)) > 0:
            return True
        return False

    def is_error(self):
        status = self.get_status()
        if (status & (STATUS_ERR_BAD_STEP | STATUS_ERR_BAD_CMD | STATUS_ERR_BAD_CONFIG)):
            return True
        return False

