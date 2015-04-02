#! /usr/bin/env python

import os
import glob

from setuptools import setup, find_packages



long_desc=""

try:
    long_desc=open("README.md").read(),
    #Try and convert the readme from markdown to pandoc
    from pypandoc import convert
    long_desc = convert("README.md", 'rst')
except:
    long_desc="FPGA core/image generator and FPGA communiation"
    pass

setup( 
    name='nysa',
    version='0.8.05',
    description='FPGA core/image generator and FPGA communication',
    author='Cospan Design',
    author_email='dave.mccoy@cospandesign.com',
    packages=find_packages('.'),
    url="http://nysa.cospandesign.com",
    package_data={'' : ["*.json", "*.txt, *.md"]},
    data_files=[
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
