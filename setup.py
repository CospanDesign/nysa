#! /usr/bin/env python

from setuptools import setup, find_packages
from distutils.command.install import install as DistutilsInstall

setup( 
    name='nysa',
    version='0.8.0',
    description='FPGA core/image generator and FPGA communication',
    author='Cospan Design',
    author_email='dave.mccoy@cospandesign.com',
    packages=find_packages('.'),
    data_files=[("nysa/cbuilder/drt", ["nysa/cbuilder/drt/drt.json"])],
    long_description=open("README.md").read(),
    scripts=[
        "bin/nysa-device-list",
        "bin/nysa-generate-slave",
        "bin/nysa-image-builder",
        "bin/nysa-update"
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: C",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
    ],
    keywords="FPGA",
    license="GPL",
)
