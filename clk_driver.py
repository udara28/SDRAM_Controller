from myhdl import *


def clk_driver(clk):

    half_period = delay(1)

    @always(half_period)
    def drive_clk():
        clk.next = not clk

    return drive_clk
