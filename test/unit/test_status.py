#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.common import status

class Test(unittest.TestCase):

    def setUp(self):
        self.dbg = False

    def test_all_functions(self):
        s = status.Status()
        s.Verbose("verbose")
        s.Debug("debug")
        s.Info("info")
        s.Important("important")
        s.Warning("warning")
        s.Error("error")
        s.Fatal("fatal")


if __name__ == "__main__":
  unittest.main()

