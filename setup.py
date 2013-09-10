#! /usr/bin/env python

from setuptools import setup, find_packages
from distutils.command.install import install as DistutilsInstall

setup( 
    name='nysa',
    version='0.0.1',
    description='FPGA core/image generator and FPGA communication',
    author='Cospan Design',
    author_email='dave.mccoy@cospandesign.com',
    packages=find_packages('.'),
    data_files=[("nysa/cbuilder/drt", ["nysa/cbuilder/drt/drt.json"])],
    long_description="""\
            Nysa is an FPGA development toolset that is split into three
            branches:\n
            \tcbuilder: Design, build and simulate Verilog cores that are
            \t\tcompatible with either an Axi or Wishbone bus interface
            \tibuilder: generate FPGA images using command line interfaces or
            \t\tvisually with the Ninja-IDE plugin
            \thost: Interface with ibuilder generated image through a Python
            \t\tbased host API
    """,

    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: C",
        "Programming Language :: Verilog",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: FPGA Developers",
        "Intended Audience :: Developers",
        "Intended Audience :: Hobbiest",
        "Topic :: FPGA",

    ],
    keywords="FPGA",
    license="GPL",

)
