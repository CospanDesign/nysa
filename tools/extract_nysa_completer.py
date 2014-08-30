#! /usr/bin/python

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "nysa", "tools")))
import nysa_cli

if __name__ == "__main__":
    nysa_cli.COMPLETER_EXTRACTOR = True
    nysa_cli.main()
    

