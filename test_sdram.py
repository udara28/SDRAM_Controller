from myhdl import *
from clk_driver import clk_driver
from sd_intf import SdramIntf
from sdram import sdram


def test_readwrite(clk, sd_intf):

    driver = sd_intf.get_driver()

    @instance
    def test():
        sd_intf.cke.next = 1
        yield sd_intf.nop(clk)
        yield delay(10000)
        yield sd_intf.load_mode(clk)
        yield sd_intf.nop(clk)
        yield sd_intf.activate(clk, 17)
        yield sd_intf.nop(clk)
        yield delay(10000)

        yield sd_intf.write(clk, driver, 20, 31)

        yield sd_intf.nop(clk)
        yield delay(100)
        yield sd_intf.read(clk, 20)

        yield sd_intf.nop(clk)
        yield delay(4)
        print "sd_intf dq = ", sd_intf.dq.val, " @ ", now()

    return test

clk = Signal(bool(0))

clk_driver_Inst = clk_driver(clk)
sd_intf_Inst = SdramIntf()
sdram_Inst = sdram(clk, sd_intf_Inst)
test_readWrite_Inst = test_readwrite(clk, sd_intf_Inst)

sim = Simulation(clk_driver_Inst, sdram_Inst, test_readWrite_Inst)
sim.run(25000)
