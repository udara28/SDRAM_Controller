from myhdl import *
from Clk import clkDriver
from sd_intf import sd_intf
from sdram import sdram

def test_rw(sd):

    # get the data driver for tristate signal
    data_driver = sd.dq.driver()

    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1
    yield delay(120)
    # [ACTIVE] cs ras cas we : L L H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,0,1,1
    sd.cke.next = 1
    yield delay(10)

    # [PRECHARGE] cs ras cas we : L L H L
#    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,0,1,0
#    yield delay(10)

    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1
    yield delay(20)
    # [WRITE] # cs ras cas we dqm : L H L L X
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,0,0
    sd.addr.next     = 20
    data_driver.next = 34 
    yield delay(10)
    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1
    data_driver.next = None
    yield delay(20)

    # [READ] # cs ras cas we dqm : L H L H X
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,0,1
    sd.addr.next     = 20
    yield delay(10)
    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1
#    yield delay(10)

    for i in range(10):
        print " BUS : [DQ @ ",now(),"] : ",sd.dq.val
        yield delay(5)

clk = Signal(bool(0))

clkDriver_Inst  = clkDriver(clk)
sd_intf_Inst    = sd_intf(clk)
sdram_Inst      = sdram(sd_intf_Inst)
test_rw_Inst    = test_rw(sd_intf_Inst)

sim = Simulation(clkDriver_Inst,sdram_Inst,test_rw_Inst)
sim.run(250)
