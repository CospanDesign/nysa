Getting started with IBuilder
=============================

This guide will show you how to get started creating FPGA images using a configuration file and nysa ibuilder tool. When you have built and downloaded an FPGA image you use the host interface to interface with your custom image.

Prerequisits
------------

The main :ref:`Getting Started <getting-started>` must be completed before following this guide.


Requirements
------------

A vendor specific build system. At the time of this writing the Xilinx build tool and Xilinx webpack must be downloaded and installed to build an actual FPGA image. The download link can be found here:

`Xilinx Webpack Download <http://www.xilinx.com/products/design-tools/ise-design-suite/ise-webpack.html>`_

First Nysa IBuilder Project (Image Builder)
-------------------------------------------

The easiest way to get started with the ibuilder is to copy a default build configuration file and modify it.

I'll be using `Dionysus <http://wiki.cospandesign.com/index.php?title=Dionysus>`_ as my target board in this demo but this demo can be adapted to work with any FPGA platform that has a supported nysa platform package. If an FPGA development board exists that is not supported by Nysa you can adapt it by following this guide: :ref:`Building a Board Support Package <board-support-package>`

.. code-block:: json

    {
        "BASE_DIR":"~/projects/ibuilder_project",
        "board":"dionysus",
        "PROJECT_NAME":"example_project",
        "SLAVES":{
            "gpio1":{
                "filename":"wb_gpio.v",
                "unique_id":1,
                "bind":{
                    "gpio_out[1:0]":{
                        "loc":"led[1:0]",
                        "direction":"output"
                    },
                    "gpio_in[3:2]":{
                        "loc":"button[1:0]",
                        "direction":"input"
                    }
                }
            }
        }
    }

Before we start modifying this configuration file lets point out some of the keywords within the configuration file. For complete documentation refere to :ref:`ibuilder configuration file <ibuilder-configuration>`
