#!/usr/bin/python

import unittest
import json
import sys
import os
import time
from array import array as Array
from PIL import Image


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver.sf_camera import SFCamera
from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("fatal")
        plat = ["", None, None]
        pscanner = PlatformScanner()
        platform_dict = pscanner.get_platforms()
        platform_names = platform_dict.keys()

        if "sim" in platform_names:
            #If sim is in the platforms, move it to the end
            platform_names.remove("sim")
            platform_names.append("sim")
        urn = None
        for platform_name in platform_names:
            if plat[1] is not None:
                break

            self.s.Debug("Platform: %s" % str(platform_name))

            platform_instance = platform_dict[platform_name](self.s)
            #self.s.Verbose("Platform Instance: %s" % str(platform_instance))

            instances_dict = platform_instance.scan()

            for name in instances_dict:

                #s.Verbose("Found Platform Item: %s" % str(platform_item))
                n = instances_dict[name]
                plat = ["", None, None]

                if n is not None:
                    self.s.Important("Found a nysa instance: %s" % name)
                    n.read_sdb()
                    #import pdb; pdb.set_trace()
                    if n.is_device_in_platform(SFCamera):
                        plat = [platform_name, name, n]
                        break
                    continue

                #self.s.Verbose("\t%s" % psi)

        if plat[1] is None:
            self.camera = None
            return
        n = plat[2]
        urn = n.find_device(SFCamera)[0]
        self.s.set_level("verbose")
        self.s.Important("Using Platform: %s" % plat[0])
        self.s.Important("Instantiated a SFCamera Device: %s" % urn)
        self.camera = SFCamera(n, urn)
        self.received_callback = False

    def read_image_callback(self):
        self.received_callback = True
        self.s.Debug("Image callback")

    def test_camera(self):
        if self.camera is None:
            self.s.Fatal("Cannot Run Test when no device is found!")
            return
        #Setup the camera
        self.camera.unregister_interrupt_callback(None)
        self.s.Debug("Image Height: %d" % self.camera.get_height())
        self.s.Debug("Image Width : %d" % self.camera.get_width())

        self.s.Debug("Initialize the camera")
        self.camera.set_control(0x00)
        self.camera.reset_camera()
        self.camera.set_rgb_mode()
        self.camera.reset_counts()
        time.sleep(0.1)
        row_count = self.camera.read_row_count()
        pixel_count = self.camera.read_pixel_count()
        height = row_count
        width = pixel_count / 2
        self.s.Debug("Height: %d" % height)
        self.s.Debug("Width : %d" % width)

        self.camera.enable_camera(True)
        time.sleep(0.1)
        #self.s.Important("Wait for a callback from the camera...")
        self.camera.start_async_reader(self.read_image_callback)
        #self.s.Important("Sleep for a moment...")
        time.sleep(0.4)
        '''
        data = self.camera.read_raw_image()
        print "Length of data: %d" % len(data)
        shape = (self.camera.get_width(), self.camera.get_height())
        img = Image.frombuffer('RGB', shape, data)
        img.save("/home/cospan/foo.png")
        '''
        if self.received_callback:
            data = self.camera.dma_reader.async_read()
            #Expand Image
            rgb_image = Array('B')
            for i in range(0, height * width * 2, 2):
                #top = data[i]
                #bot = data[i + 1]

                #red = ((top >> 3) & 0x1F) << 3
                #green = (((top & 0x7) << 3) | ((bot >> 5) & 0x7)) << 2
                #blue = (top & 0x1F) << 3

                value = (data[i + 1] << 8) + data[i]
                red = ((value >> 11) & 0x1F) << 3
                green = ((value >> 5) & 0x3F) << 2
                blue = (value & 0x1F) << 3

                rgb_image.append(red)
                rgb_image.append(green)
                rgb_image.append(blue)

            self.s.Debug("RGB Image Size: %d" % len(rgb_image))

            self.s.Important("Received callback from camera")
            self.s.Debug("Length of data: %d" % len(data))
            shape = (self.camera.get_width(), self.camera.get_height())
            img = Image.frombuffer('RGB', shape, rgb_image)
            img.save("camera_image.png")
        else:
            self.s.Error("Did not receive callback")

if __name__ == "__main__":
    unittest.main()

