#test.py
#=============================================================================
# Codigo de verificacion con Cocotb para PostCpuSys
#=============================================================================
# Actualizacion para operar con cocotb 2.0 y versiones posteriores
#=============================================================================
#   Cambios:
#       - En la funcion Clock(), el parametro "units" cambbia a "unit"
#       - La operaciones logicas con enteros binarios (bitwise) requieren emplear
#         el valor en su tipo entero, por ejemplo, dut.signal_x.value.integer en
#         vez de solo dut.signal_x.value. 
#=============================================================================
# Author: Gerardo A. Laguna S.
# Universidad Autonoma Metropolitana
# Unidad Lerma
# 12.dic.2025
#=============================================================================

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import LogicArray, Logic

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #Masks definitions according to the pinout:
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    # Inputs:
    #   ui[0]: "OUT_CTRL0"
    #   ui[1]: "OUT_CTRL1"
    #   ui[2]: "OUT_CTRL2"
    #   ui[3]: "SPI_SCK"
    #   ui[4]: "SPI_MOSI"
    #   ui[5]: "SPI_CS"
    #   ui[6]: "RUN"
    #   ui[7]: "MODE"
    #
    # Outputs:
    #   uo[0]: "OUT8B0"
    #   uo[1]: "OUT8B1"
    #   uo[2]: "OUT8B2"
    #   uo[3]: "OUT8B3"
    #   uo[4]: "OUT8B4"
    #   uo[5]: "OUT8B5"
    #   uo[6]: "OUT8B6"
    #   uo[7]: "OUT8B7"
    #
    # Bidirectional pins as otputs:
    #   uio[0]: "STATE0"
    #   uio[1]: "STATE1"
    #   uio[2]: "STATE2"
    #   uio[3]: "STATE3"
    #   uio[4]: "OUT3B0"
    #   uio[5]: "OUT3B1"
    #   uio[6]: "OUT3B2"
    #   uio[7]: "SPI_MISO"

    MSK_SPI_SCK_TO_ON = 0x08
    MSK_SPI_SCK_TO_OFF = 0xF7
    MSK_SPI_MOSI_TO_ON = 0x10
    MSK_SPI_MOSI_TO_OFF = 0xEF
    MSK_SPI_CS_TO_ON = 0x20
    MSK_SPI_CS_TO_OFF = 0xDF
    MSK_RUN_TO_ON = 0x40
    MSK_RUN_TO_OFF = 0xBF
    MSK_MODE_TO_ON = 0x80
    MSK_MODE_TO_OFF = 0x7F
    MSK_OUT3B = 0x70
    MSK_STATE = 0x0F

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # OUT8b and OUT3B seting
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #   +--------+-------------+--------------------+----------------+
    #   |out_ctrl|    OUT8B    |       OUT3B        |      Note      |
    #   +--------+-------------+--------------------+----------------+
    #   |   0    | spi2rom_add | spi2rom_din[2:0]   |                |
    #   +--------+-------------+--------------------+----------------+
    #   |   1    | spi2rom_add | spi2rom_dout[2:0]  |                |
    #   +--------+-------------+--------------------+----------------+
    #   |   2    | spi2ram_add |{2'b00,spi2rom_din} |                |
    #   +--------+-------------+--------------------+----------------+
    #   |   3    | spi2ram_add |{2'b00,spi2rom_dout}|                |
    #   +--------+-------------+--------------------+----------------+
    #   |   4    | cpu2rom_add | cpu2rom_dout[2:0]  |   OUT8B= IP    |
    #   +--------+-------------+--------------------+----------------+
    #   |   5    | cpu2rom_add | cpu2rom_dout[2:0]  |   OUT8B= IP    |
    #   +--------+-------------+--------------------+----------------+
    #   |   6    | cpu2ram_add |{2'b00,cpu2rom_din} |   OUT8B= DP    |
    #   +--------+-------------+--------------------+----------------+
    #   |   7    | cpu2ram_add |{2'b00,cpu2rom_dout}|   OUT8B= DP    |
    #   +--------+-------------+--------------------+----------------+

    MSK_OUT_CTRL_TO_0 = 0xF8
    MSK_OUT_CTRL_TO_4 = 0x04

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Programing mode (MODE=0) with OUT_CTRL=0 (OUT8B = spi2rom_add, OUT3B=spi2rom_din[2:0])
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #Master SPI initial values:  
    dut.ui_in.value  = MSK_SPI_SCK_TO_ON | MSK_SPI_CS_TO_ON | MSK_SPI_MOSI_TO_ON
    await ClockCycles(dut.clk, 16)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Sequence of ROM write SPI commands to store Post intructions
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #    |-------------------------------|
    #    |         2 Bytes SPI word      |
    #    |-------------------------------|
    #    | RW  |  Address  |     Data    |                                                        
    #    | bit |   bits    |     bits    |                                                    
    #    |-----|-----------|-------------|
    #    | b15 | [b14:b04] |  [b03:b00]  |
    #    |-----|-----------|-------------|
    #    |  x  |xxxxxxxxxxx|    xxxx     |
    #    |-----|-----------|-------------|
    #
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #     SPI 11 bits address map:
    #
    #     -----+-----------+----------
    #     0x000|           |                                                                  
    #          |  CPU ROM  |   SPI                                                              
    #     0x0FF|           |   Code                                                          
    #     -----|-----------|   space
    #          |           |                                                             
    #          | Reserved  |                                                             
    #     0x3FF|           |                                                             
    #     -----|-----------|---------
    #     0x400|           |    
    #          |  CPU RAM  |   SPI                                                              
    #     0x4FF|           |   Data                                                          
    #     -----|-----------|   space
    #          |           |                                                             
    #          | Reserved  |                                                             
    #     0x7FF|           |                                                                 
    #     -----|-----------|---------
    #    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Write STOP intruction (0x7) in loc 0x00 of CPU space code
    # SPI command word: 0000000000000111 
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #SCK period #1:
    dut.ui_in.value = dut.ui_in.value.int &   MSK_SPI_CS_TO_OFF  &   MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value.int &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value.int |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)
    

