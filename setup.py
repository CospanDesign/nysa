#! /usr/bin/env python

import os
import glob

from setuptools import setup, find_packages
from distutils.command.install import install as DistutilsInstall

long_desc=open("README.md").read(),

try:
    #Try and convert the readme from markdown to pandoc
    from pypandoc import convert
    long_desc = convert("README.md", 'rst')
except:
    pass

setup( 
    name='nysa',
    version='0.8.03',
    description='FPGA core/image generator and FPGA communication',
    author='Cospan Design',
    author_email='dave.mccoy@cospandesign.com',
    packages=find_packages('.'),
    url="http://nysa.cospandesign.com",
    package_data={'' : ["/nysa/data/bash_complete/nysa", "*.json", "*.txt"]},
    data_files=[
     ('/etc/bash_completion.d/', ['nysa/data/bash_complete/nysa'])
    ],
    include_package_data = True,
    long_description=long_desc,
    scripts=[
        "bin/nysa"
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
    ],
    keywords="FPGA",
    license="GPL"
)
