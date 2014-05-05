#Distributed under the MIT licesnse.
#Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

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

""" Spark Fun Camera

Facilitates communication with the Sparkfun Camera

For more details see:

http://wiki.cospandesign.com/index.php?title=Wb_sf_camera

"""


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time
import i2c

from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))


import nysa
from nysa import Nysa
from nysa import NysaCommError


from driver import Driver
from driver import NysaDMAException
from driver import DMAReadController

SPARKFUN_640_480_CAMERA_MODULE = 1


#Register Constants
CONTROL                   = 0
STATUS                    = 1
PIXEL_COUNT               = 2
ROW_COUNT                 = 3
MEM_0_BASE                = 4
MEM_0_SIZE                = 5
MEM_1_BASE                = 6
MEM_1_SIZE                = 7

#Control bit values
CONTROL_ENABLE            = 0
CONTROL_INTERRUPT_ENABLE  = 1
CONTROL_AUTO_FLASH_EN     = 2
CONTROL_MANUAL_FLASH_ON   = 3
CONTROL_CAMERA_RESET      = 4
CONTROL_RESET_COUNTS      = 5
CONTROL_IMAGE_DEBUG       = 6

#Status bit values
STATUS_MEMORY_0_FINISHED  = 0
STATUS_MEMORY_1_FINISHED  = 1
STATUS_IMAGE_CAPTURED     = 2
STATUS_BUSY               = 3
STATUS_LOCKED             = 4
STATUS_ENABLE             = 5
STATUS_MEMORY_0_EMPTY     = 6
STATUS_MEMORY_1_EMPTY     = 7

#Camera I2C Address
CAMERA_I2C = 0x3C
#CAMERA_I2C = 0x7A

#I2C Addresses
I2C_CLK         =   0x03
I2C_CONFIG_UTILS=   0x02
I2C_IMG_CONFIG  =   0x03
I2C_IMG_COUNTS  =   0x1A


class SFCameraError(Exception):
    pass

class SFCamera(Driver):

    @staticmethod
    def get_core_id():
        """
        Returns the identification number of the device this module controls

        Args:
            Nothing

        Returns (Integer):
            Number corresponding to the device in the drt.json file

        Raises:
            DRTError: Device ID Not found in drt.json
        """
        return Nysa.get_id_from_name("Camera")

    @staticmethod
    def get_core_sub_id():
        """Returns the identification of the specific implementation of this
        controller

        Example: Cospan Design wrote the HDL GPIO core with sub_id = 0x01
            this module was designed to interface and exploit features that
            are specific to the Cospan Design version of the GPIO controller.

            Some controllers may add extra functionalities that others do not
            sub_ids are used to differentiate them and select the right python
            controller for those HDL modules

        Args:
            Nothing

        Returns (Integer):
            Number ID for the HDL Module that this controls
            (Note: 0 = generic control or baseline funtionality of the module)

        Raises:
            Nothing
        """
        return SPARKFUN_640_480_CAMERA_MODULE

    def __init__(self, nysa, camera_id, i2c_id, debug = False):
        super(SFCamera, self).__init__(nysa, camera_id, debug)
        self.i2c = i2c.I2C(nysa, dev_id = i2c_id, debug = debug)
        self.i2c.enable_i2c(True)
        self.i2c.enable_interrupt(True)
        self.i2c.get_status()
        self.i2c.set_speed_to_100khz()
        self.reset_camera()
        self.set_rgb_mode()
        self.reset_counts()
        time.sleep(.4)
        row_count = self.read_row_count()
        pixel_count = self.read_pixel_count()
        size = row_count * pixel_count


        self.status = 0
        try:
            self.dma_reader = DMAReadController(device     = self,
                                                mem_base0  = 0x00000000,
                                                mem_base1  = 0x00100000,
                                                size       = size / 4,
                                                reg_status = STATUS,
                                                reg_base0  = MEM_0_BASE,
                                                reg_size0  = MEM_0_SIZE,
                                                reg_base1  = MEM_1_BASE,
                                                reg_size1  = MEM_1_SIZE,
                                                timeout    = 3,
                                                finished0  = STATUS_MEMORY_0_FINISHED,
                                                finished1  = STATUS_MEMORY_1_FINISHED,
                                                empty0     = STATUS_MEMORY_0_EMPTY,
                                                empty1     = STATUS_MEMORY_1_EMPTY)
        except NysaDMAException as ex:
            raise SFCameraError("Error initializing the DMA Reader: %s" % str(ex))


    def __del__(self):
        print "Shutdown"
        self.i2c.enable_i2c(False)
        #self.set_control(0)

    def get_control(self):
        """get_control

        Read the control register

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

        Write the control register

        Args:
            control: 32-bit control value

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(CONTROL, control)

    def get_status(self):
        """get_status

        read the status register

        Args:
            Nothing

        Return:
            32-bit status register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(STATUS)


    def enable_camera(self, enable):
        """

        Enable the camera core

        Args:
            enable(boolean): True/False to enable the camera and core

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        self.enable_register_bit(CONTROL, 0, enable)
        self.enable_register_bit(CONTROL, 1, enable)

    def read_row_count(self):
        """
        Read the number of rows from the camera

        Args:
            Nothing

        Returns (int)
            Number of rows in the image

        Raises:
            NysaCommError
        """
        return self.read_register(ROW_COUNT)

    def read_pixel_count(self):
        """
        Reads the number of pixels in a row

        Args:
            Nothing

        Returns (32-bit Integer):
            Number of pixels in a row

        Raises:
            NysaCommError
        """
        return self.read_register(PIXEL_COUNT)

    def reset_counts(self):
        """
        Resets the row and pixel counts so the core will re-read the values
        form an image

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        self.set_register_bit(CONTROL, 5)
        self.clear_register_bit(CONTROL, 5)

    def auto_led_mode(self, enable):
        """
        Allow core to enable and disable the 'Flash' LED

        Args:
            enable(boolean):
                True: Allow core to control LED
                False: Do not allow core to control LED

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        self.enable_register_bit(CONTROL, CONTROL_AUTO_FLASH_EN, enable)

    def manual_flash_on(self, enable):
        """
        When Auto mode is not enabled this will turn on the 'Flash'

        Args:
            enable(boolean):
                True: Turn on th flash
                False: Turn off the flash

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        self.enable_register_bit(CONTROL, CONTROL_MANUAL_FLASH_ON)

    def reset_camera(self):
        """
        Resets the camera core (sends reset to the camera as well)

        Args:
            Nothing

        Return:
            Nothing

        Raises:
            NysaCommError
        """
        self.clear_register_bit(CONTROL, CONTROL_CAMERA_RESET)
        time.sleep(.2)
        self.set_register_bit(CONTROL, CONTROL_CAMERA_RESET)
        time.sleep(.5)

    def enable_image_debug(self, enable):
        """
        Enable a debug image to be sent to the host from core
        (Exercise memroy controller)

        Args:
            enable (boolean):
                True: Send the debug image to the host
                False: Set the camera to normal mode

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        self.enable_register_bit(CONTROL, CONTROL_IMAGE_DEBUG, enable)

    def get_config_data(self):
        config_dict = {}
        img_config = self.i2c.read_from_i2c(CAMERA_I2C, Array('B', [0x02]), 2)
        return img_config

    def set_rgb_mode(self, mode = 0x00):
        """
        Set the camera to output RGB data instead of YCBCR data

        Args:
            mode (32-bit unsigned integer) default = 0x00 (RGB)

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        mode = mode << 2
        mode |= 0x02

        self.i2c.write_to_i2c(CAMERA_I2C, Array('B', [0x02, 0x40]))
        self.i2c.write_to_i2c(CAMERA_I2C, Array('B', [I2C_IMG_CONFIG, mode]))
        self.i2c.is_interrupt_enabled()

    def set_start_pixel_count(self, start_pixel):
        """
        Adjust the start of the pixel count within the camera

        Args:
            start_pixel (16-bit unsigned integer): Start pixel of the image

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        sp = Array('B')
        sp.append(start_pixel & 0xFF)
        sp.append(((start_pixel) >> 8) & 0xFF)
        self.i2c.write_to_i2c(CAMERA_I2C, Array('B', [0x1E, sp[0]]))
        self.i2c.write_to_i2c(CAMERA_I2C, Array('B', [0x1F, sp[1]]))

    def software_reset(self):
        #self.i2c.write_to_i2c(CAMERA_I2C, Array('B', [0x02, 0x40]))
        time.sleep(.5)
        #self.i2c.write_to_i2c(CAMERA_I2C, Array('B', [0x02, 0x00]))


    def set_debug_mode(self):
        #print "Setting idle mode"
        self.i2c.write_to_i2c(CAMERA_I2C, Array('B', [0x02, 0x08]))

    def read_raw_image(self):
        """
        Read an entire image from the memory. The size of the image is set
        during initialization of the DMA Reader controller. The data is outputted
        This data is not formatted

        Args:
            Nothing

        Returns:
            (Array of bytes): Size of the image (row * pixel count)

        """
        return self.dma_reader.read(anticipate = True)

