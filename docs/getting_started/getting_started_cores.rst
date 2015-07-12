Getting Started Creating Verilog Cores
======================================

This guide will show you how to get started creating verilog projects that are easy to build, simulate and debug. Once your are done with verilog core the Nysa can incorporate the core and put it into an FPGA image.

Prerequisits
------------

The main :ref:`Getting Started <getting-started>` must be completed before following this guide


Requirements
------------

Scons
^^^^^
Scons is a build tool similar to make but instead of using the Make syntax uses Python based syntax

`Scons Homepage <http://scons.org>`


**Installation on Ubuntu**
Within a terminal enter (depending on your installation situation you may need 'sudo' privledges)
``sudo apt-get install scons``

**Installation on Windows**
Download and install `scons <http://www.scons.org/download.php>`

Icarus Verilog and GTKWave
^^^^^^^^^^^^^^^^^^^^^^^^^^
Icarus Verilog is used to compile and simulate your verilog projects

`Icarus Verilog Homepage <http://iverilog.icarus.com>`

GTKWave is a logic waveform visualizer

`GTKWave Homepage <http://gtkwave.sourceforge.net>`

**Installation on Ubuntu**
Within a terminal enter (depending on your installation situation you may need 'sudo' privledges)
``sudo apt-get install verilog``
``sudo apt-get install gtkwave``

**Installation on Windows**
Download and install `Icarus Verilog <http://bleyer.org/icarus>`


First Nysa Verilog Core Project (CBuilder Project)
--------------------------------------------------
Although the tool will allow you to create a cbuilder project in any directory, it is good to put it in a place that the tool can find it, with that if your 

