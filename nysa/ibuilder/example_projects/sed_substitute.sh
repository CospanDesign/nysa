#! /bin/bash

echo "Fixing FTDI Interface"
sed -i 's/\"ftdi_clk\":/\"i_ftdi_clk\":/g' *.json
sed -i 's/\"ftdi_data/\"io_ftdi_data/g' *.json
sed -i 's/\"ftdi_txe/\"i_ftdi_txe/g' *.json
sed -i 's/\"ftdi_wr_n/\"o_ftdi_wr_n/g' *.json
sed -i 's/\"ftdi_rde_n/\"i_ftdi_rde_n/g' *.json
sed -i 's/\"ftdi_rd_n/\"o_ftdi_rd_n/g' *.json
sed -i 's/\"ftdi_oe_n/\"o_ftdi_oe_n/g' *.json
sed -i 's/\"ftdi_siwu/\"o_ftdi_siwu/g' *.json
sed -i 's/\"o_ftdi_suspend_n/\"i_ftdi_suspend_n/g' *.json


echo "Changing UART Interface"
sed -i 's/\"phy_uart_in/\"i_phy_uart_in/g' *.json
sed -i 's/\"phy_uart_out/\"o_phy_uart_out/g' *.json

echo "Changing LAX UART interface"
sed -i 's/\"la_uart_tx/\"o_la_uart_tx/g' *.json
sed -i 's/\"la_uart_rx/\"i_la_uart_rx/g' *.json

echo "Changing SDRAM interface"
sed -i 's/\"sdram_clk/\"o_sdram_clk/g' *.json
sed -i 's/\"sdram_cke/\"o_sdram_cke/g' *.json
sed -i 's/\"sdram_cs_n/\"o_sdram_cs_n/g' *.json
sed -i 's/\"sdram_ras/\"o_sdram_ras/g' *.json
sed -i 's/\"sdram_cas/\"o_sdram_cas/g' *.json
sed -i 's/\"sdram_we/\"o_sdram_we/g' *.json
sed -i 's/\"sdram_bank/\"o_sdram_bank/g' *.json
sed -i 's/\"sdram_addr/\"o_sdram_addr/g' *.json
sed -i 's/\"sdram_data/\"io_sdram_data/g' *.json
sed -i 's/\"sdram_data_mask/\"o_sdram_data_mask/g' *.json

sed -i 's/\"port/\"loc/g' *.json

sed -i 's/:\"i_ftdi_clk\"/:\"ftdi_clk\"/g' *.json
sed -i 's/:\"o_sdram_clk\"/:\"sdram_clk\"/g' *.json

#sed -i 'a/\"board\"/\"IMAGE_ID\":0,/g dionysus_gpio_mem.json

sed -i 's/sycamore_projects/ibuilder_project/g' *.json

sed -i 's/io_sdram_data_mask/o_sdram_data_mask/g' *.json
