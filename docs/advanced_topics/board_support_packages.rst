.. _board-support-package:

Building a Board Support Package
================================

The purpose of a board support package is to enable Nysa to both build images for that platform and communicate with that platform. In order to accomplish this.

The package consists of configuration files that tell Nysa various aspects the platform such as

* What type of FPGA is on the board.
* The correct flags to pass to the vendor tools to build an FPGA image correctly.
* Required cores to support various features of the FPGA such as board specific memory controllers.

The designer must also supply the python scripts to perform the following functions:

* Download the built FPGA image onto the platform
* Initiate a program cycle
* Communicate with the platform specific host interface, this host interface can be UART, SPI, USB FIFO, or even PCI Express.

Optional scripts are:

* Reset the internal state machines of the FPGA
* Monitor the done pin


A demo repository is located here: `nysa-demo-platform <https://github.com/CospanDesign/nysa-demo-platform.git>`_

