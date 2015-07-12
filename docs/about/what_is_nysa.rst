What is Nysa?
=============

Nysa is a tool that simplifies development for FPGAs.

Development for FPGAs
---------------------

FPGA development is challenging because ???

* Know verilog
* Know how verilog code and FPGAs are related (constraints)
* Know how FPGAs and their platform are related (FPGA chip and circuit board)

Nysa breaks down FPGA development into three steps, and offers tools for each step.

#. Core Developemnt: Developing functionality that performs tasks such as acquiring images from a camera sensor, or flashing an LED. This can be a large undertaking to set up a verilog project. `CBuilder`_ is Nysa's tool that will generate a ready to go verilog project that can immediately be incorporated into a final FPGA image.
#. FPGA Image Development: Creating an FPGA image is usually a large and error prone task. There are a lot of things to get right. `IBuilder`_ is a tool that will read in a simple configuration file and output a vendor specific build project that will create an FPGA image by typing 'scons' on the terminal.
#. FPGA Interaction: After you have built an FPGA image you want to interact with it. Nysa provides infrastructure that enables users to communicate with their cores they built with `CBuilder`_ in a similar way they used to develop for it.



CBuilder
--------
* Generate Projects
* The generated projects are easy to develop, stimulate and debug
* Provides a mechanism to view the output waveform
* The core that is built is ready to be incorporated into an entire FPGA image

IBuilder
--------
* From a configuration file generates an FPGA project that can be built with the target FPGAs vendor specific tools
* Generates a ROM file that will be incorporated within an FPGA image. This ROM file can be read and parsed by a host tool to determine the behavior of the FPGA.


Host
----
* Tools to interact with FPGAs and their platform (The boards that the FPGA chips are on).
* Common/Simple API used to control the FPGA functions
