# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
#from cocotb.types import LogicArray, Logic

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
    MSK_OUT_CTRL_TO_0 = 0xF8
    MSK_OUT_CTRL_TO_4 = 0x04

    #Master SPI initial values:  
    dut.ui_in.value  = MSK_SPI_SCK_TO_ON | MSK_SPI_CS_TO_ON | MSK_SPI_MOSI_TO_ON
    await ClockCycles(dut.clk, 16)

    #SCK period #1:
    dut.ui_in.value = dut.ui_in.value.integer &   MSK_SPI_CS_TO_OFF  &   MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value.integer &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value.integer |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)
    
